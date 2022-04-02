# Import Libraries
import pandas as pd
import requests
import json
import sys
from datetime import datetime

pd.set_option('display.max_columns', None)


### Parameters ###
hb_token = hcl.secret['v_hb_token'].unmask()       # Request library requires token to be in plain text
api_env = "https://apis-us.highbond.com/v1"        # Adjust your environment to PROD or S1
org_id = hcl.variable["v_org_id"]                  # Launchpad ID 
org_region = hcl.variable["v_region"]              # Launchpad org region
results_id = hcl.variable["v_results_id"]          # Result Container to push data to 


### Pull Users for this org  ###
# URL API 
api_env = "https://apis-" + org_region + ".highbond.com/v1"      # Adjust your environment to PROD or S1

# URL Endpoint
request_url = api_env +"/orgs/"+ org_id +"/users"

# Headers 
request_headers = {
  'Authorization': 'Bearer '+hb_token,
  'Content-Type' : 'application/vnd.api+json',
  'Accept-encoding' : ''
}

# Submit the request and grab the response, and convert it to JSON
request_response = requests.get(request_url, headers=request_headers)
request_json = request_response.json()

# Confirm that the request was made successfully
print(request_response)


# Create users Dataframe
df_users = pd.json_normalize(request_json['data'])
df_users


### Pull all Record Types for this org  ###
# URL Endpoint as defined from https://docs-apis.highbond.com/public.html#operation/getRecords
request_url = api_env +"/orgs/"+ org_id +"/record_types"

# Headers set for authentication; also need to add Accept-encoding as blank for the API
request_headers = {
  'Authorization': 'Bearer '+hb_token,
  'Content-Type' : 'application/vnd.api+json',
  'Accept-encoding':''
}

# Submit the request and grab the response, and convert it to JSON
request_response = requests.get(request_url, headers=request_headers)
request_json = request_response.json()

# Confirm that the request was made successfully
print(request_response)


# Asset Types Dataframe 
df_record_types = pd.json_normalize(request_json['data'])
df_record_types


