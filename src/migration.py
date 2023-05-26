import sqlite3
import os
import threading

# Chemin vers le répertoire contenant le fichier maisonpaul.db
db_directory = os.path.join(os.path.dirname(__file__), '..', 'db')

# Chemin complet vers le fichier maisonpaul.db
db_path = os.path.join(db_directory, 'maisonpaul.db')

# Connexion à la base de données
new_conn = sqlite3.connect(db_path)
new_cur = new_conn.cursor()

# Table de prod
new_cur.execute("CREATE TABLE IF NOT EXISTS HumidityTable (id INTEGER PRIMARY KEY AUTOINCREMENT, sensorid VARCHAR(50), humidity REAL, date DATETIME)")
new_cur.execute("CREATE TABLE IF NOT EXISTS TemperatureTable (id INTEGER PRIMARY KEY AUTOINCREMENT, sensorid VARCHAR(50), temperature REAL, date DATETIME)")
new_cur.execute("CREATE TABLE IF NOT EXISTS ActuatorsTable (id INTEGER PRIMARY KEY AUTOINCREMENT, actuatorid VARCHAR(50), value REAL, action VARCHAR(50), date DATETIME)")

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
                AddDatedEntryToActuatorsTable(timestamp, actuatorid, 0, str(value, 'utf-8'))
            elif str(actuatorid) == "watercloset/heater-mode":
                AddDatedEntryToActuatorsTable(timestamp, actuatorid, 0, str(value, 'utf-8'))
            else:
                print("Unknown actuatorid : {}={}".format(str(actuatorid), str(value)))
        print("File {} finished!".format(str(file_path)))


# Fonctions d'écriture dans la base de données
def AddDatedEntryToTemperatureTable(timestamp, sensorid, temperature):
    print(f"New entry to temperature table : {sensorid}, {temperature}")
    print("Connecting to database...")
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        sql_request = "INSERT INTO TemperatureTable (sensorid, temperature, date) VALUES (?, ?, datetime(?, 'unixepoch'))"
        cursor.execute(sql_request, (sensorid, temperature, timestamp))
        print(f"SQL Request : {sql_request}")
        print("Executing SQL request...")
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn is not None:
            conn.close()
        print("Done!")


def AddDatedEntryToHumidityTable(timestamp, sensorid, humidity):
    print(f"New entry to humidity table : {sensorid}, {humidity}")
    print("Connecting to database...")
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        sql_request = "INSERT INTO HumidityTable (sensorid, humidity, date) VALUES (?, ?, datetime(?, 'unixepoch'))"
        cursor.execute(sql_request, (sensorid, humidity, timestamp))
        print(f"SQL Request : {sql_request}")
        print("Executing SQL request...")
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn is not None:
            conn.close()
        print("Done!")

def AddDatedEntryToActuatorsTable(timestamp, actuatorid, value, action):
    print(f"New entry to actuators table : {actuatorid}, {value}, {action}")
    print("Connecting to database...")
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        sql_request = "INSERT INTO ActuatorsTable (actuatorid, value, action, date) VALUES (?, ?, ?, datetime(?, 'unixepoch'))"
        cursor.execute(sql_request, (actuatorid, value, action, timestamp))
        print(f"SQL Request : {sql_request}")
        print("Executing SQL request...")
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn is not None:
            conn.close()
        print("Done!")

# ENTRY POINT
def main():
    olddbs_directory = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Temperatures-logs')
    
    # Fichier contenant tous les changements des infos radiateurs
    old_actuators = os.path.join(olddbs_directory, 'heat-controls-history.txt')

    # Fichiers contenant les informations de température et d'humidité extérieure
    old_outdoor_temperature = os.path.join(olddbs_directory, 'temp-outdoor.txt')
    old_outdoor_humidity = os.path.join(olddbs_directory, 'humidity-outdoor.txt')

    # Fichiers contenant les informations de température et d'humidité dans la pièce principale
    old_station1_temperature = os.path.join(olddbs_directory, 'temp-station1.txt')
    old_station1_humidity = os.path.join(olddbs_directory, 'humidity-station1.txt')

    # Fichiers contenant les informations de température et d'humidité dans la chambre
    old_station2_temperature = os.path.join(olddbs_directory, 'temp-station2.txt')
    old_station2_humidity = os.path.join(olddbs_directory, 'humidity-station2.txt')

    # Fichiers contenant les informations de température et d'humidité dans la salle de bain (pas utilisée)
    old_station3_temperature = os.path.join(olddbs_directory, 'temp-station3.txt')
    old_station3_humidity = os.path.join(olddbs_directory, 'humidity-station3.txt')

    # Noms des capteurs
    outdoor_sensorid = "outdoor"
    station1_sensorid = "station1"
    station2_sensorid = "station2"
    station3_sensorid = "station3"

    # Construction des threads
    thread_actuators = threading.Thread(target=extract_Actuators_entries, args=(old_actuators))
    thread_outdoor_temp = threading.Thread(target=extract_TemperatureOrHumiditity_entries, args=(old_outdoor_temperature, outdoor_sensorid))
    thread_outdoor_humid = threading.Thread(target=extract_TemperatureOrHumiditity_entries, args=(old_outdoor_humidity, outdoor_sensorid))
    thread_station1_temp = threading.Thread(target=extract_TemperatureOrHumiditity_entries, args=(old_station1_temperature, station1_sensorid))
    thread_station1_humid = threading.Thread(target=extract_TemperatureOrHumiditity_entries, args=(old_station1_humidity, station1_sensorid))
    thread_station2_temp = threading.Thread(target=extract_TemperatureOrHumiditity_entries, args=(old_station2_temperature, station2_sensorid))
    thread_station2_humid = threading.Thread(target=extract_TemperatureOrHumiditity_entries, args=(old_station2_humidity, station2_sensorid))
    thread_station3_temp = threading.Thread(target=extract_TemperatureOrHumiditity_entries, args=(old_station3_temperature, station3_sensorid))
    thread_station3_humid = threading.Thread(target=extract_TemperatureOrHumiditity_entries, args=(old_station3_humidity, station3_sensorid))

    # Lancement de tous les threads
    thread_actuators.start()
    thread_outdoor_temp.start()
    thread_outdoor_humid.start()
    thread_station1_temp.start()
    thread_station1_humid.start()
    thread_station2_temp.start()
    thread_station2_humid.start()
    thread_station3_temp.start()
    thread_station3_humid.start()

    # Attente que les threads aient terminé
    thread_actuators.join()
    thread_outdoor_temp.join()
    thread_outdoor_humid.join()
    thread_station1_temp.join()
    thread_station1_humid.join()
    thread_station2_temp.join()
    thread_station2_humid.join()
    thread_station3_temp.join()
    thread_station3_humid.join()

    return

if __name__ == "__main__":
    main()
