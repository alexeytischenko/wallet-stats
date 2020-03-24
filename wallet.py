#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config
from timeframes import timeframes
import exceptions
#from collections import namedtuple
from typing import Dict, List, NamedTuple
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import re

# Set up database
engine = create_engine(config.db_sn_url)
db = scoped_session(sessionmaker(bind=engine))


class Asset(NamedTuple):
    """Datatype 'asset'. """
    date: str
    name: str
    amount: float
    usd_value: float
    btc_value: float


class Balance:
    """ 
    This is a class for gethering stats on a cripto wallet. 
      
    Attributes: 
        assets: list of assets. 
    """


    def __init__(self):
        """ 
        The constructor for Balance class.
        """

        self.assets = self.assets_for("DAY", 0) # current values of all assets


    def assets_for (self, timeframe, count) -> Dict:
        """ 
        The function to requested DataBase records for given period. 
  
        Parameters: 
            timeframe (str): interval (DAY|MONTH|YEAR). 
            count (int): number of intervals
          
        Returns: 
            Dict: assets and their values for given period. 
        """
        assets_dict = dict() # list of assets

        try:
            # get all assets for date interval '{count}' {timeframe} minus 1 day
            # for today values use: '0' DAY
            query = f"SELECT * FROM snapshot24h WHERE \
                DATE(dt) > CURRENT_DATE - (INTERVAL '{count}' {timeframe} + INTERVAL '1' DAY) AND \
                DATE(dt) <= CURRENT_DATE - INTERVAL '{count}' {timeframe}"
            print(query)
            records = db.execute(query).fetchall()

            for record in records:
                assets_dict[record.asset] = Asset(
                    date=str(record.dt)[:10],
                    name=record.asset, 
                    amount=(record.free + record.locked), 
                    usd_value=record.usd, 
                    btc_value=record.btc)

        except Exception as ex:
            print(ex)

        return assets_dict


    def summary_for (self, period) -> str:
        """ 
        The function to calculate account change summary for given period. 
  
        Parameters: 
            period (str): String represented period. 
          
        Returns: 
            Formated string with wallet info
        """

        # 0. parse period into format DAY|WEEK|MONTH <num>
        timeframe, count = self.parse_date(period)

        # 1. get data for the first day before 'period' 
        retro_assets = self.assets_for(timeframe, count)

        # define start and end date to display to user
        start_date = "..."
        if len(list(retro_assets.keys())) > 0:
            start_date = retro_assets[list(retro_assets.keys())[0]].date
        end_date = "..."
        if len(list(self.assets.keys())) > 0:
            end_date = self.assets[list(self.assets.keys())[0]].date

        reply_info = f"Balance change from {start_date} to {end_date}\n\n"
        reply_info += f"           amount       btc change    usd change\n"

        # 1.5 calculate total value of wallet (usd, btc) in the past
        retro_total_btc = 0
        retro_total_usd = 0

        for asset, retro_asset in retro_assets.items():
            retro_total_usd += retro_asset.usd_value
            retro_total_btc += retro_asset.btc_value

        # 2. compare with current values
        total_usd = 0
        total_btc = 0

        for asset, value in self.assets.items():
            total_usd += value.usd_value
            total_btc += value.btc_value

            # calculate value % change in BTC and USD
            chnage_btc = "0.00"
            chnage_usd = "0.00"
            if asset in retro_assets:
                if value.btc_value != 0:
                    chnage_btc = '%.2f' % float(((value.btc_value - retro_assets[asset].btc_value)/value.btc_value) * 100)
                if value.usd_value != 0:
                    chnage_usd = '%.2f' % float(((value.usd_value - retro_assets[asset].usd_value)/value.usd_value) * 100)

            # form reply lines, ex: BNB 15 10% -1%
            reply_info += f"{asset}     {value.amount}      {chnage_btc}%          {chnage_usd}%  \n"
        
        #final lines, ex: TOTAL BTC 1.1 10%
        if total_btc != 0:
            btc_change = '%.2f' % float(((total_btc - retro_total_btc) / total_btc)*100)
            reply_info += f"\nTOTAL BTC     {'%.8f' % total_btc}  ({btc_change}%)\n"
        if total_usd != 0:
            usd_change = '%.2f' % float(((total_usd - retro_total_usd) / total_usd)*100)
            reply_info += f"TOTAL USD     {'%.2f' % total_usd}  ({usd_change}%)\n"

        return reply_info


    def parse_date (self, period) :  #-> str, int
        """ 
        The function to parse string into timeframe and amount. 
  
        Parameters: 
            period (str): String represented period. 
          
        Returns: 
            timeframe: str DAY|WEEK|MONTH. 
            count: int 
        """

        regexp_result = re.match(r"(\D*)\s?(\d+)", period)
        if not regexp_result or \
            not regexp_result.group(0) or \
            not regexp_result.group(1) or \
            not regexp_result.group(2):
                raise exceptions.NotCorrectMessage("Unknown command, try DAY1 or MONTH")

        tf = regexp_result.group(1).strip().upper()
        if tf.startswith("/"):
            tf = tf[1:]
        count = int(regexp_result.group(2).replace(" ", ""))

        if tf in timeframes:
            return_tf = timeframes[tf]

            # special aproach to WEEK
            if return_tf == "WEEK":
                return_tf = "DAY"
                count = count * 7

            return return_tf, count
        else:
            raise exceptions.NotCorrectMessage("Unknown timeframe, try DAY1 or MONTH")

        return 'DAY', 1