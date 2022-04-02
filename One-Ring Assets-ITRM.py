# Import Libraries
import pandas as pd
import requests
import json
pd.set_option('display.max_columns', None)

### Parameters ###
org_id = hcl.variable["v_org_id"]                                 # Launchpad org id 
org_region = hcl.variable["v_region"]                             # Launchpad org region
results_id = hcl.variable["v_results_id"]                         # Result container to push data to 
hb_token = hcl.secret['v_hb_token'].unmask()                      # Request library requires token to be in plain text

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
# print(request_response)

# Create users Dataframe
df_users = pd.json_normalize(request_json['data'])
df_users

### Pull all Asset Types for this org  ###

# URL Endpoint as defined from https://docs-apis.highbond.com/public.html#operation/getRecords
request_url = api_env +"/orgs/"+ org_id +"/asset_types"

# Headers set for authentication; also need to add Accept-encoding as blank for the API
request_headers = {
  'Authorization': 'Bearer '+hb_token,
  'Content-Type' : 'application/vnd.api+json',
  'Accept-encoding':''
}

# Submit the request and grab the response, and convert it to JSON
request_response = requests.get(request_url, headers=request_headers)
request_json = request_response.json()

# Asset Types Dataframe 
df_asset_types = pd.json_normalize(request_json['data'])
df_asset_types


### Pull Asset Info for a particular asset type
### Paginate if necessary and join all info into one dataframe

def get_asset_dataframe(asset_type_id, asset_type_name):
    ### # A Function to get assets for a specific asset type ###
     
    # URI based on org and asset type
    request_url = api_env +"/orgs/"+ org_id +"/asset_types/"+ asset_type_id +"/assets"
    
    # Headers set for authentication; also need to add Accept-encoding as blank for the API
    request_headers = {
      'Authorization' : 'Bearer '+hb_token,
      'Content-Type' : 'application/vnd.api+json',
      'Accept-encoding' : ''
    }    
    
    # Make the Request and extract the JSON payload
    response = requests.get(request_url, headers=request_headers)
    raw = response.json()  
    
    if (len(raw['data']) == 0):
        return None
        
    # Initialize the dataframes with the information of the first page
    # 1. Asset info (that needs to be pivoted)
    # 2. Asset type info 
    # 3. Workflow info 
    df_all = pd.json_normalize(raw['data'], record_path=['attributes', 'asset_attributes'], meta='id')
    df_all = df_all.pivot(index = 'id', columns = 'field_name', values = 'value')
    df_all = df_all.reset_index()
    
    df_all_type = pd.json_normalize(raw['data'])
 
    df_workflow_status_id = pd.json_normalize(raw['data'], record_path=['attributes', 'asset_attributes'], meta='id')
    df_workflow_status_id = df_workflow_status_id.pivot(index = 'id', columns = 'field_name', values = 'value.id')
    df_workflow_status_id = df_workflow_status_id.reset_index()
    
    df_workflow_status_name = pd.json_normalize(raw['data'], record_path=['attributes', 'asset_attributes'], meta='id')
    df_workflow_status_name = df_workflow_status_name.pivot(index = 'id', columns = 'field_name', values = 'value.name')
    df_workflow_status_name = df_workflow_status_name.reset_index()
    
    df_owner = pd.json_normalize(raw['data'], record_path=['attributes', 'asset_attributes'], meta='id')
    df_owner = df_owner.pivot(index = 'id', columns = 'field_name', values = 'value.user_ids')
    df_owner = df_owner.reset_index()
    
    
    # Retrieve remaining pages and append to combined dataframes 
    while raw['links']['next'] != None and raw['links']['next'] != raw['links']['last'] :
        response = requests.get(api_env +"/orgs/"+org_id +raw['links']['next'], headers=request_headers)  
        raw = response.json()
   
        df_next_data = pd.json_normalize(raw['data'], record_path=['attributes', 'asset_attributes'], meta='id')
        df_next_data = df_next_data.pivot(index = 'id', columns = 'field_name', values = 'value')
        df_next_data = df_next_data.reset_index()
       
        df_next_type = pd.json_normalize(raw['data'])

        df_next_workflow_status_id = pd.json_normalize(raw['data'], record_path=['attributes', 'asset_attributes'], meta='id')
        df_next_workflow_status_id = df_next_workflow_status.pivot(index = 'id', columns = 'field_name', values = 'value.id')
        df_next_workflow_status_id = df_next_workflow_status.reset_index()
        
        df_next_workflow_status_name = pd.json_normalize(raw['data'], record_path=['attributes', 'asset_attributes'], meta='id')
        df_next_workflow_status_name = df_next_workflow_status.pivot(index = 'id', columns = 'field_name', values = 'value.name')
        df_next_workflow_status_name = df_next_workflow_status.reset_index()
        
        df_next_owner = pd.json_normalize(raw['data'], record_path=['attributes', 'asset_attributes'], meta='id')
        df_next_owner = df_next_owner.pivot(index = 'id', columns = 'field_name', values = 'value.user_ids')
        df_next_owner = df_next_owner.reset_index()
    
        df_all = pd.concat([df_all, df_next_data])
        df_all_type = pd.concat([df_all_type, df_next_type])
        df_workflow_status_id = pd.concat([df_workflow_status_id, df_next_workflow_status_id])
        df_workflow_status_name = pd.concat([df_workflow_status_name, df_next_workflow_status_name])
        df_owner = pd.concat([df_owner, df_next_owner])

    
    ### Join all dataframe information  

    df_combined = df_all

    # Get Asset Type ID 
    df_combined['Asset Type Id'] = asset_type_id
    
    # Get Asset Type Name 
    df_combined['Asset Type'] = asset_type_name
    
    df_combined.rename(columns={'id':'Asset Id'}, inplace=True)  

    # Get Workflow Status  - todo: use df_combined
    df_combined = df_combined.merge(df_workflow_status_id[['id', 'metadata.workflow_status']], left_on='Asset Id', right_on='id') 
    df_combined
    
    df_combined = df_combined.merge(df_workflow_status_name[['id', 'metadata.workflow_status']], left_on='Asset Id', right_on='id') 
    df_combined
       
    # Get Owners 
    df_combined = df_combined.merge(df_owner[['id', 'business_owner_(required)', 'technical_owner', 'metadata.created_by', 'metadata.updated_by']], left_on='Asset Id', right_on='id') 
    df_combined
    
    print(df_combined)
 
    return df_combined