### Pull Records for a specific record type
### Paginate if necessary and join all info into one dataframe
def get_records_dataframe(record_type_id, record_type_name):
    ### # A Function to get records for a specific record  type ###
    
    # URI based on org and record type
    request_url = api_env +"/orgs/"+ org_id +"/record_types/"+ record_type_id +"/records"

    # Headers set for authentication; also need to add Accept-encoding as blank for the API
    request_headers = {
      'Authorization' : 'Bearer '+hb_token,
      'Content-Type' : 'application/vnd.api+json',
      'Accept-encoding' : ''
    }    
    
    # Make the Request and extract the JSON payload
    response = requests.get(request_url, headers=request_headers)
    raw = response.json()
    
    # If the length of the returned json is 0, then no records of this type are defined.
    # Return an empty set.
    if (len(raw['data']) == 0):
        return None

    # Initialize the dataframes with the information of the first page
    # 1. Record info (that needs to be pivoted)
    # 2. Record type info 
    # 3. Workflow info 
    # 4. Parent info (has asset ID)
    # 5. Owner info (has remediation and executive owner)

    df_all = pd.json_normalize(raw['data'], record_path=['attributes', 'record_attributes'], meta='id')
    df_all = df_all.pivot(index = 'id', columns = 'field_name', values = 'value')
    df_all = df_all.reset_index()

    df_all_type = pd.json_normalize(raw['data'])
    
    df_workflow_status_id = pd.json_normalize(raw['data'], record_path=['attributes', 'record_attributes'], meta='id')
    df_workflow_status_id = df_workflow_status_id.pivot(index = 'id', columns = 'field_name', values = 'value.id')
    df_workflow_status_id = df_workflow_status_id.reset_index()
    
    df_workflow_status_name = pd.json_normalize(raw['data'], record_path=['attributes', 'record_attributes'], meta='id')
    df_workflow_status_name = df_workflow_status_name.pivot(index = 'id', columns = 'field_name', values = 'value.name')
    df_workflow_status_name = df_workflow_status_name.reset_index()
        
    df_parent = pd.json_normalize(raw['data'], record_path=['attributes', 'record_attributes'], meta='id')
    df_parent = df_parent.pivot(index = 'id', columns = 'field_name', values = 'value.id')
    df_parent = df_parent.reset_index()
    
    df_owner = pd.json_normalize(raw['data'], record_path=['attributes', 'record_attributes'], meta='id')
    df_owner = df_owner.pivot(index = 'id', columns = 'field_name', values = 'value.user_ids')
    df_owner = df_owner.reset_index()
      
    # Retrieve remaining pages and append to combined dataframes 
    while raw['links']['next'] != None: 
        response = requests.get(api_env +"/orgs/"+org_id +raw['links']['next'], headers=request_headers)  
        raw = response.json()

        df_next_data = pd.json_normalize(raw['data'], record_path=['attributes', 'record_attributes'], meta='id')
        df_next_data = df_next_data.pivot(index = 'id', columns = 'field_name', values = 'value')
        df_next_data = df_next_data.reset_index()
        
        df_next_type = pd.json_normalize(raw['data'])
        
        df_next_workflow_status_id = pd.json_normalize(raw['data'], record_path=['attributes', 'record_attributes'], meta='id')
        df_next_workflow_status_id = df_next_workflow_status.pivot(index = 'id', columns = 'field_name', values = 'value.id')
        df_next_workflow_status_id = df_next_workflow_status.reset_index()
        
        df_next_workflow_status_name = pd.json_normalize(raw['data'], record_path=['attributes', 'record_attributes'], meta='id')
        df_next_workflow_status_name = df_next_workflow_status.pivot(index = 'id', columns = 'field_name', values = 'value.name')
        df_next_workflow_status_name = df_next_workflow_status.reset_index()
        
        df_next_parent = pd.json_normalize(raw['data'], record_path=['attributes', 'record_attributes'], meta='id')
        df_next_parent = df_next_parent.pivot(index = 'id', columns = 'field_name', values = 'value.id')
        df_next_parent = df_next_parent.reset_index()
        
        df_next_owner = pd.json_normalize(raw['data'], record_path=['attributes', 'record_attributes'], meta='id')
        df_next_owner = df_next_owner.pivot(index = 'id', columns = 'field_name', values = 'value.user_ids')
        df_next_owner = df_next_owner.reset_index()
        
        df_all = pd.concat([df_all, df_next_data])
        df_all_type = pd.concat([df_all_type, df_next_type])
        df_workflow_status_id = pd.concat([df_workflow_status_id, df_next_workflow_status_id])
        df_workflow_status_name = pd.concat([df_workflow_status_name, df_next_workflow_status_name])
        df_parent = pd.concat([df_parent, df_next_parent])
        df_owner = pd.concat([df_owner, df_next_owner])
    
    ### Join all dataframe information  
    df_combined = df_all

    # Get Record Type ID 
    df_combined['Record Type Id'] = record_type_id
    
    # Get Record Type Name 
    df_combined['Record Type'] = record_type_name
    
    # Get Asset ID 
    df_combined = df_combined.merge(df_parent[['id', 'parent']], left_on='id', right_on='id') 
    df_combined
    
    # Get Remediation and Executive Owner 
    df_combined = df_combined.merge(df_owner[['id', 'tprm:remediation_owner', 'tprm:executive_owner', 'metadata.created_by', 'metadata.updated_by']], left_on='id', right_on='id') 
    df_combined

    # Get Workflow Status 
    df_combined = df_combined.merge(df_workflow_status_id[['id', 'metadata.workflow_status']], left_on='id', right_on='id') 
    df_combined
    
    df_combined = df_combined.merge(df_workflow_status_name[['id', 'metadata.workflow_status']], left_on='id', right_on='id') 
    df_combined
     
    return df_combined



### Pull all Records  of interest 
# Determine filters for record types of interest and pull info
filter_incidents = df_record_types['attributes.name'] == "Finding"
record_type_id = df_record_types[filter_incidents]['id'].values[0]

df_incidents = get_records_dataframe(record_type_id, "Finding")

if (df_incidents is None):
    v_error_text = "There are no Third-party incidents within the org."
    raise ConnectionError(v_error_text)

df_incidents

### Remove columns for reporting 
result = df_incidents
result.drop('id', axis=1, inplace=True)                        #duplicate Workflow ID from secondary table 
result.drop('parent_x', axis=1, inplace=True)                  #blank from df_all import(not flat)
result.drop('tprm:remediation_owner_x', axis=1, inplace=True)  #blank from df_all import(not flat)
result.drop('tprm:executive_owner_x', axis=1, inplace=True)    #blank from df_all import(not flat)
result.drop('metadata.created_by_x', axis=1, inplace=True)     #duplicate from original record but empty  
result.drop('metadata.updated_by_x', axis=1, inplace=True)     #duplicate from original record but empty  
result.drop('metadata.workflow_status_x', axis=1, inplace=True)


