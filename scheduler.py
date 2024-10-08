import stdlib
import settings
import energy
import publish_qh
import current_consumption
import partition_table
import os
import time

# Configure time to local timezone
os.environ['TZ'] = settings.timezone
time.tzset()

# Configure APScheduler to use the same timezone
stdlib.scheduler.configure(timezone=settings.timezone)

# Init run -- Drops an error in Postgres log if table already exists, which is fine
partition_table.partition_table()

# Add all jobs with respective intervals or cron settings
stdlib.scheduler.add_job(energy.process_energy_vars,'interval',seconds=30,id='insertjob')
stdlib.scheduler.add_job(current_consumption.warn,'interval',seconds=30,id='infojob')
stdlib.scheduler.add_job(publish_qh.publish,'interval',minutes=15,id='warningjob')
stdlib.scheduler.add_job(partition_table.process_daily_stats,'cron',hour=0,minute=0,second=5,id='process-the-day')
stdlib.scheduler.add_job(partition_table.drop_table,'cron',hour=0,minute=0,second=15,id='drop-table')
stdlib.scheduler.add_job(partition_table.partition_table,'cron',hour=0,minute=0,second=20,id='partition-table')
stdlib.scheduler.start()
