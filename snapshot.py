#!/home/admin/.pyenv/versions/3.8.2/bin/python
# -*- coding: utf-8 -*-

"""
This is a wallet stats bot.
"""

import time
import datetime as dt

import config
import logging
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import os
import sys
import urllib.request
import urllib.error
import json
import binance
from binance.client import Client

# setup logging
def status (mes):
    """
    This function prints out message and makes logging record.

    Parameters: 
        mes (str): message. 
    """

    print(mes)
    logging.debug(mes)


# setup logging
logtime = dt.datetime.now()
logging.basicConfig(
    filename='logs/snapshot' +
    str(logtime.year) + str(logtime.month) + str(logtime.day) + '.log',
    level=logging.DEBUG, 
    format='%(asctime)s %(message)s'
)
logging.debug('App Snapshot started')

# set account and api keys
ACCOUNT_CODE = "ALGO"
API_KEY = config.api_key
API_SECRET = config.api_secret

if len(sys.argv) == 2:
    ACCOUNT_CODE = sys.argv[1]
    API_KEY = config.api_key_main
    API_SECRET = config.api_secret_main

# set up database
engine = create_engine(config.db_sn_url)
db = scoped_session(sessionmaker(bind=engine))

# create python-binance client
client = Client(API_KEY, API_SECRET)

prices = {}
try:
    try:
        # getting latest prices
        url_address ='https://api.binance.com/api/v3/ticker/price'
        with urllib.request.urlopen(url_address) as url24:
            data24 = json.loads(url24.read())
        for coin in data24:
            prices[coin['symbol']] = float(coin['price'])

    except Exception as ex:
        status(ex)

    # getting snapshot volume
    info = client.get_account()

    # update time: store date of the last actions. So better take current time instead
    dt = str(info["updateTime"])[:-3]

    for asset in info["balances"] :
        if float(asset['free']) > 0 or float(asset['locked']) > 0 :

            # try to count bts and usd value of assets
            usd_value = 0.0
            usd_name = asset['asset'] + "USDT"
            btc_value = 0.0
            # for pairs like ETHBTC or LTCBTC
            btc_name = asset['asset'] + "BTC"
            # for pairs like BTCRUB or BTCBUSD
            btc_reverse_name = "BTC" + asset['asset']

            if asset['asset'] == "BTC":
                btc_value = float(asset['free']) + float(asset['locked'])
            elif btc_name in prices :
                btc_value = (float(asset['free']) + float(asset['locked'])) *  prices[btc_name]
            elif btc_reverse_name in prices:
                btc_value = (float(asset['free']) + float(asset['locked'])) /  prices[btc_reverse_name]
            
            if asset['asset'] == "USDT":
                usd_value = float(asset['free']) + float(asset['locked'])
            elif usd_name in prices:
                usd_value = (float(asset['free']) + float(asset['locked'])) *  prices[usd_name]
            else:
                usd_value = (float(asset['free']) + float(asset['locked'])) * (prices["BTCUSDT"] * prices[btc_name])


            # commit record
            db.execute("INSERT INTO snapshot24h (account, asset, dt, free, locked, usd, btc) VALUES \
                (:account, :asset, NOW(), :free, :locked, :usd, :btc)", {
                "account": ACCOUNT_CODE,
                "asset": asset['asset'],
                "free" : '%.8f' % float(asset['free']),
                "locked" : '%.8f' % float(asset['locked']),
                "usd" : '%.2f' % usd_value,
                "btc" : '%.8f' % btc_value,
            })
            db.commit()

except Exception as ex:
    status(ex)


status("=========process is over.========")