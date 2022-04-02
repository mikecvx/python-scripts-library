# Takes the data from a results table and updates the corresponding risk/control with updated details
# Assumes that the results table has the risk and control ids already in it


# Grab the variables for which results table to publish to; set a default value if blank
if hcl.variable["results_table_id"].strip():
    results_table_id = hcl.variable["results_table_id"]
else:
    results_table_id = "11247"
    
# Status for approval in Results
approved_status = "ERM: Assessment Approved"
    
# Are we debugging?
debug = True

import pandas
import json
import math

#######################################################
# URL Endpoint as defined from https://docs-apis.highbond.com/public.html#operation/getRecords
# Note that we only need the part of the URL that is after the org_id -- everything else is handled by the hb_api module
request_endpoint = "/tables/" + results_table_id + "/records/" 

# Submit the request and grab the response, and convert it to JSON
# Note that the hb_api methods handle authentication and org_id
request_response = hcl.hb_api.get(request_endpoint)

# If the response isn't successful, raise it as an error. Probably because the API key is incorrect.
if request_response.status_code != 200:
  raise ConnectionError("Could not connect to HighBond ("+request_endpoint+"). Check the HighBond token value.")

# Grab the response as a JSON
request_json = request_response.json()

#######################################################

Results_Records_df = pandas.DataFrame(request_json["data"])        # Convert the response JSON to a dataframe -- we grab data from the "data" element
Results_Records_df.head()                                           # Show top 5 records

# Grab the columns metadata into a dataframe
Results_Columns_df = pandas.DataFrame(request_json["columns"])

# Create a dictionary from the display name and field name
Results_Column_Mapping_dict = pandas.Series(Results_Columns_df.display_name.values,index=Results_Columns_df.field_name).to_dict()
Results_Column_Mapping_Reverse_dict = pandas.Series(Results_Columns_df.field_name,index=Results_Columns_df.display_name.values).to_dict()

if debug:
    print(Results_Records_df.columns)

# Grab the records from the response and rename the columns
Results_Records_df = pandas.DataFrame(request_json["data"])  
Results_Records_df.rename(columns = Results_Column_Mapping_dict, inplace = True)
Results_Records_df = Results_Records_df.convert_dtypes()

if debug:
    print(Results_Records_df.columns)

# risk_update_record = Results_Records_df.iloc[[2]] for testing, grab just one record 

#######################################################

Results_Records_df

#######################################################

# Function to update the risk records - operates on every row
def update_risk_record(risk_update_record):
    
    risk_url = "/risks/"+risk_update_record["Id"] # Define the endpoint for getting and patching
    
    try:
        risk_response = hcl.hb_api.get(risk_url)  # Grab the current version of the risk from projects
    except:
        return "Unable to get risk id "+risk_update_record["Id"]
    risk_response_dict =  risk_response.json()  # Convert response to a dictionary
    
    print(risk_response_dict["data"])
    
    
    if isinstance(risk_update_record["Updated Impact"], str) and risk_update_record["Updated Impact"].strip(): #check to see if the updated impact is null and/or blank
        # updated_impact = risk_update_record["Updated Impact"].split("-", 1)[-1].strip()     # strip anything before the dash so that the results questionnaire values match the project type
        risk_response_dict["data"]["attributes"]["impact"] = risk_update_record["Updated Impact"]
    if isinstance(risk_update_record["Updated Likelihood"], str) and risk_update_record["Updated Likelihood"].strip():
        # updated_likelihood = risk_update_record["Updated Likelihood"].split("-", 1)[-1].strip()     # strip anything before the dash so that the results questionnaire values match the project type
        risk_response_dict["data"]["attributes"]["likelihood"] = risk_update_record["Updated Likelihood"]
    
    if isinstance(risk_update_record["Updated Title"], str) and risk_update_record["Updated Title"].strip():
        risk_response_dict["data"]["attributes"]["title"] = risk_update_record["Updated Title"] 
    
    if isinstance(risk_update_record["Updated Description"], str) and risk_update_record["Updated Description"].strip():
        risk_response_dict["data"]["attributes"]["description"] = risk_update_record["Updated Description"]  
        
    if isinstance(risk_update_record["Updated Cause"], str) and risk_update_record["Updated Cause"].strip():
        for custom_attribute in risk_response_dict["data"]["attributes"]["custom_attributes"]:
            if custom_attribute["term"] == "Risk Cause":
                custom_attribute["value"] = [risk_update_record["Updated Cause"]] 
    
    if(debug):
        print(risk_response_dict["data"])
    
    update_response = "" # Default response
    
    # If the risk update record is in the approved status, make the patch update to projects
    if risk_update_record["Status"] == approved_status:
        try:
            risk_response = hcl.hb_api.patch(risk_url, data=risk_response_dict)
        except:
            return "Unable to update risk"
        update_response = risk_response.text
    else:
        return ""
    
    return "Successfully Updated"
    
# Run the above function for every record in the results table

Results_Records_df["Update Risk Status"] = Results_Records_df.apply(update_risk_record, axis=1)

###################################################

# Function to update the control records - operates on every row
def update_control_record(control_update_record):


    control_url = "/controls/"+control_update_record["Control ID"] # Define the endpoint for getting and patching
    
    try:
        control_response = hcl.hb_api.get(control_url)  # Grab the current version of the control from projects
    except:
        return "Unable to get control id "+control_update_record["Control ID"]

    control_response_dict = control_response.json()  # Convert response to a dictionary

    print(control_response_dict["data"])

    #control_response_dict["data"]["attributes"]["impact"] = risk_update_record["Updated Impact"] # Update the impact with the impact from results
    #control_response_dict["data"]["attributes"]["likelihood"] = risk_update_record["Updated Likelihood"] # Update the impact with the likelihood from results
    
    if isinstance(control_update_record["Updated Mitigation/Controls Description"], str) and control_update_record["Updated Mitigation/Controls Description"].strip():
        control_response_dict["data"]["attributes"]["description"] = control_update_record["Updated Mitigation/Controls Description"]  
    
    if isinstance(control_update_record["Updated Residual Impact"], str) and control_update_record["Updated Residual Impact"].strip():
        for custom_attribute in control_response_dict["data"]["attributes"]["custom_attributes"]:
            if custom_attribute["term"] == "Residual Impact Ranking":
                custom_attribute["value"] = [control_update_record["Updated Residual Impact"]]
                
    if isinstance(control_update_record["Updated Residual Likelihood"], str) and control_update_record["Updated Residual Likelihood"].strip():
        for custom_attribute in control_response_dict["data"]["attributes"]["custom_attributes"]:
            if custom_attribute["term"] == "Residual Likelihood Ranking":
                custom_attribute["value"] = [control_update_record["Updated Residual Likelihood"]]    

    print(control_response_dict["data"])
    
    update_response = "" # Default response
    
    # If the risk update record is in the approved status, make the patch update to projects
    if control_update_record["Status"] == approved_status:
        try:
            control_response = hcl.hb_api.patch(control_url, data=control_response_dict)
        except:
            return "Unable to update control"
        update_response = control_response.text
    else:
        return ""

    return "Successfully Updated"
    
# Run the above function for every record in the results table

Results_Records_df["Update Control Status"] = Results_Records_df.apply(update_control_record, axis=1)

####################################################

# Let's see the result of our patching!
Results_Records_df 
Results_Records_hcl_df = hcl.from_pandas(Results_Records_df[["Id","Update Risk Status","Update Control Status"]])

Results_Records_hcl_df

################################################

Results_Records_hcl_df.to_hb_results(results_table_id)