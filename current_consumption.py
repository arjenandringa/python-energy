import stdlib
import settings
from partition_table import partition_name

# Python script to check and warn if current consumption is above threshold

threshold = 0.500

# Collect latest electricity usage
def collect_power_consumed():
    stdlib.db_conn()
    # Select query: Power Consumed
    pcq = f"SELECT value FROM {partition_name()} WHERE SENSOR = 'power_consumed' ORDER BY CREATED_AT DESC LIMIT 1;"
    stdlib.cursor.execute(pcq)
    stdlib.conn.commit()
    power_consumed = stdlib.cursor.fetchall()
    stdlib.cursor.close()
    return power_consumed[-1]

# Send warning about consumption if current consumption exceeds threshold.
def warn():
    data = collect_power_consumed()
    data = float(list(data)[-1])
    if data > threshold:
        http_data = {"content": f"Geregistreerd verbruik: {data} KWh"}
        stdlib.post(settings.warn_gas, json=http_data)

if __name__ == "__main__":
    warn()

# TODO
# Evaluate if a warning has been sent out within the past 15 minutes. If so, ignore sending a warning.
# Set up Docker container rather than systemd services
