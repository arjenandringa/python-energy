import logging
import psycopg2
import requests
import settings
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

# Run the blocking scheduler to keep the app alive during runtime, otherwise Docker assumes it's done and the process ends
scheduler = BlockingScheduler(timezone=Europe/Amsterdam)

# Logging function (logs to settings.logfile)
def logger():
    logfile = settings.logfile
    logformat = "%(levelname)s %(asctime)s - %(message)s"
    logging.basicConfig(filename = logfile,
                        format = logformat,
                        level=logging.INFO)
    return logging.getLogger()

# Post lib
def post(webhook, json):
    # Default header for Discord, adapt to your liking
    header = {"Content-Type": "application/json"}
    requests.post(webhook, json, header)

# Postgres connection - Handles all DML & limited DDL
def db_conn(query):
    try:
        print(f"Found query: {query}")
        conn = psycopg2.connect(user=settings.user,password=settings.password,host=settings.dbhost,port=settings.port,database=settings.db)
        cursor = conn.cursor()
        cursor.execute(query)
        # If there is no logline for the select, there's most likely a db/query error, check logs, .
        conn.commit()
        if "SELECT" in query:
            returnable = cursor.fetchall()
            conn.close()
            return returnable
        else:
            conn.close()
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
