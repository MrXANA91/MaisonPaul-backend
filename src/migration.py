import datetime
import sqlite3
import os

from src.maisonpaul import AddEntryToHumidityTable, AddEntryToTemperatureTable

# Chemin vers le répertoire contenant le fichier maisonpaul.db
db_directory = os.path.join(os.path.dirname(__file__), '..', 'db')

# Chemin complet vers le fichier maisonpaul.db
db_path = os.path.join(db_directory, 'maisonpaul.db')

# Connexion à la base de données
new_conn = sqlite3.connect(db_path)
new_cur = new_conn.cursor()

# Table de test
new_cur.execute("CREATE TABLE IF NOT EXISTS TestHumidityTable (id INTEGER PRIMARY KEY AUTOINCREMENT, sensorid VARCHAR(10), humidity REAL, date DATETIME)")
new_cur.execute("CREATE TABLE IF NOT EXISTS TestTemperatureTable (id INTEGER PRIMARY KEY AUTOINCREMENT, sensorid VARCHAR(10), temperature REAL, date DATETIME)")
new_cur.execute("CREATE TABLE IF NOT EXISTS TestActuatorsTable (id INTEGER PRIMARY KEY AUTOINCREMENT, actuatorid VARCHAR(50), value REAL, action VARCHAR(50), date DATETIME)")

# Table de prod
#new_cur.execute("CREATE TABLE IF NOT EXISTS HumidityTable (id INTEGER PRIMARY KEY AUTOINCREMENT, sensorid VARCHAR(10), humidity REAL, date DATETIME)")
#new_cur.execute("CREATE TABLE IF NOT EXISTS TemperatureTable (id INTEGER PRIMARY KEY AUTOINCREMENT, sensorid VARCHAR(10), temperature REAL, date DATETIME)")
#new_cur.execute("CREATE TABLE IF NOT EXISTS ActuatorsTable (id INTEGER PRIMARY KEY AUTOINCREMENT, actuatorid VARCHAR(50), value REAL, action VARCHAR(50), date DATETIME)")

# Lecture des fichiers
def extract_entries(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            # split the line into timestamp and value
            timestamp, value = line.strip().split()

            # convert timestamp to datetime object
            timestamp = datetime.datetime.fromtimestamp(int(timestamp) / 1000)

            # convert value to float
            value = float(value)

            # add entry to appropriate table
            if 'temperature' in file_path:
                AddEntryToTemperatureTable(timestamp, value)
            else:
                AddEntryToHumidityTable(timestamp, value)