#import the libraries
import xlsxwriter     #pip install openpyxl xlsxwriter xlrd
import pandas as pd   #pip install pandas
from pandas.io.json import json_normalize
import requests
import json


#Enter org_id
org_id = "3027"

#Token
token = "ee93272f8f8e718d9e7ad027f2f13e0eb345c938709d9ac759821b152ee709cc"


# Highbond API base URL
basepath = 'https://apis.highbond.com'   

# Filename of the Excel file to create. This creates and open the workbook for future tasks.
filename = 'resources.xlsx'

# Filename of the Text file to create. This is to create a list of ids.
text_file_ids = 'lists.txt'

# Create an pandas excel writer based on xlsxwriter.
writer = pd.ExcelWriter(filename, engine='xlsxwriter')



# Helper function to handle pagination and grab all objects rather than just one page of objects
def highbond_api_get_all(url):
    response = requests.get(basepath + url, headers = { 'Authorization':'Bearer ' + token, 'Content-Type': 'application/vnd.api+json', 'Accept-Encoding' : "" })
    response_json = response.json() # Convert to json response.
    list_of_result_dicts = response_json["data"]
    while response.status_code == 200:
        if response_json['links']['next'] and len(response_json['links']['next']) > 0:
            url = response_json['links']['next']
            response = requests.get(basepath + url, headers = { 'Authorization':'Bearer ' + token, 'Content-Type': 'application/vnd.api+json', 'Accept-Encoding' : "" })
            response_json = response.json() # Convert to json response.
            list_of_result_dicts.extend(response_json["data"])
        else:
            break
    return list_of_result_dicts



# Define resource type
resource_type = "frameworks"

# Get the relevant item from the resources list
endpoint = "/v1/orgs/"+ org_id + "/" + resource_type    # Create URL iterating through list of resources.
frameworks_list = highbond_api_get_all(endpoint)
frameworks_df = pd.json_normalize(frameworks_list)   # Normalize the json dict using "data" as the key.
frameworks_df.to_excel(writer, sheet_name = resource_type, index=False) # Write dataframe to Excel.
frameworks_ids = frameworks_df['id'].to_list() # select a column as series and then convert it into a column.
print(frameworks_df.head(1))
print(f"{resource_type} ids: ", frameworks_ids)



# Define resource type
resource_type = "projects" 

# Get the relevant item from the resources list
endpoint = "/v1/orgs/"+ org_id + "/" + resource_type    # Create URL iterating through list of resources.
projects_list = highbond_api_get_all(endpoint)
projects_df = pd.json_normalize(projects_list)   # Normalize the json dict using "data" as the key.
projects_df.to_excel(writer, sheet_name = resource_type, index=False) # Write dataframe to Excel.
projects_ids = projects_df['id'].to_list() # select a column as series and then convert it into a column.
print(projects_df.head(1))
print(f"{resource_type} ids: ", projects_ids)



# Define resource type
resource_type = "project_types" 

# Get the relevant item from the resources list
endpoint = "/v1/orgs/"+ org_id + "/" + resource_type    # Create URL iterating through list of resources.
project_types_list = highbond_api_get_all(endpoint)
project_types_df = pd.json_normalize(project_types_list)   # Normalize the json dict using "data" as the key.
project_types_df.to_excel(writer, sheet_name = resource_type, index=False) # Write dataframe to Excel.
project_types_ids = project_types_df['id'].to_list() # select a column as series and then convert it into a column.
print(project_types_df.head(1))
print(f"{resource_type} ids: ", project_types_ids)



# Define resource type
resource_type = "entities" 

# Get the relevant item from the resources list
endpoint = "/v1/orgs/"+ org_id + "/" + resource_type    # Create URL iterating through list of resources.
entities_list = highbond_api_get_all(endpoint)
entities_df = pd.json_normalize(entities_list)   # Normalize the json dict using "data" as the key.
entities_df.to_excel(writer, sheet_name = resource_type, index=False) # Write dataframe to Excel.
entities_ids = entities_df['id'].to_list() # select a column as series and then convert it into a column.
print(entities_df.head(1))
print(f"{resource_type} ids: ", entities_ids)



