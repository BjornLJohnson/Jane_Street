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

def hello(exchange):
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})

def sell(symbol, price, size):
    order_id = random.randint(1000, 5000000)
    write_to_exchange(exchange, {"type": "add", "order_id": order_id, "symbol": symbol, "dir": "SELL", "price": price, "size": size})
    print("SOLD", symbol)
    if not read_from_exchange(exchange)["type"] == "reject":
        orders.append(order_id)

def buy(symbol, price, size):
    order_id = random.randint(1000, 5000000)
    write_to_exchange(exchange, {"type": "add", "order_id": order_id, "symbol": symbol, "dir": "BUY", "price": price, "size": size})
    print("ORDERED", symbol)
    if not read_from_exchange(exchange)["type"] == "reject":
        orders.append(order_id)

def convert(exchange, order_id, symbol, size):
    write_to_exchange(exchange, {"type": "convert", "order_id": order_id, "symbol": symbol, "dir": "BUY", "size": size})

def cancel(exchange, order_id):
    write_to_exchange(exchange, {"type": "cancel", "order_id": order_id})

# ~~~~~============== ALGORITHM CODE ==============~~~~~

def get_info(exchange, buy_dict, sell_dict):
    from_exchange = read_from_exchange(exchange)

    highest_bid = 9999999999
    lowest_offer = -9999999999
    if from_exchange["type"] == "book":
        security = from_exchange["symbol"]
        if len(from_exchange["buy"]) > 0:
            highest_bid = from_exchange["buy"][0][0]
            buy_dict[security] = highest_bid
        if len(from_exchange["sell"]) > 0:
            lowest_offer = from_exchange["sell"][0][0]
            sell_dict[security] = lowest_offer

def penny(buy_dict, sell_dict, orders):
    for symbol in buy_dict.keys():
        if symbol != "BOND" :
            buy(symbol, buy_dict[symbol] + 1, 1)

    for symbol in sell_dict.keys():
        if symbol != "BOND" :
            sell(symbol, sell_dict[symbol] - 1, 1)

#10 shares of XLF is a basket of 3 BBOND, 2 GS, 3 MS, 2 WFC
def arbitrage(exchange, buy_dict, sell_dict, orders):
    xlf = ["BOND", "GS", "MS", "WFC"]
    total_basket_value = 0
    xlf_fair_value = 0
    for security in buy_dict.keys():
        if security in xlf:
            fair_value = (buy_dict[security] + sell_dict[security])
            if security == "BOND":
                total_basket_value += (3 * fair_value)
            elif security == "GS":
                total_basket_value += (2 * fair_value)
            elif security == "MS":
                total_basket_value += (3 * fair_value)
            elif security == "WFC":
                total_basket_value += (2 * fair_value)
        if security == "XLF":
            xlf_fair_value = 10 * (buy_dict[security] + sell_dict[security])

    if xlf_fair_value > total_basket_value:
        sell("XLF", sell_dict["XLF"] - 1, 50)

    if xlf_fair_value < total_basket_value:
        buy("XLF", buy_dict["XLF"] + 1, 50)


def get_fair_price(symbol, high, low):
    return (high+low)/2

# ~~~~~============== MAIN LOOP ==============~~~~~
exchange = connect()
orders = []

def main():
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    print("The exchange replied:", hello_from_exchange, file=sys.stderr)
    
    sell_dict = {}
    buy_dict = {}
    orders = []
    count = 0

    while(True):
        get_info(exchange, buy_dict, sell_dict)

        if count % 100 == 0:
            buy("BOND", 999, 1)
            sell("BOND", 1001, 1)
            #penny(buy_dict, sell_dict, orders)
            arbitrage(exchange, buy_dict, sell_dict, orders)

        count += 1
        # A common mistake people make is to call write_to_exchange() > 1
        # time for every read_from_exchange() response.
        # Since many write messages generate marketdata, this will cause an
        # exponential explosion in pending messages. Please, don't do that!

if __name__ == "__main__":
    main()
