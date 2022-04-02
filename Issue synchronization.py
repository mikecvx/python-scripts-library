import pandas
import json


##############################################################################################################
# Parameters

# Project containing issues -- only for initial load into Results -- not required for syncrhonization
project_id = "46623"

# Results table that contains the issues for synchronization
results_table_id = "395218"

# Statuses on the results side to consider issues closed
results_closed_statuses = ["Closed","03 - Closed","Closed (Approved)"]
results_table_issue_id_field_name = "id"

# Note -- you need to configure a password variable for v_hb_token and populate it with your HighBond API token





##############################################################################################################
# Helper function to handle pagination for the HighBond API and grab all objects rather than just one page of objects

def highbond_api_get_all(url):
    response = hcl.api_get(url)
    response_json= response.json()
    list_of_result_dicts = response_json["data"]
    while response.status_code == 200:
        if response_json['links']['next'] and len(response_json['links']['next']) > 0:
            url = response_json['links']['next']
            response = hcl.api_get(url)
            response_json = response.json()
            list_of_result_dicts.extend(response_json["data"])
        else:
            break
        
    return list_of_result_dicts



##############################################################################################################
# Grab issues {protocol}://{server}/v1/orgs/{org_id}/projects/{project_id}/issues

issues_list = highbond_api_get_all("/projects/" + project_id +"/issues")
issues_df = pandas.json_normalize(issues_list) # Convert list list of issue dictionaries to a dataframe
issues_df






#############################################################################################################
# Helper functions for cleaning up the dataframe from the Projects API


#############################################################################################################
# This function converts the custom attributes column into a dictionary 
def flatten_custom_attributes(custom_attribute_field_value):
    custom_attribute_dict = {} # Initialize empty dictionary
    for attribute in custom_attribute_field_value:           # There can be multiple custom attributes, so we need to loop through each one to parse it
        if isinstance(attribute["value"], list) and len(attribute["value"]) == 1:   # If the custom attribute value is a list itself and only having one value, "de-listify it"
            attribute["value"] = attribute["value"][0] # De listifies the value list
        custom_attribute_dict[attribute["term"]] = attribute["value"] # Create the dictionary tuple with the custom attribute term and value
    
    return custom_attribute_dict # Return the completed dictionary

#############################################################################################################
# This function prepares a dataframe from projects (flattens custom attributes, and renames and removes unnecessary columns) 

def prepare_projects_dataframe(projects_df):
    # If custom attributes exist, then convert them to columns in the dataframe
    if "attributes.custom_attributes" in projects_df.columns: 
        custom_attribute_df = pandas.json_normalize(projects_df["attributes.custom_attributes"].apply(flatten_custom_attributes)) # Convert the custom attributes into a dataframe using the above function
        projects_df = projects_df.join(custom_attribute_df) # Join the custom attribute dataframe to our risks dataframe
    
    # Remove column name prefix of "attributes"
    projects_df.columns = projects_df.columns.str.replace('^attributes.', '')
    
    # Remove useless columns (if they exist)
    if "custom_attributes" in projects_df.columns: 
        del projects_df["custom_attributes"]

    # Clean up the column names that are for the related objects 
    projects_df.columns = projects_df.columns.str.replace('^relationships.', '')
    projects_df.columns = projects_df.columns.str.replace('.data.', '_')

    return projects_df
    






#############################################################################################################
# Apply the helper function above to prepare the dataframe

P_issues_df = prepare_projects_dataframe(issues_df)

# Let's list the columns
print(P_issues_df.columns)

# Preview the prepared issues dataframe
P_issues_df




#############################################################################################################
# Export to results
# COMMENTED OUT AS IT IS EXPECTED THAT THE RESULTS TABLE ALREADY HAS THE ISSUE RECORDS IN IT

# issues_hcl_df = hcl.from_pandas(P_issues_df)
# issues_hcl_df.to_hb_results(results_table_id)




#############################################################################################
# get_from_hb_results(results_table_id, include_metadata=False, display_names=True)
# Grabs a table from results
# include_metadata = flag for whether or not to include metadata fields (e.g. priority, status, publisher, publish_date, etc.)
# display_names = flag for whether to convert the column names to their display names for easier readability

