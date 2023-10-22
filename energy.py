import stdlib
import settings
import requests
from datetime import datetime
from partition_table import partition_name

# Gather data from each endpoint and make a dict (key,value)
def energy_vars():
    data = {}
    for var in settings.endpoints:
        information = requests.get(f"http://{settings.reader}/sensor/{var}")
        data[information.json()['id']] = information.json()['value']
    return data

# Fix the data a little because the API returns silly things >:(
def fix_data_keys():
    data = energy_vars()
    for var in settings.endpoints:
        # Pop drops a key, the assignment allows the replacement of said dropped key
        data[var] = data.pop(f"sensor-{var}")
    return data

# Is it the weekend?
def tariff():
    # Current day of the week
    current_dotw = datetime.now().isoweekday()
    # current_hour needs to be encapsulated in int() otherwise it will actually be 011, which does not fit in range(7,22)
    current_hour = int(datetime.now().strftime('%H'))
    # Daarbij wordt van maandag tot en met vrijdag van 23.00 uur tot 7.00 uur, in het weekend (vrijdag 23.00 uur tot maandag 7.00 uur) en op officiële feestdagen een laag tarief berekend: https://www.oxxio.nl/over/nieuws/pieken-en-dalen
    if current_dotw in range(1,6) and current_hour in range(7,23):
        tariff = 'energy_consumed_tariff_2'
    else:
        tariff = 'energy_consumed_tariff_1'
    return tariff

# Throw those bad boys out there
def process_energy_vars():
    dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = fix_data_keys()
    for val in data:
        stdlib.db_conn()
        # Insert query
        iq = f"INSERT INTO {partition_name()} (CREATED_AT,SENSOR, VALUE) VALUES (%s,%s,%s);"
        # Insertables for %s
        i = (dt,val,data[val])
        stdlib.cursor.execute(iq,i)
        stdlib.conn.commit()
    stdlib.cursor.close()

if __name__ == "__main__":
    process_energy_vars()

# TODO
# Capture meaningful log messages
# Encrypted password