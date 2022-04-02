#############################################################################################################
import requests
import json
import pandas
#############################################################################################################
# Grab the variables for which project/framework we're grabbing data from; set a default value if left blank
if hcl.variable["project_id"].strip():
    project_id = hcl.variable["project_id"]
else:
    project_id = "5718"
# Grab the variables for which results table to publish to; set a default value if blank
if hcl.variable["results_table_id"].strip():
    results_table_id = hcl.variable["results_table_id"]
else:
    results_table_id = "10827"
# Are we getting data from a project or a framework?
if hcl.variable["project_or_framework"].strip():
    project_or_framework = hcl.variable["project_or_framework"]
else:
    project_or_framework = "framework"
# Are we debugging?
debug = True
#############################################################################################################
#Function that will handle the pagination
# input:
## url = HB resource
## out1 = list where we store the elements retrieved
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
def flatten_custom_attributes(custom_attribute_field_value):
    custom_attribute_dict = {} # Initialize empty dictionary
    for attribute in custom_attribute_field_value:           # There can be multiple custom attributes, so we need to loop through each one to parse it
        if isinstance(attribute["value"], list) and len(attribute["value"]) == 1:   # If the custom attribute value is a list itself and only having one value, "de-listify it"
            attribute["value"] = attribute["value"][0] # De listifies the value list
        custom_attribute_dict[attribute["term"]] = attribute["value"] # Create the dictionary tuple with the custom attribute term and value
    return custom_attribute_dict # Return the completed dictionary
def prepare_df(data):
    df1 = pd.json_normalize(data)
    df2 = pd.json_normalize(df1["attributes.custom_attributes"].apply(flatten_custom_attributes))
    #rename columns
    df1.columns = df1.columns.str.replace('^attributes.', '')
    output= df1.join(df2)
    return output
def saverecords(obj,id):
    hcl1 = hcl.from_pandas(obj)
    hcl1.to_hb_results(id, overwrite=True)
#############################################################################################################
# Grab Objective list of the project
objectives_list = highbond_api_get_all("/"+project_or_framework+"s/" + project_id +"/objectives")
objectives_df = pandas.json_normalize(objectives_list) # First convert list list of risk dictionaries to a dataframe
objectives_df
#############################################################################################################
risk_list = []
# for each objective in the objective list, grab the risks
for objective in objectives_list:
    current_risk_list = highbond_api_get_all("/objectives/" + objective["id"] +"/risks") # Grab list of risks for the current objectiveP
    risk_list = risk_list + current_risk_list
print(risk_list)
risks_df = pandas.json_normalize(risk_list) # First convert list list of risk dictionaries to a dataframe
risks_df
#############################################################################################################
control_list = []
control_fields = "title,description,control_id,custom_attributes,mitigations"
# for each objective in the objective list, grab the risks
for objective in objectives_list:
    current_control_list = highbond_api_get_all("/objectives/" + objective["id"] +"/controls?fields[controls]="+control_fields) # Grab list of controls for the current objectiveP
    control_list = control_list + current_control_list
print(control_list)
controls_df = pandas.json_normalize(control_list) # First convert list list of risk dictionaries to a dataframe
controls_df
#############################################################################################################
mitigations_id_list=[]
for control in control_list:
    mitigation_data = control['relationships']['mitigations']['data']
    mitigations_id_list.extend(mitigation_data)
mitigations_id_list
#############################################################################################################
mitigations=[]
for mitigation_id in mitigations_id_list:
    mitigations_response = hcl.api_get('/mitigations/'+mitigation_id['id'])
    mitigations_json = mitigations_response.json()
    mitigations.append(mitigations_json['data'])
mitigations_df = pandas.json_normalize(mitigations)
mitigations_df
#############################################################################################################
risks_df = pandas.json_normalize(risk_list) # First convert list list of risk dictionaries to a dataframe
# This function converts the custom attributes column into a dictionary 
def flatten_custom_attributes(custom_attribute_field_value):
    custom_attribute_dict = {} # Initialize empty dictionary
    for attribute in custom_attribute_field_value:           # There can be multiple custom attributes, so we need to loop through each one to parse it
        if isinstance(attribute["value"], list) and len(attribute["value"]) == 1:   # If the custom attribute value is a list itself and only having one value, "de-listify it"
            attribute["value"] = attribute["value"][0] # De listifies the value list
        custom_attribute_dict[attribute["term"]] = attribute["value"] # Create the dictionary tuple with the custom attribute term and value
    return custom_attribute_dict # Return the completed dictionary
# If custom attributes exist, then convert them to columns in the dataframe
if "attributes.custom_attributes" in risks_df.columns: 
    custom_attribute_df = pandas.json_normalize(risks_df["attributes.custom_attributes"].apply(flatten_custom_attributes)) # Convert the custom attributes into a dataframe using the above function
    risks_df = risks_df.join(custom_attribute_df) # Join the custom attribute dataframe to our risks dataframe
risks_df
#############################################################################################################
controls_df = pandas.json_normalize(control_list) # First convert list list of risk dictionaries to a dataframe
# If custom attributes exist, then convert them to columns in the dataframe
if "attributes.custom_attributes" in controls_df.columns: 
    custom_attribute_df = pandas.json_normalize(controls_df["attributes.custom_attributes"].apply(flatten_custom_attributes)) # Convert the custom attributes into a dataframe using the above function
    controls_df = controls_df.join(custom_attribute_df) # Join the custom attribute dataframe to our controls dataframe
controls_df
#############################################################################################################
list_of_controls_fields = ["control_id","Mitigation/Controls","Residual Impact Ranking","Residual Likelihood Ranking"]
mitigations_df["risk_id"] = mitigations_df["relationships.risk.data.id"]
mitigations_df["control_id"] = mitigations_df["relationships.control.data.id"]
mitigations_df = mitigations_df[["risk_id","control_id"]]
risks_df["risk_id"] = risks_df["id"]
controls_df["Mitigation/Controls"] = controls_df["attributes.description"] 	
controls_df["control_id"] = controls_df["id"]
controls_df = controls_df[list_of_controls_fields]
risks_controls_df = pandas.merge(mitigations_df, risks_df, on="risk_id")
risks_controls_df = pandas.merge(risks_controls_df, controls_df, on="control_id")
risks_controls_df
#############################################################################################################
# Remove column name prefix of "attributes"
risks_controls_df.columns = risks_controls_df.columns.str.replace('^attributes.', '')
risks_controls_df.columns = risks_controls_df.columns.str.replace('_attributes.', '_')
# Clean up the titles of the columns
risks_controls_df.columns = map(str.title, risks_controls_df.columns)
risks_controls_df.columns = risks_controls_df.columns.str.replace('_',' ')
risks_controls_df.columns
# Remove useless columns (if they exist)
for column_name in risks_controls_df.columns:
    if column_name == "Custom Attributes":
        del risks_controls_df[column_name]
    if "Relationships." in column_name:
        del risks_controls_df[column_name]
risks_controls_df
#############################################################################################################
risks_hcl_df = hcl.from_pandas(risks_controls_df)
risks_hcl_df.to_hb_results(results_table_id)
#############################################################################################################