def get_from_hb_results(results_table_id, include_metadata=False, display_names=True):

    # URL Endpoint as defined from https://docs-apis.highbond.com/public.html#operation/getRecords
    # Note that we only need the part of the URL that is after the org_id -- everything else is handled by the hb_api module
    request_endpoint = "/tables/" + results_table_id + "/records/" 

    # Submit the request and grab the response, and convert it to JSON
    # Note that the hb_api methods handle authentication and org_id
    request_response = hcl.api_get(request_endpoint)

    # If the response isn't successful, raise it as an error. Probably because the API key is incorrect.
    if request_response.status_code != 200:
        raise ConnectionError("Could not connect to HighBond ("+request_endpoint+"). Check the HighBond token value: v_hb_token")

    # Grab the response as a JSON
    request_json = request_response.json()
    Results_Records_df = pandas.DataFrame(request_json["data"])        # Convert the response JSON to a dataframe -- we grab data from the "data" element

    print("Before: "+Results_Records_df.columns)    

    if not include_metadata:
        for column_name in Results_Records_df.columns:
            if column_name.startswith('metadata.') or column_name.startswith('extras.'): 
                del Results_Records_df[column_name]

    print("After: "+Results_Records_df.columns)    

    # Grab the columns metadata into a dataframe
    Results_Columns_df = pandas.DataFrame(request_json["columns"])

    # Create a dictionary from the display name and field name
    Results_Column_Mapping_dict = pandas.Series(Results_Columns_df.display_name.values,index=Results_Columns_df.field_name).to_dict()

    if display_names:
        # Grab the records from the response and rename the columns
        Results_Records_df.rename(columns = Results_Column_Mapping_dict, inplace = True)
        Results_Records_df = Results_Records_df.convert_dtypes()

    return Results_Records_df




#############################################################################################################
# Grab the table from Results and put it in a dataframe

P_results_issues_df = get_from_hb_results(results_table_id, include_metadata=True, display_names=False)

# Prepare some computed fields that convert the updated at/publish date columns to datetime
P_results_issues_df["c_updated_at"] = pandas.to_datetime(P_results_issues_df["metadata.updated_at"])
P_results_issues_df["c_published_at"] = pandas.to_datetime(P_results_issues_df["metadata.publish_date"])

P_results_issues_df




#############################################################################################################
# Function that operates on a single results record, grabs the issue ID, and synchronizes the status between projects and results

def update_issue_in_projects(issue_results_record):
   
    project_issue_status = "" # Default response status text
    
    # Define the issue's endpoint for getting and patching
    issue_url = "/issues/"+issue_results_record[results_table_issue_id_field_name]
    
    # First we get a the latest version of the issue from projects to make sure we don't overwrite anything
    try:
        api_response = hcl.hb_api.get(issue_url)  # Grab the current version of the risk from projects
    except:
        return "Unable to get issue id "+issue_results_record[results_table_issue_id_field_name]
    
    issue_response_dict =  api_response.json()  # Convert response to a dictionary
    
    #print(issue_response_dict["data"])
    
    # Grab the datetime that the issue in projects was last updated
    projects_issue_updated_at = pandas.to_datetime(issue_response_dict["data"]["attributes"]["updated_at"])
   
    # if the results record was updated later than the projects issue record
    # and the results record was updated after it was published
    if issue_results_record["c_updated_at"] >= projects_issue_updated_at  \
    and issue_results_record["c_updated_at"] > issue_results_record["c_published_at"]:
    
        if issue_results_record["metadata.status"] in results_closed_statuses:
            # Now set the closed status to be true -- we won't update re-opening of issues
            issue_response_dict["data"]["attributes"]["closed"] = True
        else:
            issue_response_dict["data"]["attributes"]["closed"] = False
            
        # try and apply the update to the issue record in projects
        try:
            patch_api_response = hcl.hb_api.patch(issue_url, data=issue_response_dict)
            project_issue_status = str(issue_response_dict["data"]["attributes"]["closed"])
        except Exception as e:
            project_issue_status = "Unable to patch issue id "+issue_results_record[results_table_issue_id_field_name]+" Error: "+str(e)
    else:
        project_issue_status = str(issue_response_dict["data"]["attributes"]["closed"])
    
    return project_issue_status





#############################################################################################################
# Apply the function to synchronize issues on every single results record. 

P_results_issues_df["Projects Issue Status"] = P_results_issues_df.apply(update_issue_in_projects, axis=1)
P_results_issues_df




#############################################################################################################
# Export updated table to results 

P_Export_To_Results_df = P_results_issues_df[[results_table_issue_id_field_name,"Projects Issue Status"]]
P_Export_To_Results_hcl_df = hcl.from_pandas(P_Export_To_Results_df)
P_Export_To_Results_hcl_df.to_hb_results(results_table_id,overwrite=False)