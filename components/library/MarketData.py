import asyncio
from datetime import datetime
import json
import logging
from os import name
import time
from collections import defaultdict
from decimal import Decimal
from typing import Sequence
from websocket import create_connection
import sys

async def connect():
    url = url = "wss://ws.luno.com/api/1/stream/XBTZAR"
    websoc = await websockets.connect(url)
    await websoc.send(json.dumps({
        'api_key_id': 'heauh4f78vajn',
        'api_key_secret': 'qkvSG6T01SDWPP7UsmRfMAuZI5gI8kkow_dC7tdZOtc'
    }))

    initial = await websoc.recv()
    initial_data = json.loads(initial)
    asks = {x['id']: [Decimal(x['price']), Decimal(x['volume'])] for x in initial_data['asks']}
    bids = {x['id']: [Decimal(x['price']), Decimal(x['volume'])] for x in initial_data['bids']}
    return asks


data = asyncio.run(connect())
print(data)



domain = "wss://api.valr.com/ws/trade"
api_feed = "MARKET_SUMMARY_UPDATE"
api_symbol = "BTCZAR"
api_data = '{"type":"SUBSCRIBE", "subscriptions": [{"event": "%(feed1)s","pairs": ["%(symbol)s"]}]}'\
        % {"feed1": api_feed, "symbol": api_symbol}
api_book = {"bids": {}, "asks": {}, "timestamp": {}}

def api_update_book(data, side, update_time):
    for x in data:
        price_level = x['price']
        size = float(x['quantity'])
        if size != 0.0:
            api_book[side].update({price_level : {'volume': size}})


if __name__=='__main__':
    try:
        ws = create_connection(domain)
        print("Connection Established ...")
    except Exception as error:
        print("WebSocket Connection failed (%s)" % error)
        ws.close()
        sys.exit(1)

    start_time = datetime.now()


    try:
        ws.send(api_data)
    except Exception as error:
        print("Feed subscription failed (%s)" % error)
        ws.close()
        sys.exit(1)


    ping = '{"type": "PING"}'
    while True:
        try:
            api_data = ws.recv()
        except KeyboardInterrupt:
            ws.close()
            sys.exit()
        except Exception as error:
            ws.close()
        print("RECEIVED")
        print(api_data)

        try:
            api_data = json.load(api_data)
        except Exception as ex:
            print(ex)
            continue

        #Order Count
        if isinstance(api_data.get("data"), dict):
            end_time = datetime.now()
            if (end_time - start_time).total_seconds() > 28:
                print("Sending PING")
                ws.send(ping)
                start_time = end_time

        
        if api_data.get("type") == api_feed:
            data = api_data.get("data")
            api_update_book(data["Bids"], "bids", data["LastChange"][:-1])
            api_update_book(data["Asks"], "asks", data["LastChange"][:-1])








