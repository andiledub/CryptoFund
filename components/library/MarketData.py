import asyncio
import websockets
import json
import os
import sys
import traceback
from decimal import Decimal
from collections import defaultdict
from multiprocessing import Pipe, Process
from time import sleep
import logging 

logger = logging.getLogger('LUNO_FEED_TRADEFEED')
logger = logging.basicConfig(level=logging.DEBUG, format= '%(asctime)s - %(levelname)s - %(message)s')

async def consumer(msg,pipe):
    if len(msg) > 2:
        pipe.send(msg)

async def producer():
    return json.dumps({
        'api_key_id': 'heauh4f78vajn',
        'api_key_secret': 'qkvSG6T01SDWPP7UsmRfMAuZI5gI8kkow_dC7tdZOtc'
    })

async def consumer_hadler(websocket, path, pipe):
    