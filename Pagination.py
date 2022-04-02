import pandas
import json
############################################################################################################## 
project_id = 1234
##############################################################################################################
# Helper function to handle pagination and grab all objects rather than just one page of objects
def highbond_api_get_all(url):
    response = hcl.api_get(url)
    response_json= response.json()
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
##############################################################################################################
# Grab Objective list of the project
objectives_list = highbond_api_get_all("/projects/" + project_id +"/objectives")
objectives_df = pandas.json_normalize(objectives_list) # Convert list list of objective dictionaries to a dataframe
objectives_df
##############################################################################################################
# Grab all risks in each objective 
risk_list = []
# for each objective in the objective list, grab the risks
for objective in objectives_list:
    current_risk_list = highbond_api_get_all("/objectives/" + objective["id"] +"/risks?include=objective") # Grab list of risks for the current objective
    risk_list = risk_list + current_risk_list
print(risk_list)
risks_df = pandas.json_normalize(risk_list) # First convert list list of risk dictionaries to a dataframe
risks_df






get project related data

# Grab Project list
project_list = highbond_api_get_projects(f"https://apis-eu.highbond.com/v1/orgs/{v_org_id}/projects/{v_project_id}")
print(project_list)
projects_df = pd.json_normalize(project_list)
print(projects_df)

# Grab Objective list
objective_list = highbond_api_get_all(f"https://apis-eu.highbond.com/v1/orgs/{v_org_id}/projects/{v_project_id}/objectives")
print(objective_list)
objectives_df = pd.json_normalize(objective_list)
print(objectives_df)

# Grab Control list
control_list = []
for objective in objective_list:
    current_control_List = highbond_api_get_all(f"https://apis-eu.highbond.com/v1/orgs/{v_org_id}/objectives/" + objective["id"]  + "/controls")
    control_list        += current_control_List
print(control_list)
controls_df = pd.json_normalize(control_list)
print(controls_df.head())


join tables

objective_control_df = pd.merge(objectives_df,controls_df,how="left",left_on="id",right_on="relationships.objective.data.id")
print(objective_control_df.head())

project_obj_ctrl_df = pd.merge(projects_df,objective_control_df,how="left",left_on="id",right_on="relationships.project.data.id")
print(project_obj_ctrl_df.head())



remove prefixes and all

# Remove column name prefix of "attributes"
project_obj_ctrl_df.columns = project_obj_ctrl_df.columns.str.replace('^attributes.', '')
project_obj_ctrl_df.columns = project_obj_ctrl_df.columns.str.replace('_attributes.', '_')
# Clean up the titles of the columns
project_obj_ctrl_df.columns = map(str.title, project_obj_ctrl_df.columns)
project_obj_ctrl_df.columns = project_obj_ctrl_df.columns.str.replace('_',' ')
# Remove useless columns (if they exist)
for column_name in project_obj_ctrl_df.columns:
    if column_name == "Custom Attributes":
        del project_obj_ctrl_df[column_name]
    if "Relationships." in column_name:
        del project_obj_ctrl_df[column_name]
project_obj_ctrl_df	