import stdlib
import energy
import publish_qh
import current_consumption
import partition_table

stdlib.scheduler.add_job(energy.process_energy_vars(),'interval',seconds=30,id='insertjob')
stdlib.scheduler.add_job(current_consumption.warn(),'interval',seconds=30,id='infojob')
stdlib.scheduler.add_job(publish_qh.publish(),'interval',minutes=1,id='warningjob')
stdlib.scheduler.add_job(partition_table.process_daily_stats(),'cron',hour=0,minute=0,second=5,id='process-the-day')
stdlib.scheduler.add_job(partition_table.drop_table(),'cron',hour=0,minute=0,second=15,id='drop-table')
stdlib.scheduler.add_job(partition_table.partition_table(),'cron',hour=0,minute=0,second=20,id='partition-table')
stdlib.scheduler.start()