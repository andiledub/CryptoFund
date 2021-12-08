import asyncio
import json
import logging
from datetime import datetime
from os import name 
from collections import defaultdict
from decimal import Decimal
import time
from websocket import create_connection
import sys

logging.basicConfig(level=logging.DEBUG, format = '%(asctime)s - %(levelname)s - %(message)s')


class MarketData:
    def __init__(self, source,ticker, api_key=None, api_secret=None) -> None:
        self.ticker = ticker.upper()
        self.source = source.upper()
        self.api_key = api_key
        self.api_secret = api_secret
        self.sequence = None
        self.bid = {}
        self.ask = {}
        self.api_book = {"bids": {}, "asks": {}, "timestamp": {}}
        self.api_feed = "MARKET_SUMMARY_UPDATE"
        self.websocket = None

    def urlSwitcher(self):
        switcher = {
            'LUNO': "wss://ws.luno.com/api/1/stream/" + self.ticker,
            'VALR': "wss://api.valr.com/ws/trade"
        }
        if self.source in switcher:
            return switcher.get(self.source)
        else:
            logging.error("Invalid Market Data Source")
            sys.exit(1)
    
    def messageHandler(self):
        api_feed = "AGGREGATED_ORDERBOOK_UPDATE"
        switcher = {
            'LUNO': json.dumps({
                                'api_key_id': 'heauh4f78vajn',
                                'api_key_secret': 'qkvSG6T01SDWPP7UsmRfMAuZI5gI8kkow_dC7tdZOtc'}),
            'VALR': '{"type":"SUBSCRIBE", "subscriptions": [{"event": "%(feed1)s","pairs": ["%(symbol)s"]}]}'\
                        % {"feed1": api_feed, "symbol": self.ticker}
        }

        return switcher.get(self.source, "Invalid Market Data Source")
    
    def api_update_book(self,data, side, update_time):
        for x in data:
            price_level = x['price']
            size = float(x['quantity'])
            if size != 0.0:
                self.api_book[side].update({price_level : {'volume': size}})

    def connect(self):
        try:
            self.websocket = create_connection(self.urlSwitcher())
            logging.info("Connection Established ...")
        except Exception as error:
            logging.error("WebSocket Connection failed (%s)" % error)
            self.websocket.close()
            sys.exit(1)
        
        start_time = datetime.now()

        try:
            self.websocket.send(self.messageHandler())
            logging.info("Feed Subcription (%s)" % self.messageHandler())
        except Exception as error:
            logging.error("Feed subscription failed (%s)" % error)
            self.websocket.close()
            sys.exit(1)


        ping = '{"type": "PING"}'
        while True:
            try:
                api_data = self.websocket.recv()
            except KeyboardInterrupt:
                self.websocket.close()
                sys.exit()
            except Exception as error:
                self.websocket.close()
            logging.info(api_data)
            

            try:
                api_data = json.load(api_data)
            except Exception as ex:
                #logging.error(ex)
                continue

            #Order Count
            if isinstance(api_data.get("data"), dict):
                end_time = datetime.now()
                if (end_time - start_time).total_seconds() > 28:
                    logging.info("Sending PING")
                    #self.websocket.send(ping)
                    start_time = end_time
            
            if api_data.get("type") == self.api_feed:
                data = api_data.get("data")
                self.api_update_book(data["Bids"], "bids", data["LastChange"][:-1])
                self.api_update_book(data["Asks"], "asks", data["LastChange"][:-1])

test = MarketData(source='Valr', ticker='BTCZAR')
test.connect()

        
