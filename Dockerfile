FROM python:3.9

RUN pip install paho-mqtt requests

WORKDIR /MaisonPaul

COPY ./production ./production

CMD ["python3.9", "./production/maisonpaul.py"]
