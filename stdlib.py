import logging
import psycopg2
from datetime import datetime, date, timedelta
import requests
import settings

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
    # Default header for Discord
    header = {"Content-Type": "application/json"}
    requests.post(webhook, json, header)

# Default db connection
def db_conn():
    try:
        global conn, cursor
        conn = psycopg2.connect(user=settings.user,password=settings.password,host=settings.dbhost,port=settings.port,database=settings.db)
        global cursor
        cursor = conn.cursor()
    except (Exception, psycopg2.Error) as error:
        logger().error(f"Postgres connection failed: {error}")