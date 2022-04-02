# I want to import all the risks within a project. To do so, I'll need to get all objectives in that project and loop through them and collect all the risks within each objective.


import pandas
import json
############################################################################################################## 

project_id = 1234

##############################################################################################################
# Helper function to handle pagination and grab all objects rather than just one page of objects
# UPDATED 2021-08-18 - Phil Lim -- added a check to make sure the next link is not the same as the current link to avoid infinite loops

# Helper function to handle pagination and grab all objects rather than just one page of objects
def highbond_api_get_all(url):
    response = hcl.api_get(url)
    response_json= response.json()
    list_of_result_dicts = response_json["data"]
    while response.status_code == 200:
        if response_json['links']['next'] and len(response_json['links']['next']) > 0 and url != response_json['links']['next']:
            url = response_json['links']['next']
            response = hcl.api_get(url)
            response_json = response.json()
            list_of_result_dicts.extend(response_json["data"])
            print(response_json)
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