### Rename columns for reporting 
result.rename(columns={'relationships.record_type.data.id':'Record Type Id'}, inplace=True)  
result.rename(columns={'relationships.workflow_status.data.id':'Workflow State Id'}, inplace=True)  
result.rename(columns={'attributes.name_x':'Record Type'}, inplace=True)  
result.rename(columns={'attributes.name_y':'Workflow State'}, inplace=True)  
result.rename(columns={'parent_y':'Asset ID'}, inplace=True)  
result.rename(columns={'tprm:remediation_owner_y':'tprm:remediation_owner'}, inplace=True)  
result.rename(columns={'tprm:executive_owner_y':'tprm:executive_owner'}, inplace=True)  

result.rename(columns={'metadata.id':'Incident Id'}, inplace=True)  
result.rename(columns={'metadata.created_at':'Incident Created At'}, inplace=True)  
result.rename(columns={'metadata.created_by_y':'Incident Created By'}, inplace=True)  
result.rename(columns={'metadata.updated_at':'Incident Updated At'}, inplace=True)  
result.rename(columns={'metadata.updated_by_y':'Incident Updated By'}, inplace=True)  
result.rename(columns={'metadata.workflow_status_y': 'Workflow State Id'}, inplace=True)
result.rename(columns={'metadata.workflow_status': 'Workflow State'}, inplace=True)

list(result.columns)

#New Cell
result.head()


def remove_brackets(df, columns):
    for column in columns:
        if column in df:
            df[column] = df[column].str[0]

    
fields = [
 'Incident Created At',
 'Incident Created By',
 'Incident Id',
 'Incident Updated At',
 'Incident Updated By',
 'name',
 'tprm:actual_remediation_date',
 'tprm:answer',
 'tprm:assessment_id',
 'tprm:assessment_name',
 'tprm:assessment_responder',
 'tprm:assessment_send_date',
 'tprm:category',
 'tprm:date_created',
 'tprm:date_updated',
 'tprm:domain',
 'tprm:escalation_level',
 'tprm:explanation',
 'tprm:identified_gap',
 'tprm:impact',
 'tprm:issue_type',
 'tprm:question_description',
 'tprm:question_id',
 'tprm:remediation_deadline',
 'tprm:remediation_plan',
 'tprm:severity',
 'tprm:sign-off',
 'tprm:sub-category',
 'tprm:remediation_owner', 
 'tprm:executive_owner'
 ]
    
remove_brackets(result, fields)
result


# Match the names to the user ID 
# If there is no match, replace with Marco as default
result = result.merge(df_users[['uid', 'name']], left_on='tprm:remediation_owner', right_on='uid', how='left') 
result.drop('uid', axis=1, inplace=True)  
result.drop('tprm:remediation_owner', axis=1, inplace=True)  
result.rename(columns={'name_x':'name'}, inplace=True)  
result.rename(columns={'name_y':'tprm:remediation_owner'}, inplace=True)  

result = result.merge(df_users[['uid', 'name']], left_on='tprm:executive_owner', right_on='uid', how='left') 
result.drop('uid', axis=1, inplace=True) 
result.drop('tprm:executive_owner', axis=1, inplace=True) 
result.rename(columns={'name_x':'name'}, inplace=True)  
result.rename(columns={'name_y':'tprm:executive_owner'}, inplace=True)  

result = result.merge(df_users[['uid', 'name']], left_on='Incident Updated By', right_on='uid', how='left') 
result.drop('uid', axis=1, inplace=True) 
result.drop('Incident Updated By', axis=1, inplace=True) 
result.rename(columns={'name_x':'name'}, inplace=True)  
result.rename(columns={'name_y':'Incident Updated By'}, inplace=True)  

result = result.merge(df_users[['uid', 'name']], left_on='Incident Created By', right_on='uid', how='left') 
result.drop('uid', axis=1, inplace=True) 
result.drop('Incident Created By', axis=1, inplace=True) 
result.rename(columns={'name_x':'name'}, inplace=True)  
result.rename(columns={'name_y':'Incident Created By'}, inplace=True) 

result

#New Cell
hcl_result = hcl.from_pandas(result)
hcl_result


#New Cell
hcl_result.to_hb_results(results_id, overwrite=True)