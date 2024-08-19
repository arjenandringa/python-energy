import stdlib
import settings

# Collect last 15 minutes worth of gas usage
def collect_gas_consumed():
    # Select query: Gas Consumed (limit 30 as there are 2 inserts per minute)
    gcq = f"SELECT value FROM {settings.db} WHERE SENSOR = 'total_gas_m3' ORDER BY CREATED_AT DESC LIMIT 30;"
    # Store the results in a variable
    gas_consumed = stdlib.db_conn(gcq)
    # Perform list comprehension to pull the data out of the tuples
    gas_data = [x[0] for x in gas_consumed]
    return gas_data

# Collect last 15 minutes worth of electricity usage
def collect_power_consumed():
    tariff = stdlib.tariff()
    # Select query: stdlib Consumed {tariff}
    ecq = f"SELECT value FROM {settings.db} WHERE SENSOR = '{tariff}' ORDER BY CREATED_AT DESC LIMIT 30;"
    # Store the results in a variable
    power_consumed = stdlib.db_conn(ecq)
    # Perform list comprehension to pull the data out of the tuples
    power_data = [x[0] for x in power_consumed]
    return power_data

# Just subtract lowest value (last in list, 29 = 30th entry) from highest value (first in list, 0 = 1st entry)
# Round the numbers to 3 decimals, we work with thousands
def process_gas():
    gas_list = collect_gas_consumed()
    gas_consumed = round(float(gas_list[0])-float(gas_list[29]),3)
    return gas_consumed

def process_power():
    power_list = collect_power_consumed()
    energy_consumed = round(float(power_list[0]) - float(power_list[29]),3)
    return energy_consumed

def publish():
    http_data = {"content": f"{process_power()} KWh verbruikt in 15 minuten"}
    stdlib.post(settings.warn_power, json=http_data)
    http_data = {"content": f"{process_gas()} m3 verbruikt in 15 minuten"}
    stdlib.post(settings.warn_gas, json=http_data)

if __name__ == "__main__":
    publish()
