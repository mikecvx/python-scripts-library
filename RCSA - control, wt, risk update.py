# Import libraries
import pandas
import json


# Hard coded variables
v_control_questionnaire_label_descr = "Observations"
v_control_questionnaire_label_concl = "Performance"

v_rejected_status_label_input       = "Rejected"

v_subdomain                         = "tr"
v_region                            = "us"

# User input parameters through tasks
v_results_table_id                  = hcl.variable["v_results_table_id"].strip() # The Results Table ID
v_object_type_input                 = hcl.variable["v_object_type"].strip()      # The Highbond Object Type



# Status variable logic
if v_rejected_status_label_input == "":
    v_rejected_status_label = "Rejected"
else:
    v_rejected_status_label = v_rejected_status_label_input
    
# Object type variable logic
if v_object_type_input.upper() == "WALKTHROUGH":
    v_object_type = "CONTROL"
elif v_object_type_input.upper() == "CONTROL TEST":
    v_object_type = "CONTROL"
elif v_object_type_input.upper() == "RISK":
    v_object_type = "RISK"
else:
    v_object_type = str()
    
# Status variable logic
if v_region == "us":
    v_results_region = "results"
else:
    v_results_region = f"results-{v_region_input}"









# Grab records from Results Table (GET) and storing the project id in a variable
def get_results_records(v_results_table_id, meta = True, extra = True):

    results_response = hcl.hb_api.get("/tables/" + v_results_table_id + "/records")
    results_table_dict_all = results_response.json()
    results_table_df_all = pandas.json_normalize(results_table_dict_all['data'])
    results_table_df = results_table_df_all[(results_table_df_all.object_type.str.upper() == f"{v_object_type.upper()}")]

    #results_table_dict = results_table_dict_all["data"]
    matches = []
    if meta ==  False:
        matches.append("metadata.")
    if extra == False:
        matches.append("extras.")

    ########################################
    columns = results_table_dict_all['columns']
    rename_dict = {item['field_name']: item['display_name'] for item in columns if not any(x in item['field_name'] for x in matches)}
    results_table_df = results_table_df.rename(rename_dict,axis='columns')

    #getting the project id
    v_project_id = v_project_id = results_table_df["Project ID"].iloc[0]

    return results_table_df, v_project_id







# Grab walkthrough and control test ids from Highbond (GET) and store them in variables
def get_wt_ctrltest_id(v_control_id):

    control_response = hcl.hb_api.get("/controls/" + v_control_id + "?fields[controls]=all")
    control_dict_all = control_response.json()
    v_control_wt_id = control_dict_all["data"]["relationships"]["walkthrough"]["data"]["id"]
    v_control_ctrltest_id = control_dict_all["data"]["relationships"]["control_tests"]["data"][0]["id"]

    return v_control_wt_id, v_control_ctrltest_id





# Grab walkthrough and control test ids from Highbond (GET) and store them in variables
def get_analysis_collection_id(v_table_id):

    analysis_response = hcl.hb_api.get("/tables/" + v_table_id)
    analysis_dict_all = analysis_response.json()
    v_analysis_id = analysis_dict_all["data"]["relationships"]["analysis"]["data"]["id"]
    
    collection_response = hcl.hb_api.get("/analyses/" + v_analysis_id)
    collection_dict_all = collection_response.json()
    v_collection_id = collection_dict_all["data"]["relationships"]["collection"]["data"]["id"]

    return v_analysis_id, v_collection_id





# R I S K
# Grab Risk Scoring Factor labels from project type
def get_risk_scoring_factors(v_project_id):
    
    #get the project data and the project type id
    project_response = hcl.hb_api.get("/projects/" + v_project_i + "?fields[projects]=all")
    project_dict_all = project_response.json()
    v_project_type_id = project_dict_all["data"]["relationships"]["project_type"]["data"]["id"]
    
    #get the project type data and the risk scroing factor labels
    project_type_response = hcl.hb_api.get("/project_types/" + v_project_type_id + "?fields[project_types]=all")
    project_type_dict_all = project_type_response.json()
    v_risk_scoring_factor_1 = project_type_dict_all["data"]["attributes"]["risk_terms"]["term_for_risk_impact"]
    v_risk_scoring_factor_2 = project_type_dict_all["data"]["attributes"]["risk_terms"]["term_for_risk_likelihood"]
    
    return v_risk_scoring_factor_1, v_risk_scoring_factor_2


# Update Highbond risks (GET and PATCH) based on predefined ruleset
def get_and_patch_risk(risk_id,v_risk_scoring_factor_label_1,v_risk_scoring_factor_value_1,v_risk_scoring_factor_label_2,v_risk_scoring_factor_value_2):

    risk_url = "/risks/" + risk_id
    risk_response_get = hcl.api_get(risk_url)
    risk_response_dict = risk_response_get.json()

    print("Before state of risk: ", risk_response_dict["data"])
    risk_response_dict["data"]["attributes"][f"{v_risk_scoring_factor_label_1.lower()}"] = v_risk_scoring_factor_value_1
    risk_response_dict["data"]["attributes"][f"{v_risk_scoring_factor_label_2.lower()}"] = v_risk_scoring_factor_value_2
    print("After state of risk: ", risk_response_dict["data"])

    hcl.hb_api.patch(risk_url, data=risk_response_dict)

    return "Risk successfully updated!"




