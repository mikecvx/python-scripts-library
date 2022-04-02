import pandas as pd
resp = hcl.api_get('/tables/156644/records')
json1 = resp.json()
df = pd.json_normalize(json1['data'])
columns = json1['columns']
rename_dict = {item['field_name']: item['display_name'] for item in columns}
df_renamed = df.rename(rename_dict,axis='columns')
df_renamed.head(1)