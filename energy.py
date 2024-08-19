import stdlib
import settings
import requests
from datetime import datetime
from partition_table import partition_name

# Gather data from each endpoint and make a dict (key,value)
def energy_vars():
    data = {}
    information = requests.get(f"http://{settings.reader}/api/v1/data")
    for var in settings.endpoints:
        data[var] = information.json()[var]
    return data

# Throw those bad boys out there
def process_energy_vars():
    dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = energy_vars()
    for val in data:
        # Insert query
        iq = f"INSERT INTO {partition_name()} (CREATED_AT,SENSOR,VALUE) VALUES ('%s','%s',%s);" % (dt,val,data[val])
        stdlib.db_conn(iq)

if __name__ == "__main__":
    process_energy_vars()

# TODO
# Capture meaningful log messages
# Encrypted password
