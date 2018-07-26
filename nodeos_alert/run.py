import configparser
import dateutil.parser
import json
import logging
import requests
from time import sleep
from datetime import datetime, timedelta

from requests import ConnectionError

config = configparser.ConfigParser()
config.read("./config.ini")

nodes = config.get('DEFAULT', 'nodes').split(',')
checkevery = int(config.get('DEFAULT', 'checkevery'))
synctolerance = int(config.get('DEFAULT', 'synctolerance'))
log_level = config.get('logging', 'level')
log_name = config.get('logging', 'name')

logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger(log_name)

while True:
    for node in nodes:
        node = node.strip('/')

        try:
            response = requests.get(f"{node}/v1/chain/get_info")
        except ConnectionError as e:
            logger.error(f"REQUEST_FAILED - {node}, {str(e)}")
            break

        if response.status_code == 200:
            response = json.loads(response.text)

            head_block_time = dateutil.parser.parse(response['head_block_time'])

            utc_now = datetime.utcnow()
            if head_block_time > utc_now - timedelta(seconds=synctolerance):
                logger.info(f"IN_SYNC - {node}")
            else:
                logger.warning(f"OUT_OF_SYNC - {node}, delay:{utc_now-head_block_time} (synctolerance:{synctolerance}s)")
        else:
            logger.error(f"REQUEST_FAILED - {node}, {response.text}")

    sleep(checkevery)