# Define resource type
resource_type = "entity_categories" 

# Get the relevant item from the resources list
endpoint = "/v1/orgs/"+ org_id + "/" + resource_type    # Create URL iterating through list of resources.
entity_categories_list = highbond_api_get_all(endpoint)
entity_categories_df = pd.json_normalize(entity_categories_list)   # Normalize the json dict using "data" as the key.
entity_categories_df.to_excel(writer, sheet_name = resource_type, index=False) # Write dataframe to Excel.
entity_categories_ids = entity_categories_df['id'].to_list() # select a column as series and then convert it into a column.
print(entity_categories_df.head(1))
print(f"{resource_type} ids: ", entity_categories_ids)



# Define resource type
resource_type = "custom_attributes"

# Initialize a blank list for holding the list of dataframes.
custom_attributes_list = []

# For each objective in the objective list, grab the risks
for i in project_types_ids:
    endpoint = "/v1/orgs/"+ org_id + "/project_types/" + i + "/" + resource_type   # Create URL iterating through list of resources.
    current_custom_attributes_list = highbond_api_get_all(endpoint)
    custom_attributes_list += current_custom_attributes_list

custom_attributes_df = pd.json_normalize(custom_attributes_list)
custom_attributes_df.to_excel(writer, sheet_name = resource_type, index=False)   # Write dataframe to Excel.
custom_attributes_ids = custom_attributes_df['id'].to_list()  # Creates list of all Analyses IDs.
print(custom_attributes_df.head(1))
print(f"{resource_type} ids: ", custom_attributes_ids)



# Define resource type
resource_type = "projects_objectives"

# Initialize a blank list for holding the list of dataframes.
projects_objectives_list = []

# Loop through all analyses, and converting the objectives lists into their own dataframes.
for i in projects_ids:
    endpoint = "/v1/orgs/"+ org_id + "/projects/" + i + "/objectives"   # Create URL iterating through list of resources.
    current_projects_objectives_list = highbond_api_get_all(endpoint)
    projects_objectives_list += current_projects_objectives_list

projects_objectives_df = pd.json_normalize(projects_objectives_list)
projects_objectives_df.to_excel(writer, sheet_name = resource_type, index=False)   # Write dataframe to Excel.
projects_objectives_ids = projects_objectives_df['id'].to_list()  # Creates list of all Analyses IDs.
print(projects_objectives_df.head(1))
print(f"{resource_type} ids: ", projects_objectives_ids)



# Define resource type
resource_type = "frameworks_objectives"

# Initialize a blank list for holding the list of dataframes.
frameworks_objectives_list = []

# Loop through all analyses, and converting the objectives lists into their own dataframes.
for i in frameworks_ids:
    endpoint = "/v1/orgs/"+ org_id + "/frameworks/" + i + "/objectives"   # Create URL iterating through list of resources.
    current_frameworks_objectives_list = highbond_api_get_all(endpoint)
    frameworks_objectives_list += current_frameworks_objectives_list

frameworks_objectives_df = pd.json_normalize(frameworks_objectives_list)
frameworks_objectives_df.to_excel(writer, sheet_name = resource_type, index=False)   # Write dataframe to Excel.
frameworks_objectives_ids = frameworks_objectives_df['id'].to_list()  # Creates list of all Analyses IDs.
print(frameworks_objectives_df.head(1))
print(f"{resource_type} ids: ", frameworks_objectives_ids)




# Define resource type
resource_type = "projects_controls"

# Initialize a blank list for holding the list of dataframes.
projects_controls_list = []

# Loop through all analyses, and converting the objectives lists into their own dataframes.
for i in projects_objectives_ids:
    endpoint = "/v1/orgs/"+ org_id + "/objectives/" + i + "/controls"   # Create URL iterating through list of resources.
    current_projects_controls_list = highbond_api_get_all(endpoint)
    projects_controls_list += current_projects_controls_list