# C O N T R O L
# Update Highbond walkthrough or control test (GET and PATCH) based on predefined ruleset
def get_and_patch_wt_ctrltest(v_control_id,v_control_questionnaire_label_descr,v_control_questionnaire_label_concl):

    # Getting the walkthrough and control test id
    v_control_wt_id, v_control_ctrltest_id = get_wt_ctrltest_id(v_control_id)
    print("Control Walkthrough ID: ", v_control_wt_id)
    print("Control Control Test ID: ", v_control_ctrltest_id)
    
    # Getting the collection and analysis id then creating the results table url
    v_analysis_id, v_collection_id = get_analysis_collection_id(v_results_table_id)
    v_results_table_url = f"https://{v_subdomain}.{v_results_region}.highbond.com/projects/{v_collection_id}/controls/{v_analysis_id}/control_tests/{v_results_table_id}"
    
    # Setting the variable for description field
    if v_control_questionnaire_label_descr is None:
        v_control_questionnaire_label_descr_all = f"<b>Assessment source:</b> <a href={v_results_table_url}>Result Table Link</a>"
    else:
        v_control_questionnaire_label_descr_all = f"{v_control_questionnaire_label_descr} <br><br><b>Assessment source:</b> <a href={v_results_table_url}>Result Table Link</a>"

    if v_object_type_input.upper() == "WALKTHROUGH":
        wt_url = "/walkthroughs/" + v_control_wt_id
        wt_response_get = hcl.api_get(wt_url)
        wt_response_dict = wt_response_get.json()
        print("Before state of walkthrough: ", wt_response_dict["data"])
        wt_response_dict["data"]["attributes"]["control_design"] = v_control_questionnaire_label_concl
        wt_response_dict["data"]["attributes"]["walkthrough_results"] = v_control_questionnaire_label_descr_all
        print("After state of walkthrough: ", wt_response_dict["data"])
        hcl.hb_api.patch(wt_url, data=wt_response_dict)
        print(f"Walkthrough {v_control_wt_id} successfully updated!")
        
    if v_object_type_input.upper() == "CONTROL TEST":
        ctrltest_url = "/control_tests/" + v_control_ctrltest_id
        ctrltest_response_get = hcl.api_get(ctrltest_url)
        ctrltest_response_dict = ctrltest_response_get.json()
        print("Before state of control test: ", ctrltest_response_dict["data"])
        ctrltest_response_dict["data"]["attributes"]["testing_conclusion"] = v_control_questionnaire_label_concl
        ctrltest_response_dict["data"]["attributes"]["testing_results"] = v_control_questionnaire_label_descr_all
        print("After state of control test: ", ctrltest_response_dict["data"])
        ctrltest_response_patch = hcl.hb_api.patch(ctrltest_url, data=ctrltest_response_dict)
        print(f"Control Test {v_control_ctrltest_id} successfully updated!")
        
    return





# 1.) Get Results records and project id
results_table_df, v_project_id = get_results_records(v_results_table_id)
print("Project ID: ", v_project_id)
print("\nGET RESULTS RECORDS TASK (1) STATUS: SUCCESSFULLY RUN!\n")


# 2.) Get Risk Scoring Factor labels from project type, then get relevant risk records and update their statuses (run only if task run is for risk)
if v_object_type.upper() == "RISK":
    v_risk_scoring_factor_1, v_risk_scoring_factor_2 = get_risk_scoring_factors(v_project_id)
    print("Risk Scoring Factor 1: ", v_risk_scoring_factor_1)
    print("Risk Scoring Factor 2: ", v_risk_scoring_factor_2)
    print("\nGET RISK SCORING FACTORS TASK STATUS: SUCCESSFULLY RUN!\n")

    for index,row in results_table_df.iterrows():
        if (row[f"{v_risk_scoring_factor_1}"] is not None and row[f"{v_risk_scoring_factor_2}"] is not None) and (row["Status"] != f"{v_rejected_status_label}"):
            get_and_patch_risk(row["Object ID"],v_risk_scoring_factor_1,row[f"{v_risk_scoring_factor_1}"],v_risk_scoring_factor_2,row[f"{v_risk_scoring_factor_2}"])
            print(f"\nGET RELEVANT RISK RECORDS AND UPDATE THEIR RISK SCORING FACTORS TASK SUCCESSFULLY RAN FOR {row['Object ID']}!\n")
    print("\nUPDATE RISK SCORING TASK (2) STATUS: SUCCESSFULLY RUN!\n")


#3.) Get relevant walkthorugh records and update their statuses (run only if task run is for walkthroughs)
if v_object_type.upper() == "CONTROL":
    for index,row in results_table_df.iterrows():
        if (row[f"{v_control_questionnaire_label_concl}"] is not None) or (row["Status"] != f"{v_rejected_status_label}"):
            get_and_patch_wt_ctrltest(row["Object ID"],row[f"{v_control_questionnaire_label_descr}"],row[f"{v_control_questionnaire_label_concl}"])
            print(f"\nGET RELEVANT {v_object_type_input.upper()} RECORDS AND UPDATE THEIR ATTRIBUTES TASK SUCCESSFULLY RAN FOR {row['Object ID']}!\n")
    print("\nUPDATE CONTROL TESTS OR WALKTHROUGHS TASK (3) STATUS: SUCCESSFULLY RUN!\n")


print("\nROBOT TASK COMPLETED SUCCESSFULLY!\n")