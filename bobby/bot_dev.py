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
test_exchange_index=0
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

def cancel(order_id):
    write_to_exchange(exchange, {"type": "cancel", "order_id": order_id})

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

def convert_buy(exchange, order_id, symbol, size):
    print("CONVERTING")
    write_to_exchange(exchange, {"type": "convert", "order_id": order_id, "symbol": symbol, "dir": "BUY", "size": size})
    print("CONVERTED")

def convert_sell(exchange, order_id, symbol, size):
    print("CONVERTING")
    write_to_exchange(exchange, {"type": "convert", "order_id": order_id, "symbol": symbol, "dir": "SELL", "size": size})
    print("CONVERTED")


def get_info(exchange, buy_dict, sell_dict):
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

def penny_buy(symbol, high, quantity):
    buy(symbol, high+increment, quantity)

def penny_sell(symbol, low, quantity):
    sell(symbol, low-decrement, quantity)

def get_fair_price(symbol, high, low):
    return (high+low)/2

def adr_arb(buy_dict, sell_dict):
    if "VALE" in buy_dict.keys() and "VALBZ" in sell_dict.keys():
       
        """
        valbz_fair = get_fair_price("VALBZ", buy_dict["VALBZ"], sell_dict["VALBZ"])
        vale_fair = get_fair_price("VALE", buy_dict["VALE"], sell_dict["VALE"])

        if valbz_fair > vale_fair:
            buy("VALE", buy_dict["VALE"] + 1, 1)
            #do some conversion in between to maximize
            sell("VALBZ", sell_dict["VALBZ"] - 1, 1)
        else:
            buy("VALBZ", buy_dict["VALBZ"] + 1, 1)
            sell("VALE", sell_dict["VALE"] - 1, 1)
            

       //// 
        valbz_buy = buy_dict["VALBZ"]
        valbz_sell = sell_dict["VALBZ"]

        vale_buy = buy_dict["VALE"]
        vale_sell = sell_dict["VALE"]

        if vale_sell - valbz_buy > 10:
            buy("VALBZ", valbz_buy+5, 10)
            convert(exchange, orders[len(orders)-1], "VALBZ", 1)
            sell("VALE", vale_sell-4, 10)

        if valbz_sell - vale_buy > 10:
            buy("VALE", valbz_buy+5, 10)
            convert(exchange, orders[len(orders)-1], "VALBZ", 1)
            sell("VALBZ", vale_sell-4, 10)
            """

def adr_equiv(buy_dict, sell_dict):
    if "VALE" in buy_dict.keys() and "VALBZ" in sell_dict.keys():
        valbz_fair = get_fair_price("VALBZ", buy_dict["VALBZ"], sell_dict["VALBZ"])
        valbz_buy = buy_dict["VALBZ"]
        valbz_sell = sell_dict["VALBZ"]

        order_id = random.randint(1000, 5000000)
        vale_buy= buy_dict["VALE"]
        vale_sell = sell_dict["VALE"]
        vale_fair = get_fair_price("VALE", buy_dict["VALE"], sell_dict["VALE"])

        if valbz_fair > vale_buy:
            buy("VALE", buy_dict["VALE"] + 1, 1)
        if valbz_fair < vale_sell:
            sell("VALE", sell_dict["VALE"] - 1, 1)

        """
        if valbz_fair > vale_sell:
            #buy("VALE", sell_dict["VALE"], 5)
            convert_sell(exchange, order_id, "VALE", 5) 

        elif valbz_fair < vale_buy:
            #buy("VALBZ", sell_dict["VALBZ"] - 1, 5)
            convert_buy(exchange, order_id + 1, "VALBZ", 5)

        elif vale_buy < valbz_fair:
            #buy("VALE", buy_dict["VALE"] + 5, 5)
            convert_sell(exchange, order_id + 2,"VALE", 5)
        
        convert_buy(exchange, order_id + 3, "VALBZ", 5)
        """

# ~~~~~============== MAIN LOOP ==============~~~~~
orders = []

def main():
    
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    # A common mistake people make is to call write_to_exchange() > 1
    # time for every read_from_exchange() response.
    # Since many write messages generate marketdata, this will cause an
    # exponential explosion in pending messages. Please, don't do that!
    print("The exchange replied:", hello_from_exchange, file=sys.stderr)
    sell_dict = {}
    buy_dict = {}

    count = 0

    while True:
        get_info(exchange, buy_dict, sell_dict)

        if count % 100 == 5:
            adr_equiv(buy_dict, sell_dict)
        
        count+=1
        response = read_from_exchange(exchange)
        messageType = response["type"]
        print(messageType, response, file=sys.stderr)
            

if __name__ == "__main__":
    main()
