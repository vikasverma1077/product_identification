import os
import redis
import raven
import sys
import ConfigParser
from pydisque.client import Client

config_parser = ConfigParser.RawConfigParser()
curr_dir = os.path.abspath(os.path.dirname(__file__))
config_parser.read(curr_dir + '/queues.conf')

## For sentry settings
sentry_client = raven.Client(
    #dsn = 'https://f65cb67d524443d2b8f9f53d3da0b3fd:5c6cb4e0d70d41efa9f77a585ade3dad@app.getsentry.com/48657'
    dsn = 'https://12bc0e7f582c48069090c5c876b923cf:7e13376d29fd4e81a5b585380729537b@app.getsentry.com/51526'
)

## for redis configuration
config = {
    #'host': 'd1-redis-addfix.iqi3ba.ng.0001.apse1.cache.amazonaws.com',
    #'host': 'data-prod-redis-002.iqi3ba.0001.apse1.cache.amazonaws.com',
    'host': 'localhost',
    'port':6379,
    'db':0,
}

#for redis connection
r = redis.Redis(**config)
if not r.ping():
    sentry_client.captureException(
        message = "settings.py: Failed to connect to redis",
        extra = {"error" : 'ping failed'})
    sys.exit()

## for disque connection
client = Client(["127.0.0.1:7711"])
#client = Client(["10.0.4.232:7711"])

try:
    client.connect()
except Exception as disque_err:
    sentry_client.captureException(message = "settings.py:Failed to connect to disque",
                                   extra={"error" : disque_err})
    sys.exit()

catfight_input = config_parser.get("Queues","catfight_input")
catfight_output = config_parser.get("Queues","catfight_output")

