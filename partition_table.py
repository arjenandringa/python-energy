import stdlib
import settings
from datetime import datetime, date, timedelta
# Execute partition_table daily at 00:00:01 to ensure a new table is created immediately at the start of the day.

def partition_name():
    return f"{settings.db}_" + date.today().strftime('%Y%m%d')

def bogus():
    print('bogus')

# First collect the day's stats.
def collect_stats():
    try:
        statsq = f"SELECT MAX(VALUE)-MIN(VALUE),SENSOR FROM {settings.db} GROUP BY sensor;"
        daily_stats = stdlib.db_conn(statsq)
    except (Exception, stdlib.psycopg2.Error) as error:
        stdlib.logger().error(f"Something went wrong: {error}")
    return dict([tuple(reversed(x)) for x in daily_stats])

# Process those stats and send them away
def process_daily_stats():
    http_data = {'content': f"{collect_stats()}"}
    stdlib.post(settings.daily_stats, http_data)

# Drop the partitioned table with value partition_name from the Previous Day.
def drop_table():
    pd_partition_name = f"{settings.db}_" + (date.today() - timedelta(days=1)).strftime('%Y%m%d')
    try:
        dropq = f"DROP TABLE {pd_partition_name}"
        stdlib.db_conn(dropq)
    except (Exception, stdlib.psycopg2.Error) as pg_error:
        stdlib.logger().error(f"Something went wrong, check the PGerror: {pg_error.pgerror}")
    else:
        stdlib.logger().info(f"Table dropped: {pd_partition_name}")

# Create a database partition. Should execute at midnight every day.
def partition_table():
    start = datetime.now().replace(hour=0,minute=0,second=0).strftime('%Y-%m-%d %H:%M:%S')
    end = datetime.now().replace(hour=23,minute=59,second=59).strftime('%Y-%m-%d %H:%M:%S')
    try:
        tableq = f"CREATE TABLE {partition_name()} PARTITION OF {settings.db} FOR VALUES FROM ('{start}') TO ('{end}');"
        stdlib.db_conn(tableq)
    except:
        stdlib.logger().error(f"Something went wrong while creating a new table, best check partition_name: {partition_name()}")
    else:
        stdlib.logger().info(f"New table created with name: {partition_name()}")

if __name__ == "__main__":
    process_daily_stats()
    drop_table()
    partition_table()
