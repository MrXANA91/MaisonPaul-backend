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

# Environment variables retrieval
mqttaddress = os.environ.get('MAISONPAULBACKEND_MQTT_HOST')
mqttport = os.environ.get('MAISONPAULBACKEND_MQTT_PORT')
mqttclientname = os.environ.get('MAISONPAULBACKEND_MQTT_CLIENT')
mqttusername = os.environ.get('MAISONPAULBACKEND_MQTT_USER')
mqttpwd = os.environ.get('MAISONPAULBACKEND_MQTT_PASSWORD')

# weatherappid = os.environ.get('MAISONPAULBACKEND_OPENWEATHERAPI_APIKEY')
# weatherapplat = os.environ.get('MAISONPAULBACKEND_OPENWEATHERAPI_LAT')
# weatherapplon = os.environ.get('MAISONPAULBACKEND_OPENWEATHERAPI_LON')

def checkEnvVar():
    if (mqttaddress == None): exit(1)
    if (mqttport == None): exit(2)
    if (mqttclientname == None): exit(3)
    if (mqttusername == None): exit(4)
    if (mqttpwd == None): exit(5)
    # if (weatherappid == None): exit(6)
    # if (weatherapplat == None): exit(7)
    # if (weatherapplon == None): exit(8)

def on_message(client, userdata, msg):
    print(str(msg.topic), " MQTT topic just got : ", str(msg.payload))

# # Logging management
# logging.basicConfig(filename='test.log',level=logging.ERROR,
#                     format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
# logger = logging.getLogger("Test-logger")
# logger.setLevel(logging.ERROR)

# # Chemin vers le répertoire contenant le fichier maisonpaul.db
# db_directory = os.path.join(os.path.dirname(__file__), '..', 'db')

# # Chemin complet vers le fichier maisonpaul.db
# db_path = os.path.join(db_directory, 'maisonpaul.db')

# # Connexion à la base de données
# new_conn = sqlite3.connect(db_path)
# new_cur = new_conn.cursor()
# new_cur.execute("CREATE TABLE IF NOT EXISTS HumidityTable (id INTEGER PRIMARY KEY AUTOINCREMENT, sensorid VARCHAR(50), humidity REAL, date DATETIME)")
# new_cur.execute("CREATE TABLE IF NOT EXISTS TemperatureTable (id INTEGER PRIMARY KEY AUTOINCREMENT, sensorid VARCHAR(50), temperature REAL, date DATETIME)")
# new_cur.execute("CREATE TABLE IF NOT EXISTS ActuatorsTable (id INTEGER PRIMARY KEY AUTOINCREMENT, actuatorid VARCHAR(50), value REAL, action VARCHAR(50), date DATETIME)")
# print("SQL database initialized!")

# new_cur.execute("""
# SELECT date, temperature FROM TemperatureTable
# WHERE sensorid = 'station1' AND date >= datetime('now', '-6 months')
# """)
# rows = new_cur.fetchall()
# new_conn.close()

# for row in rows:
#     print("Date: ", row[0], " Temperature: ", row[1])

# Client MQTT creation
client = mqtt.Client("MaisonPaul-backend-python")

# Connection to the MQTT broker
print("Connecting to the MQTT broker...")
client.username_pw_set(mqttusername, mqttpwd)

while True:
    try:
        client.connect(mqttaddress, int(mqttport))
        print("Connected!")
        break  # Si la connexion réussit, on sort de la boucle
    except Exception as e:
        print("Failed to connect to MQTT broker, trying again in 5 seconds...")
        time.sleep(5)  # Attend 5 secondes avant de réessayer

# Topic subscription
print("Subscribing to MQTT topics...")
client.subscribe("testTopic")
print("Subscription complete!")

# Registering callback function
client.on_message = on_message

# MQTT client loop
client.loop_forever()

# def getFormattedTime(timestamp):
#     # Conversion du timestamp en datetime
#     dt_object = datetime.utcfromtimestamp(int(float(timestamp)))
#     # Formatage de l'objet datetime pour l'afficher comme une chaîne de caractères
#     formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
#     return formatted_time

# def execute_sql(sql, params):
#     print("Connecting to database...")
#     conn = None
#     sqlRequestSucceeded = False
#     numberOfTries = 0
#     while sqlRequestSucceeded==False and numberOfTries<5:
#         try:
#             conn = sqlite3.connect(db_path)
#             cursor = conn.cursor()
#             cursor.execute(sql, params)
#             print(f"SQL Request : {sql}")
#             print(f"SQL Parameters : {params}")
#             print("Executing SQL request...")
#             conn.commit()
#             sqlRequestSucceeded = True
#         except sqlite3.Error as e:
#             print(f"An error occurred: {e}")
#             logger.error('An error occured executing SQL request: %s', e)
#             numberOfTries += 1
#         finally:
#             if conn is not None:
#                 conn.close()
#     if sqlRequestSucceeded==True:
#         print("Done!")
#     else:
#         print("5 consecutive failed attemps, aborting")
#         logger.critical("5 consecutive failed sql attemps, aborting")

# def AddEntryToTemperatureTable(sensorid, temperature):
#     print(f"New entry from {getFormattedTime(time.time())} to temperature table : {sensorid}, {temperature}")
#     sql = "INSERT INTO TemperatureTable (sensorid, temperature, date) VALUES (?, ?, datetime('now'))"
#     params = (sensorid, temperature)
#     execute_sql(sql, params)

# stop_thread = False
# def background_thread():
#     global stop_thread
#     while not stop_thread:
#         AddEntryToTemperatureTable('testsensor', 15.0)

#         # 15 secondes d'attente avant de répéter la boucle
#         for x in range(15):
#             time.sleep(1)
#             if stop_thread:
#                 break

# # Création un thread de fond pour exécuter la fonction de requête en arrière-plan
# thread = threading.Thread(target=background_thread)

# # Démarrage du thread
# thread.start()

# while not stop_thread:
#     print("Press escape combo Ctrl+C to exit.")
#     try:
#         var = input().lower()
#         if var.startswith('get level') == True:
#             print(f"Logging level = {logging.getLevelName(logger.level)}")
#         else:
#             print("Unknown command")
#     except KeyboardInterrupt:
#         print("MAIN-LOOP : KeyboardInterrupt !")
#         stop_thread = True

# thread.join()

# client.disconnect()

# new_cur.execute("DROP TABLE ActuatorsTable")
# new_cur.execute("DROP TABLE TemperatureTable")
# new_cur.execute("DROP TABLE HumidityTable")
# print("Done!")