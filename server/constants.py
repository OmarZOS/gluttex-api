

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
# print(DB_URI)
# raise Exception(DB_URI)



