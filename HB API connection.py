# Method for grabbing list of highbond issues from a project

def get_HB_Issues(project_id):
    v_HighBond_Issues_url = "https://apis-us.highbond.com/v1/orgs/"+org_id+"/projects/"+project_id+"/issues"
    
    payload={}
    headers = {
      'Authorization': 'Bearer '+hcl.secret["v_hb_token"].unmask(),
    }
    
    response = requests.request("GET", v_HighBond_Issues_url, headers=headers, data=payload)
    return response.text

issues_json = get_HB_Issues(project_id)

issues_dict = json.loads(issues_json)
print(issues_dict.keys())








# Peek at the message
print(markdownmessage)


# Construct the payload to send to Slack and post it

payload = json.dumps({
  "text": markdownmessage
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", v_Slack_Webhook_URL, headers=headers, data=payload)

print(response.text)





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




url_header ='https://apis-us.highbond.com/v1/orgs/11024' #This is just the Piper organization
url_body = '/collections/' # You can tweak this to whichever source you want

token =  hcl.secret["v_hb_token"].unmask() # remember to have a password variable called v_hb_token first!
url = url_header+url_body

header = {
    'Authorization': 'Bearer {}'.format(hcl.secret["v_hb_token"].unmask()),
    'Content-Type': 'application/vnd.api+json'
}

response = requests.get(url, headers=header) # Sending a GET
request_json = response.json()
Results_Records_pdf = pandas.DataFrame(request_json["data"])        # Convert the response JSON to a dataframe -- we grab data from the "data" element
print(Results_Records_pdf)