projects_controls_df = pd.json_normalize(projects_controls_list)
projects_controls_df.to_excel(writer, sheet_name = resource_type, index=False)   # Write dataframe to Excel.
projects_controls_ids = projects_controls_df['id'].to_list()  # Creates list of all Analyses IDs.
print(projects_controls_df.head(1))
print(f"{resource_type} ids: ", projects_controls_ids)



# Define resource type
resource_type = "frameworks_controls"

# Initialize a blank list for holding the list of dataframes.
frameworks_controls_list = []

# Loop through all analyses, and converting the objectives lists into their own dataframes.
for i in frameworks_objectives_ids:
    endpoint = "/v1/orgs/"+ org_id + "/objectives/" + i + "/controls"   # Create URL iterating through list of resources.
    current_frameworks_controls_list = highbond_api_get_all(endpoint)
    frameworks_controls_list += current_frameworks_controls_list

frameworks_controls_df = pd.json_normalize(frameworks_controls_list)
frameworks_controls_df.to_excel(writer, sheet_name = resource_type, index=False)   # Write dataframe to Excel.
frameworks_controls_ids = frameworks_controls_df['id'].to_list()  # Creates list of all Analyses IDs.
print(frameworks_controls_df.head(1))
print(f"{resource_type} ids: ", frameworks_controls_ids)



# Define resource type
resource_type = "projects_risks"

# Initialize a blank list for holding the list of dataframes.
projects_risks_list = []

# Loop through all analyses, and converting the objectives lists into their own dataframes.
for i in projects_objectives_ids:
    endpoint = "/v1/orgs/"+ org_id + "/objectives/" + i + "/risks"   # Create URL iterating through list of resources.
    current_projects_risks_list = highbond_api_get_all(endpoint)
    projects_risks_list += current_projects_risks_list

projects_risks_df = pd.json_normalize(projects_risks_list)
projects_risks_df.to_excel(writer, sheet_name = resource_type, index=False)   # Write dataframe to Excel.
projects_risks_ids = projects_risks_df['id'].to_list()  # Creates list of all Analyses IDs.
print(projects_risks_df.head(1))
print(f"{resource_type} ids: ", projects_risks_ids)



# Define resource type
resource_type = "frameworks_risks"

# Initialize a blank list for holding the list of dataframes.
frameworks_risks_list = []

# Loop through all analyses, and converting the objectives lists into their own dataframes.
for i in frameworks_objectives_ids:
    endpoint = "/v1/orgs/"+ org_id + "/objectives/" + i + "/controls"   # Create URL iterating through list of resources.
    current_frameworks_risks_list = highbond_api_get_all(endpoint)
    frameworks_risks_list += current_frameworks_risks_list

frameworks_risks_df = pd.json_normalize(frameworks_risks_list)
frameworks_risks_df.to_excel(writer, sheet_name = resource_type, index=False)   # Write dataframe to Excel.
frameworks_risks_ids = frameworks_risks_df['id'].to_list()  # Creates list of all Analyses IDs.
print(frameworks_risks_df.head(1))
print(f"{resource_type} ids: ", frameworks_risks_ids)




# Define resource type
resource_type = "results_files"

# Initialize a blank list for holding the list of dataframes.
results_files_list = []

# Loop through all analyses, and converting the objectives lists into their own dataframes.
for i in projects_ids:
    endpoint = "/v1/orgs/"+ org_id + "/projects/" + i + "/results_files"   # Create URL iterating through list of resources.
    current_results_files_list = highbond_api_get_all(endpoint)
    results_files_list += current_results_files_list

results_files_df = pd.json_normalize(results_files_list)
results_files_df.to_excel(writer, sheet_name = resource_type, index=False)   # Write dataframe to Excel.
results_files_ids = results_files_df['id'].to_list()  # Creates list of all Analyses IDs.
print(results_files_df.head(1))
print(f"{resource_type} ids: ", results_files_ids)



# Define resource type
resource_type = "collections"

