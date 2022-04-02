####  Paste this in a cell
!pip install presto-python-client
import prestodb
import pandas as pd
import requests
from datetime import datetime, timedelta, date
import sys
###




### Paste this in a different cell



#set up some variables, most of them from Task inputs

token = hcl.secret["v_hb_token"].unmask() #your HB token
v_user = hcl.variable['v_email']          #your username in HB
v_today = str(date.today())               
v_off_days =int(hcl.variable['v_days']) 
v_date = str(date.today() - timedelta(days=v_off_days)) # today - number of days to look back in the table
v_schema = 'ruben_rejon_training__inc_'   # schema, which is your org name sanitized to meet SQL standards
v_table = hcl.variable['v_table_name']
query = f'SELECT * FROM {v_table} WHERE \"metadata.publish_date\" >= TIMESTAMP \'{v_date}\''

# create the connection

conn = prestodb.dbapi.connect(
    host='presto.highbond.com',
    port=443,
    user=v_user,
    catalog='highbond',
    schema=v_schema,
    http_scheme='https',
    auth=prestodb.auth.BasicAuthentication(v_user, token)
)

# request the data and create a data frame

cur = conn.cursor()
cur.execute(query)
rows = cur.fetchall()
col_names = [i[0] for i in cur.description]
df = pd.DataFrame(rows, columns = col_names)
df.head(10)