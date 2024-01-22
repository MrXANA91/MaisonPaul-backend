# MaisonPaul-backend
Python source for the backend program of the MaisonPaul application

## maisonpaul.py
Source code of the main Python backend program. It has to :
- Subscribe to all MQTT topics that are actualised by the sensors (temperature+humidity) and upon receiving, extract the data from the received payload and format it to store the extracted data into the SQL database
- Every 2 seconds, send a HTTP request to the OpenWeather API and send the JSON response to the corresponding MQTT topic

## migration.py
Script used to extract all the data stored in textfiles and send the extracted data to the SQL database <br/>
This script will be used to complete the migration from Node-RED to Python

# Installation
- Copy `src/maisonpaul.py` into a `production` folder at the root of this repo
- Create a `maisonpaul.db` SQLite3 file inside a `db` folder at the root of this repo
- Still at the root of this repo, launch using a Docker Compose file :

```yaml
version: '3.8'
services:
  maisonpaul-backend-app:
    build: .
    container_name: maisonpaul-backend-app
    restart: always
    environment:
      - MAISONPAULBACKEND_MQTT_HOST=host # replace with mqtt broker host address
      - MAISONPAULBACKEND_MQTT_PORT=1883 # leave default, or replace with configured port
      - MAISONPAULBACKEND_MQTT_CLIENT=MaisonPaul-backend-python # change to a unused client name
      - MAISONPAULBACKEND_MQTT_USER=user # replace with username
      - MAISONPAULBACKEND_MQTT_PASSWORD=password # replace with password
      
      - MAISONPAULBACKEND_OPENWEATHERAPI_APIKEY=APIKEY # replace with OpenWeatherAPI key
      - MAISONPAULBACKEND_OPENWEATHERAPI_LAT=LAT # replace with GPS Latitude
      - MAISONPAULBACKEND_OPENWEATHERAPI_LON=LON # replace with GPS Longitude
    volumes:
      - ./db:/MaisonPaul/db # replace with 

```

# Future
- The docker-compose will include the MQTT broker
- The docker-compose will include a database (MariaDB probably)