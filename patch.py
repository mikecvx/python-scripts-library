def update_risk_record(risk_id, new_impact, new_likelihood):
    risk_url = "/risks/"+risk_id # Define the endpoint for getting and patching
    try:
        risk_response = hcl.hb_api.get(risk_url)  # Grab the current version of the risk from projects
    except:
        return "Unable to get risk id "+risk_id
    risk_response_dict =  risk_response.json()  # Convert response to a dictionary
    print(risk_response_dict["data"]) # Before state
	risk_response_dict["data"]["attributes"]["impact"] = new_impact   # Update the impact with the new_impact
	risk_response_dict["data"]["attributes"]["likelihood"] = new_likelihood # Update the likelihoodwith the new_likelihood
    print(risk_response_dict["data"]) # After state
    update_response = "Not updated" # Default response
    # try patching the risk with the new values
	try:
		risk_response = hcl.hb_api.patch(risk_url, data=risk_response_dict)
	except:
		return "Unable to update risk"
    return "Successfully Updated"