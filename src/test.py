import os
import sqlite3

# Chemin vers le répertoire contenant le fichier maisonpaul.db
db_directory = os.path.join(os.path.dirname(__file__), '..', 'db')

# Chemin complet vers le fichier maisonpaul.db
db_path = os.path.join(db_directory, 'maisonpaul.db')

# Connexion à la base de données
new_conn = sqlite3.connect(db_path)
new_cur = new_conn.cursor()
res = new_cur.execute("SELECT * FROM ActuatorsTable")
print(res.fetchall())
res = new_cur.execute("SELECT * FROM TemperatureTable")
print(res.fetchall())
res = new_cur.execute("SELECT * FROM HumidityTable")
print(res.fetchall())
res = new_cur.execute("SELECT temperature, date FROM TemperatureTable WHERE sensorid = 'station1/temperature'")
print(res.fetchall())
res = new_cur.execute("SELECT actuatorid, value, action, date FROM ActuatorsTable WHERE actuatorid = 'mainroom/heater1' OR actuatorid = 'mainroom/heater2'")
print(res.fetchall())

# new_cur.execute("DROP TABLE ActuatorsTable")
# new_cur.execute("DROP TABLE TemperatureTable")
# new_cur.execute("DROP TABLE HumidityTable")
print("Done!")