

import os


# # getting a list of scylla node names ["node1","node2"]
# SCYLLA_NODES = os.getenv("SCYLLA_NODES").split(",")
# SCYLLA_KEYSPACE = os.getenv("SCYLLA_DEFAULT_KEYSPACE")


SQL_SCHEMA = os.getenv("SQL_SCHEMA","mysql+pymysql")
SQL_HOST = os.getenv("SQL_HOST","172.18.0.2")
SQL_USER = os.getenv("SQL_USER","root")
SQL_PASSWORD = os.getenv("SQL_PASSWORD","dev_password")
SQL_DATABASE = os.getenv("SQL_DATABASE","gluttex")
DB_URI = f"{SQL_SCHEMA}://{SQL_USER}:{SQL_PASSWORD}@{SQL_HOST}/{SQL_DATABASE}"



GOOGLE_CLIENT_ID = os.getenv("API_GOOGLE_CLIENT_ID",'')
GOOGLE_CLIENT_SECRET = os.getenv("API_GOOGLE_CLIENT_SECRET",'')
FACEBOOK_CLIENT_ID = os.getenv("API_FACEBOOK_CLIENT_ID",'')
FACEBOOK_CLIENT_SECRET = os.getenv("API_FACEBOOK_CLIENT_SECRET",'')
INSTAGRAM_CLIENT_ID = os.getenv("API_INSTAGRAM_CLIENT_ID",'')
INSTAGRAM_CLIENT_SECRET = os.getenv("API_INSTAGRAM_CLIENT_SECRET",'')
SECRET_KEY = os.getenv("API_SECRET_KEY",'')




# COMPUTING_SERVER_BASE_URL = os.getenv("COMPUTING_SERVER_BASE_URL","gluttex") 