# Get the relevant item from the resources list
endpoint = "/v1/orgs/"+ org_id + "/" + resource_type    # Create URL iterating through list of resources.
response = requests.get(basepath + endpoint, headers = { 'Authorization':'Bearer ' + token, 'Content-Type': 'application/vnd.api+json', 'Accept-Encoding' : "" })
response_json = response.json() # Convert to json response.
collections_list = response_json["data"]
collections_df = pd.json_normalize(collections_list)   # Normalize the json dict using "data" as the key.
collections_df.to_excel(writer, sheet_name = resource_type, index=False) # Write dataframe to Excel.
collections_ids = collections_df['id'].to_list() # select a column as series and then convert it into a column.
print(collections_df.head(1))
print(f"{resource_type} ids: ", collections_ids)




# Define resource type
resource_type = "analyses"

# Initialize a blank list for holding the list of dataframes.
analyses_list = []

# Loop through all analyses, and converting the objectives lists into their own dataframes.
for i in collections_ids:
    endpoint = "/v1/orgs/"+ org_id + "/collections/" + i + "/" + resource_type   # Create URL iterating through list of resources.
    response = requests.get(basepath + endpoint, headers = { 'Authorization':'Bearer ' + token, 'Content-Type': 'application/vnd.api+json', 'Accept-Encoding' : "" })
    response_json = response.json() # Convert to json response.
    analyses_list.extend(response_json["data"])

analyses_df = pd.json_normalize(analyses_list)
analyses_df.to_excel(writer, sheet_name = resource_type, index=False)   # Write dataframe to Excel.
analyses_ids = analyses_df['id'].to_list()  # Creates list of all Analyses IDs.
print(analyses_df.head(1))
print(f"{resource_type} ids: ", analyses_ids)



# Define resource type
resource_type = "tables"

# Initialize a blank list for holding the list of dataframes.
tables_list = []

# Loop through all analyses, and converting the objectives lists into their own dataframes.
for i in analyses_ids:
    endpoint = "/v1/orgs/"+ org_id + "/analyses/" + i + "/" + resource_type   # Create URL iterating through list of resources.
    response = requests.get(basepath + endpoint, headers = { 'Authorization':'Bearer ' + token, 'Content-Type': 'application/vnd.api+json', 'Accept-Encoding' : "" })
    response_json = response.json() # Convert to json response.
    tables_list.extend(response_json["data"])

tables_df = pd.json_normalize(tables_list)
tables_df.to_excel(writer, sheet_name = resource_type, index=False)   # Write dataframe to Excel.
tables_ids = tables_df['id'].to_list()  # Creates list of all Analyses IDs.
print(tables_df.head(1))
print(f"{resource_type} ids: ", tables_ids)



# Define resource type
resource_type = "questionnaires"

# Initialize a blank list for holding the list of dataframes.
questionnaires_list = []

# Loop through all analyses, and converting the objectives lists into their own dataframes.
for i in collections_ids:
    endpoint = "/v1/orgs/"+ org_id + "/collections/" + i + "/" + resource_type   # Create URL iterating through list of resources.
    response = requests.get(basepath + endpoint, headers = { 'Authorization':'Bearer ' + token, 'Content-Type': 'application/vnd.api+json', 'Accept-Encoding' : "" })
    response_json = response.json() # Convert to json response.
    questionnaires_list.extend(response_json["data"])

questionnaires_df = pd.json_normalize(questionnaires_list)
questionnaires_df.to_excel(writer, sheet_name = resource_type, index=False)   # Write dataframe to Excel.
questionnaires_ids = questionnaires_df['id'].to_list()  # Creates list of all Analyses IDs.
print(questionnaires_df.head(1))
print(f"{resource_type} ids: ", questionnaires_ids)



# Define resource type
resource_type = "robots"

# Get the relevant item from the resources list
endpoint = "/v1/orgs/"+ org_id + "/" + resource_type    # Create URL iterating through list of resources.
response = requests.get(basepath + endpoint, headers = { 'Authorization':'Bearer ' + token, 'Content-Type': 'application/vnd.api+json', 'Accept-Encoding' : "" })
response_json = response.json() # Convert to json response.
robots_list = response_json["data"]
robots_df = pd.json_normalize(robots_list)   # Normalize the json dict using "data" as the key.
robots_df.to_excel(writer, sheet_name = resource_type, index=False) # Write dataframe to Excel.
robots_ids = robots_df['id'].to_list() # select a column as series and then convert it into a column.
print(robots_df.head(1))
print(f"{resource_type} ids: ", robots_ids)



