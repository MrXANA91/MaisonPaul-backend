# MaisonPaul-backend
Python source for the backend program of the MaisonPaul application

## maisonpaul.py
Source code of the main Python backend program. It has to :
- Subscribe to all MQTT topics that are actualised by the sensors (temperature+humidity) and upon receiving, extract the data from the received payload and format it to store the extracted data into the SQL database
- Every 2 seconds, send a HTTP request to the OpenWeather API and send the JSON response to the corresponding MQTT topic

## migration.py
Script used to extract all the data stored in textfiles and send the extracted data to the SQL database <br/>
This script will be used to complete the migration from Node-RED to Python
