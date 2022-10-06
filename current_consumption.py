import requests
import energy
import settings

# Python script to check and warn if current consumption is above 1KWh

# Collect latest electricity usage
def collect_power_consumed():
    energy.db_conn()
    # Select query: Power Consumed
    pcq = f"SELECT value FROM {energy.partition_name()} WHERE SENSOR = 'power_consumed' ORDER BY CREATED_AT DESC LIMIT 1;"
    energy.cursor.execute(pcq)
    energy.conn.commit()
    power_consumed = energy.cursor.fetchall()
    energy.cursor.close()
    return power_consumed[-1]

# Send warning about consumption if current consumption 1KWh or higher.
def warn():
    data = collect_power_consumed()
    data = float(list(data)[-1])
    if data > 0.500:
        headers = {"Content-Type": "application/json"}
        http_data = {"content": f"Geregistreerd verbruik: {data} KWh"}
        requests.post(settings.power_consumed, json=http_data, headers=headers)

if __name__ == "__main__":
    warn()

# TODO
# Evaluate if a warning has been sent out within the past 15 minutes. If so, ignore sending a warning.
# Set up Docker container rather than systemd services
