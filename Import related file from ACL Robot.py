# ACL Robots can have related files uploaded to them. This script downloads and imports a related excel file from a specified ACL robot.

############################################################################################################
# Python modules

#importing excel requires xlrd dependency

import pandas
\!pip install xlrd
import xlrd


############################################################################################################
# Parameters

# Robot ID of the robot that contains the related file

file_robot_id = "23832"

# File name of the related file we want

file_name = "Finding_Details (4).xls"

############################################################################################################
# Helper functions


# Function to get the file_id from a robot based on the name of the related file

def get_file_id_from_robot(robot_id, file_name, environment="development"):
    resp = hcl.api_get(f'/robots/\{robot_id}/robot_files?env=\{environment}')
    resp_json =resp.json()
    print(resp_json)
    file_id = \[item\['id'] for item in resp_json\['data'] if item\['attributes']\['filename'] == file_name]
    if len(file_id) < 1:
        raise LookupError(f"Filename \{file_name} not found in Robot id: \{robot_id} in environment: \{environment}")
    id = str(file_id\[0])
    return id
    
# Downloads a related file from robots given a file id

def download_related_file_by_file_id(file_id, as_file_name):
    resp = hcl.api_get(f"/robot_files/\{file_id}/download")
    output = open(as_file_name, 'wb')
    output.write(resp.content)
    output.close()

# Downloads a related file from robots given a robot id, file name, and environment

def download_related_file_by_file_name(robot_id, file_name, environment="development"):
    related_file_id = get_file_id_from_robot(robot_id, file_name, environment)
    download_related_file_by_file_id(related_file_id, file_name)

############################################################################################################
# Download a file from robots and import it 

download_related_file_by_file_name(file_robot_id, file_name, environment="production")
my_df = pandas.read_excel(file_name)
my_df