

import logging
from copy import copy
from datetime import datetime
from decimal import Decimal, getcontext
 
getcontext().prec = 10
 
# logger = logging.getLogger('LUNO_ORDERBOOK')
# logger.setLevel(logging.INFO)
# ch = logging.StreamHandler()
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# ch.setFormatter(formatter)
# logger.addHandler(ch)
 
 
class Order(object):
    '''
    Struct for representing and order received in the XML file.
    '''
    __slots__ = ['orderId', 'bidAsk', 'price', 'volume']
 
    def __init__(self, orderId, bidAsk, price, volume, ts=None):
        self.orderId = str(orderId)
        self.bidAsk = bidAsk
        self.price = Decimal(price)
        self.volume = Decimal(volume)
        # self.created_ts = ts
 
    def __lt__(self, other):
        '''
        Implementation of custom comparison function so that Buy/Sell lists will be organized correctly.
        '''
        if self.price == other.price:
            return self.orderId < other.orderId
        if self.bidAsk == 'BUY':
            return self.price > other.price
        else:
            return self.price < other.price
 
    def __eq__(self, other):
        if self.orderId == other.orderId:
            return True
        return False
 
    def __str__(self):
        if str(self.orderId) == '1':
            return '%s V: %s @ P: %s' % (self.bidAsk, self.volume, self.price)
        else:
            return 'Id: %s, %s V: %s @ P: %s' % (self.orderId, self.bidAsk, self.volume, self.price)
 
    def to_dict(self):
        result = {'oid': self.orderId,
                  'side': self.bidAsk,
                  'price': str(self.price),
                  'volume': str(self.volume)}
        return result
 
 
class SimpleOrderbook(object):
    __slots__ = ['asks', 'asks_by_price', 'bids', 'bids_by_price', 'orders_by_price']
 
    def __init__(self, asks, bids, ts=None):
        self.asks = asks
        self.asks_by_price = {}
        self.bids = bids
        self.bids_by_price = {}
        self.orders_by_price = {}
        for key, order in bids.items():
            if order.price in self.bids_by_price:
                self.bids_by_price[order.price] += order.volume
            else:
                self.bids_by_price[order.price] = order.volume
 
            if order.price in self.orders_by_price:
                self.orders_by_price[order.price].append(copy(order))
            else:
                self.orders_by_price[order.price] = [copy(order)]
 
        for key, order in asks.items():
            if order.price in self.asks_by_price:
                self.asks_by_price[order.price] += order.volume
            else:
                self.asks_by_price[order.price] = order.volume
 
            if order.price in self.orders_by_price:
                self.orders_by_price[order.price].append(copy(order))
            else:
                self.orders_by_price[order.price] = [copy(order)]
 
    def addOrder(self, order):
        if order.bidAsk == 'BID':
            self.bids[order.orderId] = order
            if order.price in self.bids_by_price:
                self.bids_by_price[order.price] += order.volume
            else:
                self.bids_by_price[order.price] = order.volume
        else:
            self.asks[order.orderId] = order
            if order.price in self.asks_by_price:
                self.asks_by_price[order.price] += order.volume
            else:
                self.asks_by_price[order.price] = order.volume
 
        if order.price in self.orders_by_price:
            self.orders_by_price[order.price].append(copy(order))
        else:
            self.orders_by_price[order.price] = [copy(order)]
 
    def reduceOrder(self, order):
        if order.orderId in self.bids:
            maker_order = copy(self.bids[order.orderId])
            order.price = maker_order.price
            order.bidAsk = 'ASK'  # This is the aggressor/taker trade side
            self.bids[order.orderId].volume -= order.volume
            if self.bids[order.orderId].volume <= 0:
                del self.bids[order.orderId]
            self.bids_by_price[maker_order.price] -= order.volume
            if self.bids_by_price[maker_order.price] <= 0:
                del self.bids_by_price[maker_order.price]
 
        else:
            maker_order = copy(self.asks[order.orderId])
            order.price = maker_order.price
            order.bidAsk = 'BID'  # This is the aggressor/taker trade side
            self.asks[order.orderId].volume -= order.volume
            if self.asks[order.orderId].volume <= 0:
                del self.asks[order.orderId]
            self.asks_by_price[maker_order.price] -= order.volume
            if self.asks_by_price[maker_order.price] <= 0:
                del self.asks_by_price[maker_order.price]
 
        for o in self.orders_by_price[maker_order.price]:
            if o == maker_order:
                o.volume -= order.volume
                if o.volume <= 0:
                    self.orders_by_price[maker_order.price].remove(maker_order)
                break
 
        return order
 
    def deleteOrder(self, orderId):
        try:
            order = self.asks[orderId]
            self.asks_by_price[order.price] -= order.volume
            if self.asks_by_price[order.price] <= 0:
                del self.asks_by_price[order.price]
            del self.asks[orderId]
        except KeyError:
            order = self.bids[orderId]
            self.bids_by_price[order.price] -= order.volume
            if self.bids_by_price[order.price] <= 0:
                del self.bids_by_price[order.price]
            del self.bids[orderId]
        if order.price in self.orders_by_price:
            print('Removing %s' % order)
            self.orders_by_price[order.price].remove(order)
        else:
            self.orders_by_price[order.price] = []
 
    def to_dict(self, top_levels=30):
        result = {}
        result['asks'] = {}
        for price in sorted(self.asks_by_price.keys())[:top_levels]:
            result['asks'][str(price)] = {'volume': str(self.asks_by_price[price]), 'orders': [o.to_dict() for o in self.orders_by_price[price]]}
        result['bids'] = {}
        for price in sorted(self.bids_by_price.keys(), reverse=True)[:top_levels]:
            result['bids'][str(price)] = {'volume': str(self.bids_by_price[price]), 'orders': [o.to_dict() for o in self.orders_by_price[price]]}
        result['timestamp'] = datetime.utcnow().isoformat()
        return result
 
    def __str__(self):
        prec = getcontext().prec
        top_bids = sorted(self.bids_by_price.keys(), reverse=True)[:30]
        top_asks = sorted(self.asks_by_price.keys())[:30]
        result = 'Bids-----------=====================-----------Asks\n'
        for i in range(len(top_bids)):
            bid_price = top_bids[i]
            bid_vol = str(self.bids_by_price[bid_price])
            ask_price = top_asks[i]
            ask_vol = str(self.asks_by_price[ask_price])
 
            result += ("%s -- %s|%s -- %s\n" %
                       (bid_vol[:bid_vol.find('.') + prec],
                        str(bid_price)[:str(bid_price).find('.') + prec],
                        str(ask_price)[:str(ask_price).find('.') + prec],
                        ask_vol[:ask_vol.find('.') + prec]))
        return result