### Pull all Assets of interest 

# Determine filters for asset types of interest 
# and pull information
filter_hardware = df_asset_types['attributes.name'] == "IT Asset - Hardware"
filter_software = df_asset_types['attributes.name'] == "IT Asset - Software"
filter_systems = df_asset_types['attributes.name'] == "IT Asset - Information System"
filter_cloud = df_asset_types['attributes.name'] == "IT Asset - Cloud"


asset_type_id = df_asset_types[filter_hardware]['id'].values[0]
df_hardware =  get_asset_dataframe(asset_type_id, "IT Asset - Hardware")
if (df_hardware is None):
    print('IT Asset - Hardware assets have not been installed.')

asset_type_id = df_asset_types[filter_software]['id'].values[0]
df_software =  get_asset_dataframe(asset_type_id, "IT Asset - Software")
if (df_software is None):
    print('IT Asset - Software assets have not been installed.')

asset_type_id = df_asset_types[filter_systems]['id'].values[0]
df_systems =  get_asset_dataframe(asset_type_id, "IT Asset - Information System")
if (df_systems is None):
    print('IT Asset - Information System assets have not been installed.')
    
asset_type_id = df_asset_types[filter_cloud]['id'].values[0]
df_cloud =  get_asset_dataframe(asset_type_id, "IT Asset - Cloud")
if (df_cloud is None):
    print('IT Asset - Cloud assets have not been installed.')

### New Cell
df_all = pd.concat([df_hardware, df_software, df_systems, df_cloud])
df_all = df_all.reset_index()
result = df_all
result

### New Cell
list(result.columns)


### New Cell
### Remove column that cause the upload to fail  'metadata.updated_at',

### Remove columns for reporting 
result.drop('id_x', axis=1, inplace=True)    #duplicate Asset Type ID from secondary table 
result.drop('id_y', axis=1, inplace=True)    #duplicate Asset Type ID from secondary table 
result.drop('Asset Id', axis=1, inplace=True)    #duplicate Asset ID  
result.drop('index', axis=1, inplace=True)   #no use, df specific
result.drop('business_owner_(required)_x', axis=1, inplace=True)   #no use, df specific
result.drop('technical_owner_x', axis=1, inplace=True)   #no use, df specific
result.drop('metadata.created_by_x', axis=1, inplace=True)  #duplicate from original record but empty  
result.drop('metadata.updated_by_x', axis=1, inplace=True)  #duplicate from original record but empty
result.drop('metadata.workflow_status_x', axis = 1, inplace = True)  #duplicate from original record but empty