# Define resource type
resource_type = "robot_tasks"

# Initialize a blank list for holding the list of dataframes.
robot_tasks_list = []

# Loop through all analyses, and converting the objectives lists into their own dataframes.
for i in robots_ids:
    endpoint = "/v1/orgs/"+ org_id + "/robots/" + i + "/" + resource_type   # Create URL iterating through list of resources.
    response = requests.get(basepath + endpoint, headers = { 'Authorization':'Bearer ' + token, 'Content-Type': 'application/vnd.api+json', 'Accept-Encoding' : "" })
    response_json = response.json() # Convert to json response.
    try:
        robot_tasks_list.extend(response_json["data"])
    except:
        pass

robot_tasks_df = pd.json_normalize(robot_tasks_list)
robot_tasks_df.to_excel(writer, sheet_name = resource_type, index=False)   # Write dataframe to Excel.
robot_tasks_ids = robot_tasks_df['id'].to_list()  # Creates list of all Analyses IDs.
print(robot_tasks_df.head(1))
print(f"{resource_type} ids: ", robot_tasks_ids)



# Define resource type
resource_type = "robot tasks parameters values"

# Initialize a blank list for holding the list of dataframes.
robot_tasks_values_list = []

# Loop through all analyses, and converting the objectives lists into their own dataframes.
for i in robot_tasks_ids:
    endpoint = "/v1/orgs/"+ org_id + "/robot_tasks/" + i + "/values"   # Create URL iterating through list of resources.
    response = requests.get(basepath + endpoint, headers = { 'Authorization':'Bearer ' + token, 'Content-Type': 'application/vnd.api+json', 'Accept-Encoding' : "" })
    response_json = response.json() # Convert to json response.
    try:
        robot_tasks_values_list.extend(response_json["data"])
    except:
        pass

robot_tasks_values_df = pd.json_normalize(robot_tasks_values_list)
robot_tasks_values_df.to_excel(writer, sheet_name = resource_type, index=False)   # Write dataframe to Excel.
robot_tasks_values_ids = robot_tasks_values_df['id'].to_list()  # Creates list of all Analyses IDs.
print(robot_tasks_values_df.head(1))
print(f"{resource_type} ids: ", robot_tasks_values_ids)



# Define resource type
resource_type = "robot tasks schedules"

# Initialize a blank list for holding the list of dataframes.
robot_tasks_schedules_list = []

# Loop through all analyses, and converting the objectives lists into their own dataframes.
for i in robot_tasks_ids:
    endpoint = "/v1/orgs/"+ org_id + "/robot_tasks/" + i + "/schedule"   # Create URL iterating through list of resources.
    response = requests.get(basepath + endpoint, headers = { 'Authorization':'Bearer ' + token, 'Content-Type': 'application/vnd.api+json', 'Accept-Encoding' : "" })
    response_json = response.json() # Convert to json response.
    try:
        robot_tasks_schedules_list.append(response_json["data"])
    except:
        pass

robot_tasks_schedules_df = pd.json_normalize(robot_tasks_schedules_list)
robot_tasks_schedules_df.to_excel(writer, sheet_name = resource_type, index=False)   # Write dataframe to Excel.
robot_tasks_schedules_ids = robot_tasks_schedules_df['id'].to_list()  # Creates list of all Analyses IDs.
print(robot_tasks_schedules_df.head(1))
print(f"{resource_type} ids: ", robot_tasks_schedules_ids)



# Define resource type
resource_type = "robot script versions (apps)"

# Initialize a blank list for holding the list of dataframes.
robot_apps_list = []

