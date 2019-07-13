#!/usr/bin/python

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import sys
import socket
import json
import random
import time

# ~~~~~============== CONFIGURATION  ==============~~~~~
# replace REPLACEME with your team name!
team_name="BANANAS"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = True

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index=0
prod_exchange_hostname="production"

port=25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

# ~~~~~============== NETWORKING CODE ==============~~~~~
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((exchange_hostname, port))
    s.settimeout(1)
    return s.makefile('rw', 1)

def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read_from_exchange(exchange):
    return json.loads(exchange.readline())

def hello():
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})

def sell(symbol, price, size):
    order_id = random.randint(1000, 5000000)
    write_to_exchange(exchange, {"type": "add", "order_id": order_id, "symbol": symbol, "dir": "SELL", "price": price, "size": size})

def buy(symbol, price, size):
    order_id = random.randint(1000, 5000000)
    write_to_exchange(exchange, {"type": "add", "order_id": order_id, "symbol": symbol, "dir": "BUY", "price": price, "size": size})

def convert(exchange, order_id, symbol, size):
    write_to_exchange(exchange, {"type": "convert", "order_id": order_id, "symbol": symbol, "dir": "BUY", "size": size})

def cancel(exchange, order_id):
    write_to_exchange(exchange, {"type": "cancel", "order_id": order_id})

# ~~~~~============== Algorithm CODE ==============~~~~~

def get_info(buy_dict, sell_dict):
    from_exchange = read_from_exchange(exchange)
    
    highest_bid = 9999999999
    lowest_offer = -9999999999
    if from_exchange["type"] == "book":
        security = from_exchange["symbol"]
        security = from_exchange["symbol"]
        if len(from_exchange["buy"]) > 0:
            highest_bid = from_exchange["buy"][0][0]
            buy_dict[security] = highest_bid
        if len(from_exchange["sell"]) > 0:
            lowest_offer = from_exchange["sell"][0][0]
            sell_dict[security] = lowest_offer

def penny(buy_dict, sell_dict, orders):
    for bond in buy_dict.keys():
        buy(bond, buy_dict[bond] + 1, 1)
        print("ORDERED")
        if not read_from_exchange(exchange)["type"] == "reject":
            orders.append(order_id)

    for bond in sell_dict.keys():
        sell(bond, sell_dict[bond] - 1, 1)
        print("SOLD")
        if not read_from_exchange(exchange)["type"] == "reject":
            orders.append(order_id)

def get_fair_price(symbol, high, low):
    return (high+low)/2

# ~~~~~============== MAIN LOOP ==============~~~~~
exchange = connect()

def main():
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    print("The exchange replied:", hello_from_exchange, file=sys.stderr)
    
    sell_dict = {}
    buy_dict = {}

    orders = []
    while(True):
        get_info(buy_dict, sell_dict)

        buy("BOND", 999, 1)
        sell("BOND", 1001, 1)
        penny(buy_dict, sell_dict, orders)
        time.sleep(5)

        # A common mistake people make is to call write_to_exchange() > 1
        # time for every read_from_exchange() response.
        # Since many write messages generate marketdata, this will cause an
        # exponential explosion in pending messages. Please, don't do that!

if __name__ == "__main__":
    main()
