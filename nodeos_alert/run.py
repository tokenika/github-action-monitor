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

logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger(__name__)


while True:
    for node in nodes:
        node = node.strip('/')

        try:
            response = requests.get(f"{node}/v1/chain/get_info")
        except ConnectionError as e:
            logging.error(f"[failed] - {node}, {str(e)}")
            break

        if response.status_code == 200:
            response = json.loads(response.text)

            head_block_time = dateutil.parser.parse(response['head_block_time'])

            utc_now = datetime.utcnow()
            if head_block_time > utc_now - timedelta(seconds=synctolerance):
                logging.info(f"[in sync] - {node}")
            else:
                logging.warning(f"[out of sync] - {node}, delay:{utc_now-head_block_time} (synctolerance:{synctolerance}s)")
        else:
            logging.error(f"[failed] - {node}, {response.text}")

    sleep(checkevery)
