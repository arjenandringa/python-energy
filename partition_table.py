import energy
from datetime import datetime, date, timedelta
from retrying import retry
import settings

# Execute partition_table daily at 00:00:01 to ensure a new table is created immediately at the start of the day.

def partition_name():
    return 'energydb_' + date.today().strftime('%Y%m%d')

# First collect the day's stats.
def collect_stats():
    energy.db_conn()
    try:
        statsq = "SELECT MAX(VALUE)-MIN(VALUE),SENSOR FROM energydb GROUP BY sensor;"
        energy.cursor.execute(statsq)
        energy.conn.commit()
        daily_stats = energy.cursor.fetchall()
        energy.cursor.close()
    except (Exception, energy.psycopg2.Error) as error:
        energy.logger().error(f"Something went wrong: {error}")
    return dict([tuple(reversed(x)) for x in daily_stats])

# Process those stats and send them away
def process_daily_stats():
    http_data = {"content": f"{collect_stats()}"}
    energy.post(settings.daily_stats, http_data)

# Drop the partitioned table with value partition_name from the Previous Day.
@retry(wait_random_min=1000, wait_random_max=2000,stop_max_attempt_number=5)
def drop_table():
    pd_partition_name = 'energydb_' + (date.today() - timedelta(days=1)).strftime('%Y%m%d')
    try:
        energy.db_conn()
        dropq = f"DROP TABLE {pd_partition_name}"
        energy.cursor.execute(dropq)
        energy.conn.commit()
        energy.cursor.close()
    except (Exception, energy.psycopg2.Error) as pg_error:
        energy.logger().error(f"Something went wrong, check the PGerror: {pg_error.pgerror}")
    else:
        energy.logger().info(f"Table dropped: {pd_partition_name}")

# Create a database partition. Should execute at midnight every day.
def partition_table():
    energy.db_conn()
    start = datetime.now().replace(hour=0,minute=0,second=0).strftime('%Y-%m-%d %H:%M:%S')
    end = datetime.now().replace(hour=23,minute=59,second=59).strftime('%Y-%m-%d %H:%M:%S')
    try:
        tableq = f"CREATE TABLE {partition_name()} PARTITION OF energydb FOR VALUES FROM ('{start}') TO ('{end}');"
        energy.cursor.execute(tableq)
        energy.conn.commit()
        energy.cursor.close()
    except:
        energy.logger().error("Something went wrong while creating a new table, best check partition_name: {partition_name()}")
    else:
        energy.logger().info(f"New table created with name: {partition_name()}")

if __name__ == "__main__":
    process_daily_stats()
    drop_table()
    partition_table()