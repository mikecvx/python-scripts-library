# This function takes the response from the API or the HCL GET method as is, and returns a data frame where the columns use the Display name that you can see in Results
# It is helpful if you are dealing with questionnaires where they are assigned a random named starting with q
# You can choose if you want to rename metadata fields and/or extra fields
# Note: there will be another function to use in situations like Presto imports, where the API response does not have the information


#Function that creates a data frame where the columns have the display name instead of the field name
####
#Input:
## response: the payload from the HCL or API call to Results
## meta    : (optiona), if you want to rename the metadata fields as well. Default is True
## extra   : (optiona), if you want to rename the extra fields as well. Default is True
####
#Output:
## data frame with the columns renamed with the Result table display names


def renamefields(response,meta = True, extra = True):
    resp_json = response.json()
    df = pd.json_normalize(resp_json['data'])
    #determine if we are going to rename metadata and/or extra fields
    matches = []
    if meta ==  False:
        matches.append("metadata.")
    if extra == False:
        matches.append("extras.")
    ########################################
    columns = resp_json['columns']
    rename_dict = {item['field_name']: item['display_name'] for item in columns if not any(x in item['field_name'] for x in matches)}
    df_renamed = df.rename(rename_dict,axis='columns')
    return df_renamed



##################
# Examples:

resp = hcl.api_get('/tables/4632/records')
#json1 = resp.json()
df_renamed = renamefields(resp, extra=False)
df_renamed2 = renamefields(resp, True, False)