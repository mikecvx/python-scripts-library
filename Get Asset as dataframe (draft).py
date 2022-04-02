# get_asset_as_dataframe(asset_type_id,asset_id)
# Gets an asset by id into a dataframe


import pandas


def delistify_singleton_list(potential_list):
    """
    If the passed in value is a list with only one item, the item is returned.
    """
    return_value = potential_list
    if isinstance(potential_list, list):
        if len(potential_list) == 1:
            return_value = potential_list\[0]
    return return_value

def lookup_name_of_hb_user_id(user_id: str):
    #TODO : Unimplemented Currently a hack to grab the user id associated. Will need to replace this with an actual lookup on name
    return user_id

def parse_asset_attributes(asset_attributes_dict : dict):
    """
    Parse asset attributes into a proper dictionary.
    
    Input asset attributes dictionary comes from HighBond Public API spec here: https://docs-apis.highbond.com/public.html#operation/getAsset
    
    Parameters
    ----------
    asset_attributes_dict : dict
        Dictionary of asset attributes from getasset public API
    """
    
    asset_dict = \{}  #initialize asset dictionary for the function's return value
    
    for attribute in asset_attributes_dict\["asset_attributes"]:
        
        attribute_field_name = attribute\['field_name']
        attribute_value = attribute\['value']
        
        # Clean up the field names 
        # TODO: Make this step optional with a function parameter
        attribute_field_name = attribute_field_name.replace("_(required)","")
        attribute_field_name = attribute_field_name.replace("/_","")
        attribute_field_name = attribute_field_name.replace(".","_")
        
        if isinstance(attribute_value,dict):
            if "user_ids" in attribute_value:
                attribute_value = lookup_name_of_hb_user_id(attribute_value\["user_ids"])        
        
        attribute_value = delistify_singleton_list(attribute_value)
        
        # TODO: make excluding metadata and relationship columns optional
        if "metadata_" not in attribute_field_name and "." not in attribute_field_name:
            asset_dict\[attribute_field_name] = attribute_value
        
    return asset_dict

def get_asset_as_dataframe(asset_type_id,asset_id):
    """
    Import an asset as a dataframe.
    
    See HighBond Public API spec here: https://docs-apis.highbond.com/public.html#operation/getAsset
    
    Parameters
    ----------
    asset_type_id : str
    asset_id : str    
    """
    
    # Get the Asset via API
    response = hcl.api_get(f"/asset_types/\{asset_type_id}/assets/\{asset_id}")

    # Parse the asset attributes (they are nested in an ugly structure)
    asset_dict = parse_asset_attributes(response.json()\["data"]\["attributes"])

    # Convert the dictionary to a dataframe
    asset_df = pandas.json_normalize(asset_dict)

    #print(asset_df.columns)
    return asset_df