# Loop through all analyses, and converting the objectives lists into their own dataframes.
for i in robots_ids:
    endpoint = "/v1/orgs/"+ org_id + "/robots/" + i + "/robot_apps"   # Create URL iterating through list of resources.
    response = requests.get(basepath + endpoint, headers = { 'Authorization':'Bearer ' + token, 'Content-Type': 'application/vnd.api+json', 'Accept-Encoding' : "" })
    response_json = response.json() # Convert to json response.
    try:
        robot_apps_list.extend(response_json["data"])
    except:
        pass

robot_apps_df = pd.json_normalize(robot_apps_list)
robot_apps_df.to_excel(writer, sheet_name = resource_type, index=False)   # Write dataframe to Excel.
robot_apps_ids = robot_apps_df['id'].to_list()  # Creates list of all Analyses IDs.
print(robot_apps_df.head(1))
print(f"{resource_type} ids: ", robot_apps_ids)



# Define resource type
resource_type = "robot script activations"

# Initialize a blank list for holding the list of dataframes.
robot_script_activations_list = []

# Loop through all analyses, and converting the objectives lists into their own dataframes.
for i in robots_ids:
    endpoint = "/v1/orgs/"+ org_id + "/robots/" + i + "/robot_activations"   # Create URL iterating through list of resources.
    response = requests.get(basepath + endpoint, headers = { 'Authorization':'Bearer ' + token, 'Content-Type': 'application/vnd.api+json', 'Accept-Encoding' : "" })
    response_json = response.json() # Convert to json response.
    try:
        robot_script_activations_list.extend(response_json["data"])
    except:
        pass

robot_script_activations_df = pd.json_normalize(robot_script_activations_list)
robot_script_activations_df.to_excel(writer, sheet_name = resource_type, index=False)   # Write dataframe to Excel.
robot_script_activations_ids = robot_script_activations_df['id'].to_list()  # Creates list of all Analyses IDs.
print(robot_script_activations_df.head(1))
print(f"{resource_type} ids: ", robot_script_activations_ids)



# Define resource type
resource_type = "robot files"

# Initialize a blank list for holding the list of dataframes.
robot_files_list = []

# Loop through all analyses, and converting the objectives lists into their own dataframes.
for i in robots_ids:
    endpoint = "/v1/orgs/"+ org_id + "/robots/" + i + "/robot_files"   # Create URL iterating through list of resources.
    response = requests.get(basepath + endpoint, headers = { 'Authorization':'Bearer ' + token, 'Content-Type': 'application/vnd.api+json', 'Accept-Encoding' : "" })
    response_json = response.json() # Convert to json response.
    try:
        robot_files_list.extend(response_json["data"])
    except:
        pass

robot_files_ids = []
robot_files_df = pd.json_normalize(robot_files_list)
robot_files_df.to_excel(writer, sheet_name = resource_type, index=False)   # Write dataframe to Excel.
#robot_files_ids = robot_files_df['id'].to_list()  # Creates list of all Analyses IDs.
#print(robot_files_df.head(1))
#print(f"{resource_type} ids: ", robot_files_ids)



# saves and closes workbook
writer.save() 



joined_frameworks_ids               = ",".join(frameworks_ids)
joined_projects_ids                 = ",".join(projects_ids)
joined_project_types_ids            = ",".join(project_types_ids)
joined_entities_ids                 = ",".join(entities_ids)
joined_entity_categories_ids        = ",".join(entity_categories_ids)
joined_custom_attributes_ids        = ",".join(custom_attributes_ids)
joined_projects_objectives_ids      = ",".join(projects_objectives_ids)
joined_frameworks_objectives_ids    = ",".join(frameworks_objectives_ids)
joined_projects_controls_ids        = ",".join(projects_controls_ids)
joined_frameworks_controls_ids      = ",".join(frameworks_controls_ids)
joined_projects_risks_ids           = ",".join(projects_risks_ids)
joined_frameworks_risks_ids         = ",".join(frameworks_risks_ids)
joined_results_files_ids            = ",".join(results_files_ids)
joined_collections_ids              = ",".join(collections_ids)
joined_analyses_ids                 = ",".join(analyses_ids)
joined_tables_ids                   = ",".join(tables_ids)
joined_questionnaires_ids           = ",".join(questionnaires_ids)
joined_robots_ids                   = ",".join(robots_ids)
joined_robot_tasks_ids              = ",".join(robot_tasks_ids)
joined_robot_tasks_values_ids       = ",".join(robot_tasks_values_ids)
joined_robot_tasks_schedules_ids    = ",".join(robot_tasks_schedules_ids)
joined_robot_apps_ids               = ",".join(robot_apps_ids)
joined_robot_script_activations_ids = ",".join(robot_script_activations_ids)
joined_robot_files_ids              = ",".join(robot_files_ids)
joined_storyboards_ids_manual       = ",".join(['5371','6117','15474','11145','10307','8380','5381','5602','5599','5380','1484','1131','1061'])
joined_metrics_ids_manual           = ",".join(['264','6801','12850','2613','14928','7545','7569','6189','6194','5971','5972','5975','5978','1880'])


