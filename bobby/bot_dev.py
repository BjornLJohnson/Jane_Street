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
test_exchange_index=1
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

# ~~~~~============== PARAMETERS ==============~~~~~
exchange = connect()

increment = 1
decrement = 1

# ~~~~~============== BOT FUNCTIONS ==============~~~~~
def hello():
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    order_id = random.randint(1000, 5000000)
    write_to_exchange(exchange, {"type": "add", "order_id": order_id, "symbol": symbol, "dir": "BUY", "price": price, "size": size})

def sell(symbol, price, size):
    order_id = random.randint(1000, 5000000)
    write_to_exchange(exchange, {"type": "add", "order_id": order_id, "symbol": symbol, "dir": "SELL", "price": price, "size": size})

def buy(symbol, price, size):
    order_id = random.randint(1000, 5000000)
    write_to_exchange(exchange, {"type": "add", "order_id": order_id, "symbol": symbol, "dir": "BUY", "price": price, "size": size})

def convert(order_id, symbol, size):
    write_to_exchange(exchange, {"type": "convert", "order_id": order_id, "symbol": symbol, "dir": "BUY", "size": size})

def cancel(order_id):
    write_to_exchange(exchange, {"type": "cancel", "order_id": order_id})

def penny_buy(symbol, high, quantity):
    buy(symbol, high+increment, quantity)

def penny_sell(symbol, low, quantity):
    sell(symbol, low-decrement, quantity)

def get_fair_price(symbol, high, low):
    return (high+low)/2

def adr_arb():
    valbz_fair = get_fair_price("VALBZ", high, low)
    vale_fair = get_fair_price("VALE", high, low)

    if valbz_fair > vale_fair:
            buy(vale_fair, xprice, xsize)
            #do some conversion in between to maximize
            sell(vale_fair, xprice, xsize)

# ~~~~~============== MAIN LOOP ==============~~~~~

def main():
    
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    # A common mistake people make is to call write_to_exchange() > 1
    # time for every read_from_exchange() response.
    # Since many write messages generate marketdata, this will cause an
    # exponential explosion in pending messages. Please, don't do that!
    print("The exchange replied:", hello_from_exchange, file=sys.stderr)

    count = 0

    while True:
        if count%1000 == 0 :
            buy("BOND", 999, 1)
            sell("BOND", 1001, 1)

        count+=1
        response = read_from_exchange(exchange)
        messageType = response["type"]
        print(messageType,response, file=sys.stderr)
        # for symbol in sym_list :
        #     fair = get_fair_price(symbol, high, low)
        #     if fair>prev_fair :
        #         penny_buy(symbol, )
        #     elif

if __name__ == "__main__":
    main()
