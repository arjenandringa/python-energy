import requests
from datetime import datetime
import psycopg2
import logging
import settings

# Script lives as systemd unit with timer unit
# /etc/systemd/system/energy.service and ./energy.timer

def logger():
    logfile = settings.logfile
    logformat = "%(levelname)s %(asctime)s - %(message)s"
    logging.basicConfig(filename = logfile,
                        format = logformat,
                        level=logging.INFO)
    return logging.getLogger()

# Gather data from each endpoint and make a dict (key,value)
def energy_vars():
    data = {}
    for var in settings.endpoints:
        information = requests.get(f'http://{settings.reader}/sensor/{var}')
        data[information.json()['id']] = information.json()['value']
    return data

# Fix the data a little because the API returns silly things >:(
def fix_data_keys():
    data = energy_vars()
    for var in settings.endpoints:
        # Pop drops a key, the assignment allows the replacement of said dropped key
        data[var] = data.pop(f'sensor-{var}')
    return data

# Write the partition name for partition_table.py
def partition_name():
    partition_name = 'energydb_' + datetime.now().strftime('%Y%m%d')
    # Write partition name to file for use in drop_table()
    with open(f'{settings.workdir}/partition_name','w+',encoding='utf-8') as f:
        f.write(partition_name)
    return partition_name
    
# Set up database connection
def db_conn():
    try:
        global conn, cursor
        conn = psycopg2.connect(user=settings.user,password=settings.password,host=settings.dbhost,port=settings.port,database=settings.db)
        global cursor
        cursor = conn.cursor()
    except (Exception, psycopg2.Error) as error:
        logger().error(f"Postgres connection failed: {error}")

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
        db_conn()
        # Insert query
        iq = f"INSERT INTO {partition_name()} (CREATED_AT,SENSOR, VALUE) VALUES (%s,%s,%s);"
        # Insertables for %s
        i = (dt,val,data[val])
        cursor.execute(iq,i)
        conn.commit()
    cursor.close()

if __name__ == "__main__":
    process_energy_vars()

# TODO
# ~~ Write to logfile upon success and failure ~~ logger()
# Capture meaningful log messages
# ~~ Write main ~~ Si cabron.
# ~~ Script to evaluate data and post messages ~~ warn_gas_power.py
# ~~Postgres db storage: daily partitioning ~~: partition_table.py
# ~~ Postgres db logging ~~ No need. Drops daily anyway.
# ~~ Logrotate all logfiles to save storage ~~ Not necessary lul
# Encrypted password