with open(text_file_ids,"wt") as lists_file:
    lists_file.write("framework ids: \n")
    lists_file.writelines(joined_frameworks_ids)
    lists_file.write("\n\nproject ids: \n")
    lists_file.writelines(joined_projects_ids)
    lists_file.write("\n\nproject type ids: \n")
    lists_file.writelines(joined_project_types_ids)
    lists_file.write("\n\nentity ids: \n")
    lists_file.writelines(joined_entities_ids)
    lists_file.write("\n\nentity category ids: \n")
    lists_file.writelines(joined_entity_categories_ids)
    lists_file.write("\n\ncustom attributes ids: \n")
    lists_file.writelines(joined_custom_attributes_ids)
    lists_file.write("\n\nproject objective ids: \n")
    lists_file.writelines(joined_projects_objectives_ids)
    lists_file.write("\n\nframework objective ids: \n")
    lists_file.writelines(joined_frameworks_objectives_ids)
    lists_file.write("\n\nproject control ids: \n")
    lists_file.writelines(joined_projects_controls_ids)
    lists_file.write("\n\nframework control ids: \n")
    lists_file.writelines(joined_frameworks_controls_ids)
    lists_file.write("\n\nproject risk ids: \n")
    lists_file.writelines(joined_projects_risks_ids)
    lists_file.write("\n\nframework risk ids: \n")
    lists_file.writelines(joined_frameworks_risks_ids)
    lists_file.write("\n\nresults files ids: \n")
    lists_file.writelines(joined_results_files_ids)
    lists_file.write("\n\ncollection ids: \n")
    lists_file.writelines(joined_collections_ids)
    lists_file.write("\n\nanalysis ids: \n")
    lists_file.writelines(joined_analyses_ids)
    lists_file.write("\n\ntable ids: \n")
    lists_file.writelines(joined_tables_ids)
    lists_file.write("\n\nquestionnaire ids: \n")
    lists_file.writelines(joined_questionnaires_ids)
    lists_file.write("\n\nrobot ids: \n")
    lists_file.writelines(joined_robots_ids)
    lists_file.write("\n\nrobot task ids: \n")
    lists_file.writelines(joined_robot_tasks_ids)
    lists_file.write("\n\nrobot task value ids: \n")
    lists_file.writelines(joined_robot_tasks_values_ids)
    lists_file.write("\n\nrobot task schedule ids: \n")
    lists_file.writelines(joined_robot_tasks_schedules_ids)
    lists_file.write("\n\nrobot script versions (apps) ids: \n")
    lists_file.writelines(joined_robot_apps_ids)
    lists_file.write("\n\nrobot script activation ids: \n")
    lists_file.writelines(joined_robot_script_activations_ids)
    lists_file.write("\n\nrobot file ids: \n")
    lists_file.writelines(joined_robot_files_ids)
    lists_file.write("\n\nstoryboard ids (manual): \n")
    lists_file.writelines(joined_storyboards_ids_manual)
    lists_file.write("\n\nmetric ids (manual): \n")
    lists_file.writelines(joined_metrics_ids_manual)

print("Finished Successfully!")