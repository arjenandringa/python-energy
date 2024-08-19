import stdlib
import settings
from partition_table import partition_name

# Python script to check and warn if current consumption is above threshold

threshold = 1.000

# Collect latest electricity usage
def collect_power_consumed():
    # Select query: Power Consumed
    pcq = f"SELECT value FROM {partition_name()} WHERE SENSOR = 'active_power_w' ORDER BY CREATED_AT DESC LIMIT 1;"
    power_consumed = stdlib.db_conn(pcq)
    return int([val[0] for val in power_consumed][0]) / 1000

# Send warning about consumption if current consumption exceeds threshold.
def warn():
    data = collect_power_consumed()
    if data > threshold:
        http_data = {"content": f"Geregistreerd actief verbruik: {data} KWh"}
        stdlib.post(settings.power_consumed, json=http_data)

if __name__ == "__main__":
    warn()

# TODO
# Evaluate if a warning has been sent out within the past 15 minutes. If so, ignore sending a warning.
# Set up Docker container rather than systemd services
