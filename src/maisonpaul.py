import argparse
import paho.mqtt.client as mqtt
import sqlite3
import requests
import json
import time
import threading
import os
import uuid

# Argument parsing management
parser = argparse.ArgumentParser(description='Python script authentication')
parser.add_argument('--mqttaddress', dest='mqttaddress', type=str, help='IP address of the MQTT broker')
parser.add_argument('--mqttusername', dest='mqttusername', type=str, help='Username to use for MQTT broker authentication')
parser.add_argument('--mqttpwd', dest='mqttpwd', type=str, help='Password to use for MQTT broker authentication')
parser.add_argument('--weatherappid', dest='weatherappid', type=str, help='App ID for OpenWeatherAPI authentication')
parser.add_argument('--weatherapplat', dest='weatherapplat', type=str, help='Latitude for the OpenWeatherAPI request')
parser.add_argument('--weatherapplon', dest='weatherapplon', type=str, help='Longitude for the OpenWeatherAPI request')

args = parser.parse_args()

# Client MQTT creation
client = mqtt.Client("MaisonPaul-backend-python")

# Connection to the MQTT broker
print("Connecting to the MQTT broker...")
client.username_pw_set(args.mqttusername, args.mqttpwd)
client.connect(args.mqttaddress, port=1883)
print("Connected!")

# Topic subscription
print("Subscribing to MQTT topics...")
client.subscribe("mainroom/heater1")
client.subscribe("mainroom/heater2")
client.subscribe("bedroom/heater")
client.subscribe("bedroom/heater-mode")
client.subscribe("watercloset/heater")
client.subscribe("watercloset/heater-mode")
client.subscribe("station1/temperature")
client.subscribe("station1/humidity")
client.subscribe("station2/temperature")
client.subscribe("station2/humidity")
client.subscribe("local-current-weather")
print("Subscription complete!")

# Connection to the SQLite3 database and creation of the tables if they don't exist
print("Initializing SQL database...")
# Chemin vers le répertoire contenant le fichier maisonpaul.db
db_directory = os.path.join(os.path.dirname(__file__), '..', 'db')
# Chemin complet vers le fichier maisonpaul.db
db_path = os.path.join(db_directory, 'maisonpaul.db')
# Connexion à la base de données
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS HumidityTable (id INTEGER PRIMARY KEY AUTOINCREMENT, sensorid VARCHAR(50), humidity REAL, date DATETIME)")
cursor.execute("CREATE TABLE IF NOT EXISTS TemperatureTable (id INTEGER PRIMARY KEY AUTOINCREMENT, sensorid VARCHAR(50), temperature REAL, date DATETIME)")
cursor.execute("CREATE TABLE IF NOT EXISTS ActuatorsTable (id INTEGER PRIMARY KEY AUTOINCREMENT, actuatorid VARCHAR(50), value REAL, action VARCHAR(50), date DATETIME)")
conn.close()
print("SQL database initialized!")

def AddEntryToActuatorsTable(actuatorid, value, action):
    print(f"New entry to actuators table : {actuatorid}, {value}, {action}")
    print("Connecting to database...")
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        sql_request = "INSERT INTO ActuatorsTable (actuatorid, value, action, date) VALUES (?, ?, ?, datetime('now'))"
        cursor.execute(sql_request, (actuatorid, value, action))
        print(f"SQL Request : {sql_request}")
        print("Executing SQL request...")
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn is not None:
            conn.close()
        print("Done!")

def AddEntryToTemperatureTable(sensorid, temperature):
    print(f"New entry to temperature table : {sensorid}, {temperature}")
    print("Connecting to database...")
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        sql_request = "INSERT INTO TemperatureTable (sensorid, temperature, date) VALUES (?, ?, datetime('now'))"
        cursor.execute(sql_request, (sensorid, temperature))
        print(f"SQL Request : {sql_request}")
        print("Executing SQL request...")
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn is not None:
            conn.close()
        print("Done!")