### Rename columns for reporting 
result.rename(columns={'relationships.asset_type.data.id':'Asset Type Id'}, inplace=True)  
result.rename(columns={'relationships.workflow_status.data.id':'Workflow State Id'}, inplace=True)  
result.rename(columns={'attributes.name_x':'Asset Type'}, inplace=True)  
result.rename(columns={'attributes.name_y':'Workflow State'}, inplace=True)  

result.rename(columns={'business_owner_(required)_y':'business_owner'}, inplace=True)  
result.rename(columns={'technical_owner_y':'technical_owner'}, inplace=True)  
result.rename(columns={'reference_id_(required)':'reference_id'}, inplace=True)  

result.rename(columns={'metadata.id':'Asset Id'}, inplace=True)  
result.rename(columns={'metadata.created_at':'Asset Created At'}, inplace=True)  
result.rename(columns={'metadata.created_by_y':'Asset Created By'}, inplace=True)  
result.rename(columns={'metadata.updated_at':'Asset Updated At'}, inplace=True)  
result.rename(columns={'metadata.updated_by_y':'Asset Updated By'}, inplace=True)  
result.rename(columns={'metadata.workflow_status_y': 'Workflow State Id'}, inplace=True)
result.rename(columns={'metadata.workflow_status': 'Workflow State'}, inplace=True)

list(result.columns)


### New Cell
def remove_brackets(df, columns):
	for column in columns:
	     if column in df:
	        df[column] = df[column].str[0]
	    
fields = ['active_date',
 'availability_impact_level',
 'business_unit',
 'confidentiality_impact_level',
 'criticality_level',
 'description_(required)',
 'end_of_support_date',
 'hardware_device_type',
 'hostname_/_domain_name_/_url',
 'integrity_impact_level',
 'ip_address',
 'location',
 'manufacturer',
 'Asset Created At',
 'Asset Created By',
 'Asset Id',
 'Asset Updated At',
 'Asset Updated By',
 'model',
 'name',
 'reference_id',
 'serial_number',
 'total_asset_value',
 'business_owner',
 'technical_owner',
 'expiration_date',
 'license_id',
 'software_type',
 'version',
 'cloud_environment',
 'resource_state',
 'resource_type',
 'unique_cloud_id'
 ]
    
remove_brackets(result, fields)
result

### New Cell
# Match the names to the user ID 
result = result.merge(df_users[['uid', 'name']], left_on='Asset Created By', right_on='uid', how='left') 
result.drop('uid', axis=1, inplace=True)  
result.drop('Asset Created By', axis=1, inplace=True)  
result.rename(columns={'name_x':'name'}, inplace=True)  
result.rename(columns={'name_y':'Asset Created By'}, inplace=True)  

result = result.merge(df_users[['uid', 'name']], left_on='Asset Updated By', right_on='uid', how='left') 
result.drop('uid', axis=1, inplace=True) 
result.drop('Asset Updated By', axis=1, inplace=True)
result.rename(columns={'name_x':'name'}, inplace=True)  
result.rename(columns={'name_y':'Asset Updated By'}, inplace=True)  

result = result.merge(df_users[['uid', 'name']], left_on='technical_owner', right_on='uid', how='left') 
result.drop('uid', axis=1, inplace=True) 
result.drop('technical_owner', axis=1, inplace=True) 
result.rename(columns={'name_x':'name'}, inplace=True)  
result.rename(columns={'name_y':'technical_owner'}, inplace=True)  

result = result.merge(df_users[['uid', 'name']], left_on='business_owner', right_on='uid', how='left') 
result.drop('uid', axis=1, inplace=True) 
result.drop('business_owner', axis=1, inplace=True) 
result.rename(columns={'name_x':'name'}, inplace=True)  
result.rename(columns={'name_y':'business_owner'}, inplace=True) 
result

### New Cell
hcl_result = hcl.from_pandas(result)
hcl_result

### New Cell
hcl_result.to_hb_results(results_id, overwrite=True)