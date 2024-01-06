from datetime import datetime
import logging
import sqlite3
import os
import time

# Logging management
logging.basicConfig(filename='migration.log',level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger("Test-logger")
logger.setLevel(logging.DEBUG)

# Chemin vers le répertoire contenant le fichier maisonpaul.db
db_directory = os.path.join(os.path.dirname(__file__), '..', 'db')

# Chemin complet vers le fichier maisonpaul.db
db_path = os.path.join(db_directory, 'maisonpaul.db')

# Création des tables de prod si jamais elles sont absentes
new_conn = sqlite3.connect(db_path)
new_cur = new_conn.cursor()
new_cur.execute("CREATE TABLE IF NOT EXISTS HumidityTable (id INTEGER PRIMARY KEY AUTOINCREMENT, sensorid VARCHAR(50), humidity REAL, date DATETIME)")
new_cur.execute("CREATE TABLE IF NOT EXISTS TemperatureTable (id INTEGER PRIMARY KEY AUTOINCREMENT, sensorid VARCHAR(50), temperature REAL, date DATETIME)")
new_cur.execute("CREATE TABLE IF NOT EXISTS ActuatorsTable (id INTEGER PRIMARY KEY AUTOINCREMENT, actuatorid VARCHAR(50), value REAL, action VARCHAR(50), date DATETIME)")
new_conn.close()

def execute_sql(sql, params):
    print("Connecting to database...")
    conn = None
    sqlRequestSucceeded = False
    numberOfTries = 0
    while sqlRequestSucceeded==False and numberOfTries<5:
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(sql, params)
            print(f"SQL Request : {sql}")
            print(f"SQL Parameters : {params}")
            print("Executing SQL request...")
            conn.commit()
            sqlRequestSucceeded = True
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            logger.error('An error occured executing SQL request: %s', e)
            numberOfTries += 1
        finally:
            if conn is not None:
                conn.close()
    if sqlRequestSucceeded==True:
        print("Done!")
    else:
        print("5 consecutive failed attemps, aborting")
        logger.critical("5 consecutive failed sql attemps, aborting")

def getFormattedTime(timestamp):
    # Conversion du timestamp en datetime
    dt_object = datetime.utcfromtimestamp(int(float(timestamp)))
    # Formatage de l'objet datetime pour l'afficher comme une chaîne de caractères
    formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_time

# Lecture des fichiers
def extract_TemperatureOrHumiditity_entries(file_path, nameid):
    with open(file_path, 'r') as f:
        for line in f:
            # split the line into timestamp and value
            timestamp, value = line.strip().split()

            # convert value to float
            value = float(value)

            # add entry to appropriate table
            if 'temp' in file_path:
                AddDatedEntryToTemperatureTable(timestamp, nameid, value)
            else:
                AddDatedEntryToHumidityTable(timestamp, nameid, value)
            time.sleep(0.1)
        print("File {} finished!".format(str(file_path)))

def extract_Actuators_entries(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            # Supprimer les espaces de début et de fin
            line = line.strip()

            # Diviser la ligne en deux parties : timestamp et le reste
            timestamp, rest = line.split(" ; ")

            # Diviser le reste en deux parties : id_actuator et action/number
            actuatorid, value = rest.split("=")

            if str(actuatorid) == "mainroom/heater1":
                AddDatedEntryToActuatorsTable(timestamp, actuatorid, value, "")
            elif str(actuatorid) == "mainroom/heater2":
                AddDatedEntryToActuatorsTable(timestamp, actuatorid, value, "")
            elif str(actuatorid) == "bedroom/heater":
                AddDatedEntryToActuatorsTable(timestamp, actuatorid, value, "")
            elif str(actuatorid) == "watercloset/heater":
                AddDatedEntryToActuatorsTable(timestamp, actuatorid, value, "")
            elif str(actuatorid) == "bedroom/heater-mode":
                AddDatedEntryToActuatorsTable(timestamp, actuatorid, 0, str(value))
            elif str(actuatorid) == "watercloset/heater-mode":
                AddDatedEntryToActuatorsTable(timestamp, actuatorid, 0, str(value))
            else:
                print("Unknown actuatorid : {}={}".format(str(actuatorid), str(value)))
            time.sleep(0.1)
        print("File {} finished!".format(str(file_path)))


# Fonctions d'écriture dans la base de données
def AddDatedEntryToTemperatureTable(timestamp, sensorid, temperature):
    print(f"New entry from {getFormattedTime(timestamp)} to temperature table : {sensorid}, {temperature}")
    sql = "INSERT INTO TemperatureTable (sensorid, temperature, date) VALUES (?, ?, datetime(?, 'unixepoch', 'UTC'))"
    params = (sensorid, temperature, timestamp)
    execute_sql(sql, params)

def AddDatedEntryToHumidityTable(timestamp, sensorid, humidity):
    print(f"New entry from {getFormattedTime(timestamp)} to humidity table : {sensorid}, {humidity}")
    sql = "INSERT INTO HumidityTable (sensorid, humidity, date) VALUES (?, ?, datetime(?, 'unixepoch', 'UTC'))"
    params = (sensorid, humidity, timestamp)
    execute_sql(sql, params)

def AddDatedEntryToActuatorsTable(timestamp, actuatorid, value, action):
    print(f"New entry from {getFormattedTime(timestamp)} to actuators table : {actuatorid}, {value}, {action}")
    sql = "INSERT INTO ActuatorsTable (actuatorid, value, action, date) VALUES (?, ?, ?, datetime(?, 'unixepoch', 'UTC'))"
    params = (actuatorid, value, action, timestamp)
    execute_sql(sql, params)

# ENTRY POINT
def main():
    olddbs_directory = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Temperatures-logs')
    
    # Fichier contenant tous les changements des infos radiateurs
    old_actuators = os.path.join(olddbs_directory, 'heat-controls-history.txt')

    # Noms des capteurs et leurs fichiers associés
    sensors = {
        "outdoor": ["temp-outdoor.txt", "humidity-outdoor.txt"],
        "station1": ["temp-station1.txt", "humidity-station1.txt"],
        "station2": ["temp-station2.txt", "humidity-station2.txt"],
        "station3": ["temp-station3.txt", "humidity-station3.txt"]
    }

    # # Exécution de la fonction pour les actuators
    # extract_Actuators_entries(old_actuators)

    # # Exécution des fonctions pour les capteurs
    # for sensor, files in sensors.items():
    #     for file in files:
    #         old_file = os.path.join(olddbs_directory, file)
    #         extract_TemperatureOrHumiditity_entries(old_file, sensor)
    
    logger.info('Starting job : humidity-station3.txt')

    old_file= os.path.join(olddbs_directory, "humidity-station3.txt")
    extract_TemperatureOrHumiditity_entries(old_file, "station3")

    logger.info('Job finished!')
    print('Job finished!')

    return


if __name__ == "__main__":
    main()
