import argparse
import paho.mqtt.client as mqtt
import sqlite3
import requests
import json
import time
import threading
import os
import uuid
import time
from datetime import datetime
import logging

# VERSION
VERSION_MAJOR = 0
VERSION_MINOR = 2
VERSION_PATCH = 0

# Environment variables retrieval
mqttaddress = os.environ.get('MAISONPAULBACKEND_MQTT_HOST')
mqttport = os.environ.get('MAISONPAULBACKEND_MQTT_PORT')
mqttclientname = os.environ.get('MAISONPAULBACKEND_MQTT_CLIENT')
mqttusername = os.environ.get('MAISONPAULBACKEND_MQTT_USER')
mqttpwd = os.environ.get('MAISONPAULBACKEND_MQTT_PASSWORD')

weatherappid = os.environ.get('MAISONPAULBACKEND_OPENWEATHERAPI_APIKEY')
weatherapplat = os.environ.get('MAISONPAULBACKEND_OPENWEATHERAPI_LAT')
weatherapplon = os.environ.get('MAISONPAULBACKEND_OPENWEATHERAPI_LON')

def checkEnvVar():
    if (mqttaddress == None): exit(1)
    if (mqttport == None): exit(2)
    if (mqttclientname == None): exit(3)
    if (mqttusername == None): exit(4)
    if (mqttpwd == None): exit(5)
    if (weatherappid == None): exit(6)
    if (weatherapplat == None): exit(7)
    if (weatherapplon == None): exit(8)

# Logging management
logging.basicConfig(filename='maisonpaul.log',level=logging.WARNING,
                    format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger("MaisonPaul-logger")
logger.setLevel(logging.WARNING)

# Chemin vers le répertoire contenant le fichier maisonpaul.db
db_directory = os.path.join(os.path.dirname(__file__), '..', 'db')
# Chemin complet vers le fichier maisonpaul.db
db_path = os.path.join(db_directory, 'maisonpaul.db')

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
            logger.debug('Executing SQL request : %s with parameters %s', sql, params)
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

def AddEntryToActuatorsTable(actuatorid, value, action):
    print(f"New entry from {getFormattedTime(time.time())} to actuators table : {actuatorid}, {value}, {action}")
    sql = "INSERT INTO ActuatorsTable (actuatorid, value, action, date) VALUES (?, ?, ?, datetime('now'))"
    params = (actuatorid, value, action)
    execute_sql(sql, params)

def AddEntryToTemperatureTable(sensorid, temperature):
    print(f"New entry from {getFormattedTime(time.time())} to temperature table : {sensorid}, {temperature}")
    sql = "INSERT INTO TemperatureTable (sensorid, temperature, date) VALUES (?, ?, datetime('now'))"
    params = (sensorid, temperature)
    execute_sql(sql, params)

def AddEntryToHumidityTable(sensorid, humidity):
    print(f"New entry from {getFormattedTime(time.time())} to humidity table : {sensorid}, {humidity}")
    sql = "INSERT INTO HumidityTable (sensorid, humidity, date) VALUES (?, ?, datetime('now'))"
    params = (sensorid, humidity)
    execute_sql(sql, params)

# Variable to store generated UUID
#request_id = None
 
# Callback fonction for received messages
def on_message(client, userdata, msg):
    print(str(msg.topic), " MQTT topic just got : ", str(msg.payload))
    logger.debug('Message received on topic %s : %s', str(msg.topic), str(msg.payload))

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

stop_thread = False
def background_request():
    global stop_thread
    global logger
    while not stop_thread:
        # Définition l'URL de la requête
        url = "https://api.openweathermap.org/data/2.5/weather?lat="+weatherapplat+"&lon="+weatherapplon+"&appid="+weatherappid+"&units=metric&lang=fr"

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
            logger.info('Published into local-current-weather')
        else:
            print("(Thread) Failed HTTP request. Error code :", response.status_code)
            logger.error('An error occured with HTTP request. Error code : %d', response.status_code)

        # 2 minutes d'attente avant de répéter la boucle
        for x in range(120):
            time.sleep(1)
            if stop_thread:
                break

if __name__ == "__main__":
    # Intro
    logger.info(f'MaisonPaul-backend - starting up version {VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}')
    print('================================')
    print('====== MaisonPaul-backend ======')
    print('================================')
    print(f'Version {VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}')

    checkEnvVar()

    # Connection to the SQLite3 database and creation of the tables if they don't exist
    print("Initializing SQL database...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS HumidityTable (id INTEGER PRIMARY KEY AUTOINCREMENT, sensorid VARCHAR(50), humidity REAL, date DATETIME)")
        cursor.execute("CREATE TABLE IF NOT EXISTS TemperatureTable (id INTEGER PRIMARY KEY AUTOINCREMENT, sensorid VARCHAR(50), temperature REAL, date DATETIME)")
        cursor.execute("CREATE TABLE IF NOT EXISTS ActuatorsTable (id INTEGER PRIMARY KEY AUTOINCREMENT, actuatorid VARCHAR(50), value REAL, action VARCHAR(50), date DATETIME)")
        conn.close()
        print("SQL database initialized!")
        logger.info('SQL database initialized!')
    except sqlite3.Error as e:
        print(f"An error occured: {e}")
        logger.error('An error occured executing SQL request: %s', e)
    finally:
        if conn is not None:
            conn.close()
    
    # Client MQTT creation
    client = mqtt.Client(mqttclientname)

    # Connection to the MQTT broker
    print("Connecting to the MQTT broker...")
    client.username_pw_set(mqttusername, mqttpwd)
    
    while True:
        try:
            client.connect(mqttaddress, int(mqttport))
            print("Connected!")
            logger.info('Connected to the MQTT broker')
            break  # Si la connexion réussit, on sort de la boucle
        except Exception as e:
            print("Failed to connect to MQTT broker, trying again in 5 seconds...")
            logger.error('Failed to connect to MQTT broker (trying again in 5 seconds) : %s', e)
            time.sleep(5)  # Attend 5 secondes avant de réessayer

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

    # Registering callback function
    client.on_message = on_message

    # MQTT client loop
    client.loop_start()

    # Création un thread de fond pour exécuter la fonction de requête en arrière-plan
    thread = threading.Thread(target=background_request)

    # Démarrage du thread
    thread.start()

    # # TODO : ne fonctionne plus depuis le passage sous Docker
    # while not stop_thread:
    #     try:
    #         var = input().lower()
    #         if var.startswith('get level') == True:
    #             print(f"Logging level = {logging.getLevelName}")
    #         elif var.startswith('set level debug') == True:
    #             print(f"Logging level set to DEBUG")
    #             logger.setLevel(logging.DEBUG)
    #         elif var.startswith('set level info') == True:
    #             print(f"Logging level set to INFO")
    #             logger.setLevel(logging.INFO)
    #         elif var.startswith('set level warning') == True:
    #             print(f"Logging level set to WARNING")
    #             logger.setLevel(logging.WARNING)
    #         elif var.startswith('set level error') == True:
    #             print(f"Logging level set to ERROR")
    #             logger.setLevel(logging.ERROR)
    #         elif var.startswith('set level critical') == True:
    #             print(f"Logging level set to CRITICAL")
    #             logger.setLevel(logging.CRITICAL)
    #         else:
    #             print("Unknown command")
    #     except KeyboardInterrupt:
    #         print("MAIN-LOOP : KeyboardInterrupt !")
    #         stop_thread = True

    # thread.join()

    # client.loop_stop()
    # client.disconnect()

    # logger.info('Program terminated')