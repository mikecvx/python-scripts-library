# Importing the required libraries
import pandas
import json
import numpy as np

# Change default settings to display all rows and full cell content instead of shortened data in a Pandas dataframeú
# pandas.set_option('display.max_colwidth', None)
# pandas.set_option('display.max_rows', None)
pandas.set_option('display.max_columns', None)



# Setting the org variables
v_hb_org_id = '27993'
v_hb_project_type_id = ['34291','34297'] # v_hb_project_type_id = [] -> if you don't want to filter by project type id
v_hb_project_statuses = ['proposed','draft','active']
v_hb_published_only = False


# Setting the issue severity and score options
v_hb_issue_severity_1 = "High"
v_hb_issue_score_1 = 10
v_hb_issue_severity_2 = "Medium"
v_hb_issue_score_2 = 7
v_hb_issue_severity_3 = "Low"
v_hb_issue_score_3 = 3

# Setting the project rating options
v_hb_project_rating_1 = "Excellent"
v_hb_project_rating_1_score = 1
v_hb_project_rating_2 = "Good"
v_hb_project_rating_2_score = 26
v_hb_project_rating_3 = "Satisfactory"
v_hb_project_rating_3_score = 50




# Function to grab Highbond resources
def highbond_api_get_all(url):
    response = hcl.api_get(url)
    response_json = response.json()
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
# Grab projects list 
# Conditions check for projects: PROJECT TYPE and PROJECT STATUS
projects_list = highbond_api_get_all("/projects/")
if not v_hb_project_statuses:
    projects_list_filtered = [project for project in projects_list if project['relationships']['project_type']['data']['id'] in v_hb_project_type_id and project['attributes']['status'] in v_hb_project_statuses]
else:
    projects_list_filtered = [project for project in projects_list if project['attributes']['status'] in v_hb_project_statuses]
projects_list_filtered


##############################################################################################################
# Grab each open project and their published issues then calculate and update the projects conclusion
# Conditions check for issues: PUBLISHED STATUS
try:
    projects_list_filtered[0]
    for project in projects_list_filtered:
        issue_list = highbond_api_get_all("/projects/" + project['id'] + "/issues")
        if v_hb_published_only:
            issue_list_filtered = [issue for issue in issue_list if issue['attributes']['published'] is True]
        else:
            issue_list_filtered = issue_list
        #print("---------------------------------")
        #print("Old: ", project['attributes']['opinion'])
        if issue_list_filtered:
            issue_df = pandas.json_normalize(issue_list_filtered)
            conditions = [issue_df['attributes.severity'] == v_hb_issue_severity_1, issue_df['attributes.severity'] == v_hb_issue_severity_2, issue_df['attributes.severity'] == v_hb_issue_severity_3]
            choices = [v_hb_issue_score_1, v_hb_issue_score_2, v_hb_issue_score_3]
            issue_df['conclusion_score'] = np.select(conditions, choices, default = 0)
            v_hb_project_issue_report_score = issue_df['conclusion_score'].sum()
            v_hb_project_issue_report_rating = v_hb_project_rating_3 if v_hb_project_issue_report_score >= v_hb_project_rating_3_score else v_hb_project_rating_2 if v_hb_project_issue_report_score >= v_hb_project_rating_2_score else v_hb_project_rating_1 if v_hb_project_issue_report_score >= v_hb_project_rating_1_score else v_hb_project_rating_1
            
            # Update the project conclusion
            original_project_response = hcl.hb_api.get("/projects/" + project['id'])
            original_project_dict = original_project_response.json()
            original_project_dict['data']['attributes']['opinion'] = v_hb_project_issue_report_rating
            #print(project['id'], ":", v_hb_project_issue_report_score, "->", v_hb_project_issue_report_rating)
            #print("New: ", project['attributes']['opinion'])
            #print("*************************************")

            v_hb_project_conclusion_update_response = hcl.hb_api.patch("/projects/" + project['id'], data=original_project_dict)
            print("Successfully updated project: ", project['id'])

        else:
            continue

except IndexError:
    print("No project met the criteria for update")


print("\nSCRIPT SUCCESSFULLY RAN\n")