import requests
import json
import pandas
import numpy as np

##################################################################
# Populate variables. If they're not passed in use default values

org_regioncode = "us"
org_baseurl = "https://apis-"+org_regioncode+".highbond.com/v1/"

try:
    org_subdomain = hcl.variable["org_subdomain"]
except KeyError:
    org_subdomain = "piedpiper"
    
try:
    org_id = hcl.variable["org_id"]
except KeyError:
    org_id = "11024"
    
try:
    project_id = hcl.variable["project_id"]
except KeyError:
    project_id = "110982"
    
try:
    frequency_minutes = hcl.variable["frequency_minutes"]
except KeyError:
    frequency_minutes = 10
    
try:
    v_Slack_Webhook_URL = hcl.variable["slack_webhook"]
except KeyError:
    raise KeyError("slack_webhook variable not defined.")

try: 
    hcl.secret["v_hb_token"]
except KeyError:
    raise KeyError("HighBond token not defined.")
    
##################################################################
# Method for grabbing list of highbond issues from a project

def get_HB_Issues(project_id):
    v_HighBond_Issues_url = org_baseurl+"orgs/"+org_id+"/projects/"+project_id+"/issues"
    
    payload={}
    headers = {
      'Authorization': 'Bearer '+hcl.secret["v_hb_token"].unmask(),
    }
    
    response = requests.request("GET", v_HighBond_Issues_url, headers=headers, data=payload)
    
    if response.status_code != 200:
        raise ConnectionError("Could not connect to HighBond ("+v_HighBond_Issues_url+") to retrieve issues. Check the HighBond token value.")
    
    return response.text

##################################################################
# Grab issues and parse the response into a dictinary

issues_json = get_HB_Issues(project_id)
issues_dict = json.loads(issues_json)

# Parse issues dictionary into a dataframe. If the data element of the response is not available, then we will print the keys/response to troubleshoot the error
try:
    issues_pdf = pandas.json_normalize(issues_dict["data"])
except KeyError:
    print(issues_dict.keys())
    raise KeyError("Unable to parse the response (data is not available in the json) -- these keys are available: ["+",".join(issues_dict.keys())+"]")

# Parse created and updated datetimes into new computed fields
issues_pdf['updated_date'] = issues_pdf['attributes.updated_at'].astype('datetime64[ns]')
issues_pdf['created_date'] = issues_pdf['attributes.created_at'].astype('datetime64[ns]')

issues_pdf['newly_updated'] = np.where(issues_pdf['updated_date'] >= pandas.datetime.now() - pandas.Timedelta(minutes=frequency_minutes), True, False)
issues_pdf['newly_created'] = np.where(issues_pdf['created_date'] >= pandas.datetime.now() - pandas.Timedelta(minutes=frequency_minutes), True, False)

issues_pdf.head(10)

##################################################################
# helper method to remove html tags

def remove_html_tags(text):
    """Remove html tags from a string"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

##################################################################
# Reverse the dataframe so that newest items are on top

issues_pdf = issues_pdf[::-1]

# Loop through each issue, constructing the markdownmessage 
# to send to slack for each issue by grabbing its title, creator, and whether or not it's published

slack_blocks = []
current_issue_index = 0

for index, issue in issues_pdf.iterrows():
    
    # Grab issue creator
    
    issue_author = issue['attributes.creator_name'].strip()
    
    # Grab issue title and clean it and truncate it
    
    issue_title = issue['attributes.title'].strip()
    issue_title = remove_html_tags(issue_title).rstrip("\n")
    issue_title = (issue_title[:75] + '..') if len(issue_title) > 75 else issue_title
    
    # Grab issue description, clean it, and truncate it
    
    issue_description = issue['attributes.description'].strip()
    issue_description = remove_html_tags(issue_description).rstrip("\n")
    issue_description = (issue_description[:255] + '..') if len(issue_description) > 255 else issue_description
    issue_description = issue_description.rstrip("\r\n")
    
    # Grab whether the issue has been published
    
    if issue["attributes.published"] == True:
        issue_published = "Published"
    else:
        issue_published = "Not Published"
        
    # Reconstruct the issue URL so that users can click a link to go straight to it from Slack
    
    issue_url = "https://"+org_subdomain+".projects-"+org_regioncode+".highbond.com/audits/"+issue['relationships.project.data.id']+"/findings/"+issue['id']
    
    # If it's a newly created issue then add the author
    
    issue_author = "Ruben Rejon"
    
    slack_section_header = ""
    
    if issue['newly_created'] == True:
        slack_section_header = "*"+issue_author+" created issue: "+issue_title+"*"
    elif issue['newly_updated'] == True:
        slack_section_header = "*Issue updated: "+issue_title+"*"

    slack_section = {}
    slack_section["type"] = "section"
    slack_section["text"] = {"type":"mrkdwn","text": "> "+slack_section_header+"\n> "+issue_description + "\n> <"+issue_url+"|Open In HighBond>"}
    
    if issue['newly_created'] == True or issue['newly_updated'] == True:
        slack_blocks.append(slack_section)
        
# Peek at the message
payload = json.dumps({"text":"New Issue in HighBond","blocks":slack_blocks})
print(payload)

##################################################################
# Construct the payload to send to Slack and post it

print(v_Slack_Webhook_URL)

headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", v_Slack_Webhook_URL, headers=headers, data=payload)

print(response.text)