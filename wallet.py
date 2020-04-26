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

def drop_trail_zeros(float_num):
    """ 
    Drops trailing zeros. 
    
    Parameters: 
        float_num (str): float number represented in string.   

    Returns: 
        float.   
    """
    return float(re.sub(r"(\d+\.\d+?)(0+)$", r"\1", str(float_num)))

class Balance:
    """ 
    This is a class for gethering stats on a cripto wallet. 
      
    Attributes: 
        assets: list of assets. 
    """


    def __init__(self, acc):
        """ 
        The constructor for Balance class.
        """
        self.account = acc
        self.assets = self.assets_for("DAY", 0) # current values of all assets


    def assets_for (self, timeframe, count) -> Dict:
        """ 
        The function to requested DataBase records for given period. 
  
        Parameters: 
            timeframe (str): interval (DAY|MONTH|YEAR). 
            count (int): number of intervals
            asset_name (str): request more detailed info on certain asset
          
        Returns: 
            Dict: assets and their values for given period. 
        """
        assets_dict = dict() # list of assets

        try:
            # get all assets for date interval '{count}' {timeframe} minus 1 day
            # for today values use: '0' DAY
            query = f"SELECT * FROM snapshot24h WHERE account = '{self.account}' AND \
                DATE(dt) > CURRENT_DATE - (INTERVAL '{count}' {timeframe} + INTERVAL '1' DAY) AND \
                DATE(dt) <= CURRENT_DATE - INTERVAL '{count}' {timeframe}"
            print(query)
            records = db.execute(query).fetchall()

            for record in records:
                assets_dict[record.asset.rstrip()] = Asset(
                    date=str(record.dt)[:10],
                    name=record.asset.rstrip(), 
                    amount=(record.free + record.locked), 
                    usd_value=record.usd, 
                    btc_value=record.btc)

        except Exception as ex:
            print(ex)

        return assets_dict


    def summary_for (self, period):
        """ 
        The function to calculate account change summary for given period. 
  
        Parameters: 
            period (str): String represented period. 
          
        Returns: 
            reply_info Formated string with wallet info
            start_date Formated string - start of period
            end_date Formated string - end of period
        """
        reply_info = ""

        # 0. parse period into format DAY|WEEK|MONTH <num>
        timeframe, count, asset_name = self.parse_date(period)

        # 1. get data for the first day before 'period' 
        retro_assets = self.assets_for(timeframe, count)

        # define start and end date to display to user
        start_date = "..."
        if len(list(retro_assets.keys())) > 0:
            start_date = retro_assets[list(retro_assets.keys())[0]].date
        end_date = "..."
        if len(list(self.assets.keys())) > 0:
            end_date = self.assets[list(self.assets.keys())[0]].date

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
            change_val = chnage_btc = chnage_btc_per = chnage_usd = chnage_usd_per = "-"

            if asset in retro_assets:
                change_val = '%.8f' % float(value.amount - retro_assets[asset].amount)
                if value.btc_value != 0:
                    chnage_btc = '%.8f' % float(value.btc_value - retro_assets[asset].btc_value)
                    chnage_btc_per = '%.2f' % float(((value.btc_value - retro_assets[asset].btc_value)/value.btc_value) * 100)
                if value.usd_value != 0:
                    chnage_usd = '%.2f' % float(value.usd_value - retro_assets[asset].usd_value)
                    chnage_usd_per = '%.2f' % float(((value.usd_value - retro_assets[asset].usd_value)/value.usd_value) * 100)

            # form reply lines, format ASSET value change \n\n btc value (% change) usd value (% change)
            if asset_name is None or asset_name == asset:
                reply_info += "{:<9}{:<15}{:^15}\nbtc {}({}%)  ${}({}%)\n\n" \
                    .format(asset, float(value.amount), float(change_val), \
                    float(chnage_btc), chnage_btc_per, chnage_usd, chnage_usd_per)

        
        #final lines, ex: TOTAL BTC 1.1 10%
        if total_btc != 0:
            btc_change = total_btc - retro_total_btc
            btc_change_per = (total_btc - retro_total_btc) / total_btc
            reply_info += "\nTOTAL BTC     {:.8f}  {:.8f} ({:.2%})\n"\
                .format(float(total_btc), float(btc_change), float(btc_change_per))
        if total_usd != 0:
            usd_change = '%.2f' % float(total_usd - retro_total_usd)
            usd_change_per = '%.2f' % float(((total_usd - retro_total_usd) / total_usd)*100)
            reply_info += f"TOTAL USD     {'%.2f' % total_usd}  {usd_change} ({usd_change_per}%)\n"

        return reply_info, start_date, end_date


    def parse_date (self, period) :  #-> str, int
        """ 
        The function to parse string into timeframe and amount. 
  
        Parameters: 
            period (str): String represented period. 
          
        Returns: 
            timeframe: str DAY|WEEK|MONTH. 
            count: int 
        """

        regexp_result = re.match(r"(\D*)\s?(\d+)(?:\s?(.+))?", period)
        if not regexp_result or \
            not regexp_result.group(0) or \
            not regexp_result.group(1) or \
            not regexp_result.group(2):
                raise exceptions.NotCorrectMessage("Unknown command, try DAY1 or MONTH1")

        tf = regexp_result.group(1).strip().upper()
        if tf.startswith("/"):
            tf = tf[1:]
        count = int(regexp_result.group(2).replace(" ", ""))

        asset = None
        if regexp_result.group(3) is not None:
            asset = regexp_result.group(3).strip().upper()
        print(asset)

        if tf in timeframes:
            return_tf = timeframes[tf]

            # special aproach to WEEK
            if return_tf == "WEEK":
                return_tf = "DAY"
                count = count * 7

            return return_tf, count, asset
        else:
            raise exceptions.NotCorrectMessage("Unknown timeframe, try DAY1 or MONTH1")

        return 'DAY', 1, None
