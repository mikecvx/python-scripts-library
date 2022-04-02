import requests

url = "https://apis.highbond-s1.com/v1/orgs/1000223/robots/10760/robot_files"

querystring = {"env":"development"}

payload = "-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"file\"; filename=\"audit_logs (1).json\"\r\nContent-Type: application/json\r\n\r\n\r\n-----011000010111000001101001--\r\n"
headers = {
    "Authorization": "Bearer <<INSERT TOKEN>>",
    "Accept": "application/vnd.acl.v1+json",
    "content-type": "multipart/form-data; boundary=---011000010111000001101001"
}

response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

print(response.text)