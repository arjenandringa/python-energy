import energy
from datetime import datetime
import settings
from retrying import retry

# Execute partition_table daily at 00:00:01 to ensure a new table is created immediately at the start of the day.

# First collect the day's stats and post them.
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

def write_partition_name():
    # Write partition name to file for use in drop_table()
    with open(f'{settings.workdir}/partition_name','w+',encoding='utf-8') as f:
        f.write(energy.partition_name())

# Drop the partitioned table with value partition_name from the Previous Day. Retrying mechanism implemented because this tends to fail every few days.
# Bug for which retrying is implemented has been fixed, but retrying will still be kept around for now.
@retry(wait_random_min=1000, wait_random_max=2000,stop_max_attempt_number=5)
def drop_table():
    with open(f'{settings.workdir}/partition_name','r',encoding='utf-8') as f:
        pd_partition_name = f.read()
    # Do not execute drop_table() if partition_name is empty, this means the database is just being initialized.
    if pd_partition_name != "":
        energy.db_conn()
        try:
            dropq = f"DROP TABLE {pd_partition_name};"
            energy.cursor.execute(dropq)
            energy.conn.commit()
            energy.cursor.close()
        except:
            energy.logger().error(f"Drop table failed! >:(")
        else:
            energy.logger().info(f"Table dropped: {pd_partition_name}")
    else:
        energy.logger().error("Partition_name not set. This must be the first time you're running this script against the initialized postgres instance and something went wrong in partition_table.py.")

# Create a database partition. Should execute at midnight every day.
def partition_table():
    energy.db_conn()
    start = datetime.now().replace(hour=0,minute=0,second=0).strftime('%Y-%m-%d %H:%M:%S')
    end = datetime.now().replace(hour=23,minute=59,second=59).strftime('%Y-%m-%d %H:%M:%S')
    try:
        tableq = f"CREATE TABLE {energy.partition_name()} PARTITION OF energydb FOR VALUES FROM ('{start}') TO ('{end}');"
        energy.cursor.execute(tableq)
        energy.conn.commit()
        energy.cursor.close()
    except:
        energy.logger().error(f"Something went wrong while creating a new table, best check partition_name in {settings.workdir}")
    else:
        energy.logger().info(f"New table created with name: {energy.partition_name()}")
        write_partition_name()

if __name__ == "__main__":
    process_daily_stats()
    drop_table()
    partition_table()
