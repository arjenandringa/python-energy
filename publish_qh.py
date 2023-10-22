import stdlib
import settings

# Collect last 15 minutes worth of gas usage
def collect_gas_consumed():
    stdlib.db_conn()
    # Select query: Gas Consumed (limit 30 as there are 2 inserts per minute)
    gcq = f"SELECT value FROM {settings.db} WHERE SENSOR = 'gas_consumed' ORDER BY CREATED_AT DESC LIMIT 30;"
    stdlib.cursor.execute(gcq)
    stdlib.conn.commit()
    # Store the results in a variable
    gas_consumed = stdlib.cursor.fetchall()
    stdlib.cursor.close()
    # Perform list comprehension to pull the data out of the tuples
    gas_data = [x[0] for x in gas_consumed]
    return gas_data

# Collect last 15 minutes worth of electricity usage
def collect_power_consumed():
    stdlib.db_conn()
    tariff = stdlib.tariff()
    # Select query: stdlib Consumed {tariff}
    ecq = f"SELECT value FROM {settings.db} WHERE SENSOR = '{tariff}' ORDER BY CREATED_AT DESC LIMIT 30;"
    stdlib.cursor.execute(ecq)
    stdlib.conn.commit()
    # Store the results in a variable
    power_consumed = stdlib.cursor.fetchall()
    stdlib.cursor.close()
    # Perform list comprehension to pull the data out of the tuples
    power_data = [x[0] for x in power_consumed]
    return power_data

# Just subtract lowest value (last in list, 29 = 30th entry) from highest value (first in list, 0 = 1st entry)
# Round the numbers to 3 decimals, we work with thousands
def process_gas():
    gas_list = collect_gas_consumed()
    gas_consumed = round(float(gas_list[0])-float(gas_list[29]),3)
    # Write gas down, we don't need to be updated when gas usage is 0.0 (which it is, most of the time)
    with open('gas_consumed','w+',encoding='utf-8') as f:
        f.write(str(gas_consumed))
    return gas_consumed

def process_power():
    power_list = collect_power_consumed()
    energy_consumed = round(float(power_list[0]) - float(power_list[29]),3)
    return energy_consumed

def publish():
    http_data = {"content": f"{process_power()} KWh verbruikt in 15 minuten"}
    stdlib.post(settings.warn_power, json=http_data)
    with open(f'{settings.workdir}/gas_consumed','r',encoding='utf-8') as f:
        gc = f.read()
    # Convert process_gas() value to string, because gc is also of class string
    if gc != str(process_gas()):
        http_data = {"content": f"{process_gas()} m3 verbruikt in 15 minuten"}
        stdlib.post(settings.warn_gas, json=http_data)

if __name__ == "__main__":
    publish()
