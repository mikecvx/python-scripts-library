# Import libraries
import pandas as pd
import json

# Set the variables
v_results_table_id    = hcl.variable["v_results_table_id"].strip()    # The Results Table ID
v_results_analysis_id = hcl.variable["v_results_analysis_id"].strip() # The Results Analysis ID
v_control_update_flag = hcl.variable["v_control_update_flag"].strip().upper() # Control update logic
v_wt_update_flag      = hcl.variable["v_wt_update_flag"].strip().upper() # ToD update logic






# Grab records from Results Table (GET)
def get_results_records(v_results_table_id):
    try:
        results_response = hcl.hb_api.get("/tables/" + v_results_table_id + "/records")
    except:
        return "Unable to get recrods from Results Table with id: " + v_results_table_id
    results_table_dict_all = results_response.json()
    results_table_dict = results_table_dict_all["data"]
    return results_table_dict
	
	
	
	
# Update Highbond controls (GET and PATCH) based on predefined ruleset
def get_and_patch_control(control_id,owner_yes_no,current_owner,current_owner_email):
    control_url = "/controls/" + control_id
    try:
        control_response_get = hcl.api_get(control_url)
    except:
        return "Unable to get control id: " + control_id
    control_response_dict = control_response_get.json()
    print("Before state of control: ", control_response_dict["data"])
    if owner_yes_no == "No":
        control_response_dict["data"]["attributes"]["owner"] = current_owner
        control_response_dict["data"]["attributes"]["custom_attributes"][2]["value"].clear()
        control_response_dict["data"]["attributes"]["custom_attributes"][2]["value"].append(current_owner_email)
    else:
        pass
    print("After state of control: ", control_response_dict["data"])
    # try patching the control with the new values
    try:
        control_response_patch = hcl.hb_api.patch(control_url, data=control_response_dict)
    except:
        return "Unable to update control owner!"
    return "Control owner successfully updated!"
	
	


# Update Highbond walkthroughs (GET and PATCH) based on predefined ruleset
def get_and_patch_test_of_wt(wt_id,wt_test_yes_no,wt_test_desc,wt_test_conf,wt_test_evidence):
    try:
        wt_url = "/walkthroughs/" + wt_id
        wt_response_get = hcl.api_get(wt_url)
        wt_response_dict = wt_response_get.json()
    except:
        return "Unable to get walkthrough id: " + wt_id
    if wt_test_yes_no == "Yes":
        wt_test_yes_no_final = "Designed Effectively"
    elif wt_test_yes_no == "No":
        wt_test_yes_no_final = "Design Failed"
    else:
        wt_test_yes_no_final = ""
    if wt_test_evidence is not None:
        v_results_evidence_id = wt_test_evidence.split('-')[0]
        wt_test_evidence_final = "https://richemont-international-sa.results-eu.highbond.com/projects/29959/controls/" + v_results_analysis_id + "/control_tests/" + v_results_table_id + "/exception_attachments/" + v_results_evidence_id + "/download"
    else:
        wt_test_evidence_final = None
    print("Before state of walkthrough: ", wt_response_dict["data"])
    try:
        wt_response_dict["data"]["attributes"]["custom_attributes"][0]["value"].clear()
        wt_response_dict["data"]["attributes"]["custom_attributes"][0]["value"].append(wt_test_yes_no_final)
        wt_response_dict["data"]["attributes"]["custom_attributes"][1]["value"].clear()
        wt_response_dict["data"]["attributes"]["custom_attributes"][1]["value"].append(wt_test_desc)
        wt_response_dict["data"]["attributes"]["custom_attributes"][2]["value"].clear()
        wt_response_dict["data"]["attributes"]["custom_attributes"][2]["value"].append(wt_test_conf)
        wt_response_dict["data"]["attributes"]["custom_attributes"][3]["value"].clear()
        wt_response_dict["data"]["attributes"]["custom_attributes"][3]["value"].append(wt_test_evidence_final)
    except:
        pass
    print("After state of walkthrough: ", wt_response_dict["data"])
    # try patching the walkthrough with the new values
    try:
        wt_response_patch = hcl.hb_api.patch(wt_url, data=wt_response_dict)
    except:
        return "Unable to update walkthrough data!"
    return "Walkthrough data successfully updated!"




# 1.) Get Results records
results_table_dict = get_results_records(v_results_table_id)
print("\GET RESULTS RECORDS TASK HAS SUCCESSFULLY RUN!\n")

#2.) Get relevant control records and update their statuses
if v_control_update_flag == "YES":
    for item_in_res_tab_dict in results_table_dict:
        get_and_patch_control(item_in_res_tab_dict["Control Id"],item_in_res_tab_dict["q973647"],item_in_res_tab_dict["q973648"],item_in_res_tab_dict["q973649"])
        print(f"\nGet relevant control records and update their statuses task successfully ran for {item_in_res_tab_dict['Control Id']}!\n")
    print("\nUPDATE CONTROLS TASK HAS SUCCESSFULLY RUN!\n")

#3.) Get relevant walkthrough records and update their statuses
if v_wt_update_flag == "YES":
    for item_in_res_tab_dict in results_table_dict:
        get_and_patch_test_of_wt(item_in_res_tab_dict["Walkthrough Id"],item_in_res_tab_dict["q973651"],item_in_res_tab_dict["q973652"],item_in_res_tab_dict["q975972"],item_in_res_tab_dict["q973650"])
        print(f"\nGet relevant test of desing records and update their statuses task successfully ran for {item_in_res_tab_dict['Walkthrough Id']}!\n")
    print("\nUPDATE TEST OF DESIGN TASK HAS SUCCESSFULLY RUN!\n")


print("\nROBOT TASK COMPLETED SUCCESSFULLY!\n")



