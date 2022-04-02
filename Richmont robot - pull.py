#import the libraries
import pandas as pd   #pip install pandas
import numpy as np
from pandas.io.json import json_normalize
import json



# FUNCTIONS

# Convert the user inputted project ids to a list and trim them
def convert_to_list(project_ids):
	project_ids_list = list(project_ids.split(","))
	return project_ids_list


# Helper function to handle pagination and grab all objects rather than just one page of objects
def highbond_api_get_all_nopagination(url):
    response = hcl.api_get(url)
    response_json = response.json()
    list_of_result_dicts = response_json["data"]
    return list_of_result_dicts


# Helper function to handle pagination and grab all objects rather than just one page of objects
def highbond_api_get_all_pagination(url):
    response = hcl.api_get(url)
    response_json = response.json()
    list_of_result_dicts = response_json["data"]
    while response.status_code == 200:
        if response_json['links']['next'] and len(response_json['links']['next']) > 0:
            url = response_json['links']['next']
            response = hcl.api_get(url)
            response_json = response.json()
            list_of_result_dicts.append(response_json["data"])
        else:
            break
    return list_of_result_dicts


# This function converts the custom attributes column into a dictionary and flatten them
def flatten_custom_attributes(custom_attribute_field_value):
    custom_attribute_dict = {} # Initialize empty dictionary
    for attribute in custom_attribute_field_value:           # There can be multiple custom attributes, so we need to loop through each one to parse it
        if isinstance(attribute["value"], list) and len(attribute["value"]) == 1:   # If the custom attribute value is a list itself and only having one value, "de-listify it"
            attribute["value"] = attribute["value"][0] # De listifies the value list
        custom_attribute_dict[attribute["term"]] = attribute["value"] # Create the dictionary tuple with the custom attribute term and value
    return custom_attribute_dict # Return the completed dictionary
	
	
	
	
	
#Enter org_id
org_id = "32208"

v_project_ids = hcl.variable["v_project_ids"].strip()   # The Project IDs
v_results_table_id = hcl.variable["v_results_table_id"].strip()   # The Results Table ID

project_ids_list_temp = convert_to_list(v_project_ids)
project_ids_list = [i.strip() for i in project_ids_list_temp]


# Grab selected projects based on user input
projects_list = []
project_fields = "name"

# Loop through all analyses, and converting the objectives lists into their own dataframes.
for project in project_ids_list:
    current_projects_list = highbond_api_get_all_nopagination("/projects/" + project + "?fields[projects]=" + project_fields)
    projects_list.append(current_projects_list)

projects_df = pd.json_normalize(projects_list)
projects_df["project_id"] = projects_df["id"] #rename the id field
del projects_df["id"] #removing the original the id field
projects_df



# Grab the objectives of the selected projects
objectives_list = []
objective_fields = "title,reference,project"

# Loop through all analyses, and converting the objectives lists into their own dataframes.
for project in projects_list:
    current_objectives_list = highbond_api_get_all_pagination("/projects/" + project["id"] + "/objectives?fields[objectives]=" + objective_fields)
    objectives_list.extend(current_objectives_list)

objectives_df = pd.json_normalize(objectives_list)
objectives_df["objective_id"] = objectives_df["id"] #rename the id field
del objectives_df["id"] #removing the original the id field
objectives_df




# Grab the controls of the selected projects
controls_list = []
control_fields = "description,control_id,owner,frequency,control_type,prevent_detect,method,status,custom_attributes,objective,walkthrough"

# Loop through all analyses, and converting the objectives lists into their own dataframes.
for objective in objectives_list:
    current_controls_list = highbond_api_get_all_pagination("/objectives/" + objective["id"] + "/controls?fields[controls]="+control_fields)
    controls_list.extend(current_controls_list)

controls_df = pd.json_normalize(controls_list)
controls_df["control_id"] = controls_df["id"] #rename the id field
del controls_df["id"] #removing the original the id field

# If custom attributes exist, then convert them to columns in the dataframe
if "attributes.custom_attributes" in controls_df.columns: 
    custom_attribute_df = pd.json_normalize(controls_df["attributes.custom_attributes"].apply(flatten_custom_attributes)) # Convert the custom attributes into a dataframe using the above function
    controls_df = controls_df.join(custom_attribute_df) # Join the custom attribute dataframe to our controls dataframe

controls_df





# Grab the walkthroughs of the selected controls
walkthrough_list = []

# Loop through all analyses, and converting the objectives lists into their own dataframes.
for control in controls_list:
    current_walkthrough_list = highbond_api_get_all_nopagination("/walkthroughs/" + control["relationships"]["walkthrough"]["data"]["id"])
    walkthrough_list.append(current_walkthrough_list)

