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
test_exchange_index=2
prod_exchange_hostname="production"

port=25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

# ~~~~~============== NETWORKING CODE ==============~~~~~
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((exchange_hostname, port))
    return s.makefile('rw', 1)

def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read_from_exchange(exchange):
    return json.loads(exchange.readline())

def hello(exchange):
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})

def buy(exchange, order_id, symbol, price, size):
    write_to_exchange(exchange, {"type": "add", "order_id": order_id, "symbol": symbol, "dir": "BUY", "price": price, "size": size})

def sell(exchange, order_id, symbol, price, size)
    write_to_exchange(exchange, {"type": "add", "order_id": order_id, "symbol": symbol, "dir": "SELL", "price": price, "size": size})

def convert(exchange, order_id, symbol, size):
    write_to_exchange(exchange, {"type": "convert", "order_id": order_id, "symbol": symbol, "dir": "BUY", "size": size})

def cancel(exchange, order_id):
    write_to_exchange(exchange, {"type": "cancel", "order_id": order_id})

def get_info(exchange, buy_dict, sell_dict):
    from_exchange = read_from_exchange(exchange)

    words_arr = from_exchange.split()
    if words_arr[0] == "BOOK":
        security  = words_arr[1]
        buy_str = words_arr[words_arr.index("BUY") + 1]
        highest_buy_str = ""
        for char in buy_str:
            if char.isdigit():
                highest_buy_str = highest_buy_str + char
            else:
                break
        highest_buy_int = int(highest_buy_str)

        sell_str = words_arr[words_arr.index("SELL") + 1]
        lowest_sell_str = ""
        for char in sell_str:
            if char.isdigit():
                lowest_sell_str = lowest_sell_str + char
            else:
                break
        highest_buy_int = int(highest_buy_str)

# ~~~~~============== MAIN LOOP ==============~~~~~

def main():
    exchange = connect()

    sell_dict = {}
    buy_dict = {}

    order_id = random.randint(1000, 100000)

    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    # A common mistake people make is to call write_to_exchange() > 1
    # time for every read_from_exchange() response.
    # Since many write messages generate marketdata, this will cause an
    # exponential explosion in pending messages. Please, don't do that!
    print("The exchange replied:", hello_from_exchange, file=sys.stderr)

if __name__ == "__main__":
    main()

