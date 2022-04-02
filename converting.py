Hi Team, just wanted to share a script snippet for importing a results table and converting it to a dataframe.
Challenge: I want to import a table from results. However, I might have issues because it contains metadata fields which cause issues when saving back to results, or has column names that are different from the display names.
Solution (##### lines are suggested cell boundaries):
#############################################################################################
# Import packages
import pandas
import json
import math
#############################################################################################
# get_from_hb_results(results_table_id, include_metadata=False, display_names=True)
# Grabs a table from results
# include_metadata = flag for whether or not to include metadata fields (e.g. priority, status, publisher, publish_date, etc.)
# display_names = flag for whether to convert the column names to their display names for easier readability
def get_from_hb_results(results_table_id, include_metadata=False, display_names=True):
    # URL Endpoint as defined from https://docs-apis.highbond.com/public.html#operation/getRecords
    # Note that we only need the part of the URL that is after the org_id -- everything else is handled by the hb_api module
    request_endpoint = "/tables/" + results_table_id + "/records/" 
    # Submit the request and grab the response, and convert it to JSON
    # Note that the hb_api methods handle authentication and org_id
    request_response = hcl.api_get(request_endpoint)
    # If the response isn't successful, raise it as an error. Probably because the API key is incorrect.
    if request_response.status_code != 200:
        raise ConnectionError("Could not connect to HighBond ("+request_endpoint+"). Check the HighBond token value: v_hb_token")
    # Grab the response as a JSON
    request_json = request_response.json()
    Results_Records_df = pandas.DataFrame(request_json["data"])        # Convert the response JSON to a dataframe -- we grab data from the "data" element
    print("Before: "+Results_Records_df.columns)    
    if not include_metadata:
        for column_name in Results_Records_df.columns:
            if column_name.startswith('metadata.') or column_name.startswith('extras.'): 
                del Results_Records_df[column_name]
    print("After: "+Results_Records_df.columns)    
    # Grab the columns metadata into a dataframe
    Results_Columns_df = pandas.DataFrame(request_json["columns"])
    # Create a dictionary from the display name and field name
    Results_Column_Mapping_dict = pandas.Series(Results_Columns_df.display_name.values,index=Results_Columns_df.field_name).to_dict()
    if display_names:
        # Grab the records from the response and rename the columns
        Results_Records_df.rename(columns = Results_Column_Mapping_dict, inplace = True)
        Results_Records_df = Results_Records_df.convert_dtypes()
    return Results_Records_df
#############################################################################################
# test the function above to grab a table from results
results_df = get_from_hb_results("442569")
results_df
(edited)
2 replies

Ruben Rejon  8 hours ago
I see that you use convert_dtypes()
Something that can help, to avoid surprises with Pandas guessing, is an explicit mapping
In the other direction, to_hb_result, we are doing it behind the scenes
I can paste here the mapping we do

Ruben Rejon  8 hours ago
When I code these calls, I keep the response as is, without raise
The API methods keeps the response very close to the real value returned by the API, and seeing a 404 or a 401 is helpful
But this is a personal preference