def AddEntryToHumidityTable(sensorid, humidity):
    print(f"New entry to humidity table : {sensorid}, {humidity}")
    print("Connecting to database...")
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        sql_request = "INSERT INTO HumidityTable (sensorid, humidity, date) VALUES (?, ?, datetime('now'))"
        cursor.execute(sql_request, (sensorid, humidity))
        print(f"SQL Request : {sql_request}")
        print("Executing SQL request...")
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn is not None:
            conn.close()
        print("Done!")

# Variable to store generated UUID
#request_id = None
 
# Callback fonction for received messages
def on_message(client, userdata, msg):
    print(str(msg.topic), " MQTT topic just got : ", str(msg.payload))

    if str(msg.topic) == "mainroom/heater1":
        AddEntryToActuatorsTable(str(msg.topic), msg.payload, "")
    elif str(msg.topic) == "mainroom/heater2":
        AddEntryToActuatorsTable(str(msg.topic), msg.payload, "")
    elif str(msg.topic) == "bedroom/heater":
        AddEntryToActuatorsTable(str(msg.topic), msg.payload, "")
    elif str(msg.topic) == "watercloset/heater":
        AddEntryToActuatorsTable(str(msg.topic), msg.payload, "")
    elif str(msg.topic) == "bedroom/heater-mode":
        AddEntryToActuatorsTable(str(msg.topic), 0, str(msg.payload, 'utf-8'))
    elif str(msg.topic) == "watercloset/heater-mode":
        AddEntryToActuatorsTable(str(msg.topic), 0, str(msg.payload, 'utf-8'))
    elif str(msg.topic) == "station1/temperature":
        AddEntryToTemperatureTable("station1", msg.payload)
    elif str(msg.topic) == "station1/humidity":
        AddEntryToHumidityTable("station1", msg.payload)
    elif str(msg.topic) == "station2/temperature":
        AddEntryToTemperatureTable("station2", msg.payload)
    elif str(msg.topic) == "station2/humidity":
        AddEntryToHumidityTable("station2", msg.payload)
    elif str(msg.topic) == "local-current-weather":
        weather_json = json.loads(str(msg.payload, 'utf-8'))
        AddEntryToTemperatureTable("outdoor", weather_json["main"]["temp"])
        AddEntryToHumidityTable("outdoor", weather_json["main"]["humidity"])
    else:
        print("MQTT topic not recognized")

# Registering callback function
client.on_message = on_message

# MQTT client loop
client.loop_start()

stop_thread = False

def background_request():
    global stop_thread
    while not stop_thread:
        # Définition l'URL de la requête
        url = "https://api.openweathermap.org/data/2.5/weather?lat="+args.weatherapplat+"&lon="+args.weatherapplon+"&appid="+args.weatherappid+"&units=metric&lang=fr"

        # Execution de la requête HTTP
        response = requests.get(url)

        # Vérification du succès de la requête
        if response.status_code == 200:
            # Chargez la réponse sous forme d'objet JSON
            response_txt = response.text
            print("(Thread) Received from HTTP request : {}".format(response_txt))
            print("(Thread) Publishing to local-current-weather MQTT topic...")
            client.publish("local-current-weather", response_txt, 2, True)
            print("(Thread) Done! (Going to sleep for 2 minutes)")
        else:
            print("(Thread) Failed HTTP request. Error code :", response.status_code)

        # 2 minutes d'attente avant de répéter la boucle
        for x in range(120):
            time.sleep(1)
            if stop_thread:
                break

# Création un thread de fond pour exécuter la fonction de requête en arrière-plan
thread = threading.Thread(target=background_request)

# Démarrage du thread
thread.start()

while not stop_thread:
    try:
        var = input()
    except KeyboardInterrupt:
        print("MAIN-LOOP : KeyboardInterrupt !")
        stop_thread = True

thread.join()

client.loop_stop()
client.disconnect()