walkthrough_df = pd.json_normalize(walkthrough_list)
walkthrough_df["walkthrough_id"] = walkthrough_df["id"] #rename the id field
del walkthrough_df["id"] #removing the original the id field
walkthrough_df






#Joining the tables to create one result table with all the walkthrough/control/objective/project information
wt_ctrl_df = pd.merge(walkthrough_df, controls_df, left_on='relationships.control.data.id',right_on='control_id', how='inner')
wt_ctrl_obj_df = pd.merge(wt_ctrl_df, objectives_df, left_on='relationships.objective.data.id',right_on='objective_id', how='inner')
wt_ctrl_obj_prj_df = pd.merge(wt_ctrl_obj_df, projects_df, left_on='relationships.project.data.id',right_on='project_id', how='inner')
wt_ctrl_obj_prj_df





# Final clean up of fields
# Renaming and removing fields
wt_ctrl_obj_prj_df['test_of_design_result'] = np.select([
(wt_ctrl_obj_prj_df["attributes.control_design"] == True),
(wt_ctrl_obj_prj_df["attributes.control_design"] == False)
],
["Designed Appropriately","Design Failure"],
default=["Not Tested"])

wt_ctrl_obj_prj_df["control_reference"] = wt_ctrl_obj_prj_df["attributes.control_id"]
wt_ctrl_obj_prj_df["objective_title"] = wt_ctrl_obj_prj_df["attributes.title"]
wt_ctrl_obj_prj_df["objective_reference"] = wt_ctrl_obj_prj_df["attributes.reference"]
wt_ctrl_obj_prj_df["project_name"] = wt_ctrl_obj_prj_df["attributes.name"]
wt_ctrl_obj_prj_df["project_link"] = wt_ctrl_obj_prj_df["links.ui_y"]
wt_ctrl_obj_prj_df["control_link"] = "https://richemont-international-sa.projects-eu.highbond.com/audits/" + wt_ctrl_obj_prj_df["project_id"] + "/objectives/" + wt_ctrl_obj_prj_df["objective_id"] + "/controls/" + wt_ctrl_obj_prj_df["control_id"]
wt_ctrl_obj_prj_df["test_of_design_link"] = "https://richemont-international-sa.projects-eu.highbond.com/audits/" + wt_ctrl_obj_prj_df["project_id"] + "/objectives/" + wt_ctrl_obj_prj_df["objective_id"] + "/walkthroughs/" + wt_ctrl_obj_prj_df["walkthrough_id"]
wt_ctrl_obj_prj_df["unique_id"] = wt_ctrl_obj_prj_df["project_id"] + wt_ctrl_obj_prj_df["objective_id"] + wt_ctrl_obj_prj_df["control_id"]


# Remove column name prefix of "attributes"
del wt_ctrl_obj_prj_df["attributes.control_id"]
wt_ctrl_obj_prj_df.columns = wt_ctrl_obj_prj_df.columns.str.replace('^attributes.', '')
wt_ctrl_obj_prj_df.columns = wt_ctrl_obj_prj_df.columns.str.replace('_attributes.', '_')
# Clean up the titles of the columns
wt_ctrl_obj_prj_df.columns = map(str.title, wt_ctrl_obj_prj_df.columns)
wt_ctrl_obj_prj_df.columns = wt_ctrl_obj_prj_df.columns.str.replace('_',' ')
wt_ctrl_obj_prj_df.columns
# Remove useless columns (if they exist)
for column_name in wt_ctrl_obj_prj_df.columns:
    if column_name == "Custom Attributes":
        del wt_ctrl_obj_prj_df[column_name]
    if "Relationships." in column_name:
        del wt_ctrl_obj_prj_df[column_name]


# Select the fields to be exported
list_of_fields_final = ["Test Of Design Result", "Control Reference","Description","Owner","Frequency","Control Type","Prevent Detect","Method","Status","Ca Priority","Group Standard Ca Description","Control Owner Email","Control Link","Test Of Design Link","Objective Reference","Objective Title","Project Name","Project Link","Unique Id","Walkthrough Id","Control Id","Launch Tod Self Assessment"]
wt_ctrl_obj_prj_df = wt_ctrl_obj_prj_df[list_of_fields_final]

wt_ctrl_obj_prj_df





#Export into Results Table entered by user
controls_join_obj_proj_hcl_df = hcl.from_pandas(wt_ctrl_obj_prj_df)
controls_join_obj_proj_hcl_df.to_hb_results(v_results_table_id,overwrite = False)