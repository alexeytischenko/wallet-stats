#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a wallet stat bot.
"""

import config
from wallet import Balance
from aiogram import Bot, Dispatcher, executor, types

import exceptions

# api_tocken retrive from telegram
API_TOKEN = config.api_tocken
# the only telegram account id allowed to use this bot
TELEGRAM_ACCESS_ID = config.telgram_client_id

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


def auth(func) :
    """Auth: only TELEGRAM_ACCESS_ID will be accepted."""

    async def wrapper(message):
        if message["from"]["id"] != TELEGRAM_ACCESS_ID:
            return await message.reply(
                "Access denied! for {}".format(message["from"]["id"]), 
                reply=False)
        return await func(message)

    return wrapper


@dp.message_handler(commands=['start', 'help'])
@auth
async def send_welcome(message: types.Message):
    """
    Bot help message.

    This handler will be called when user sends `/start` or `/help` command.
    """
    
    await message.reply(
        "Binance wallet stats bot\n\n"
        "For several days: /day1 or /day2\n"
        "For the weeks: /week1 \n"
        "For the months: /month1 ")


@dp.message_handler()
@auth
async def standard_reply(message: types.Message):
    """
    This handler will be called when user sends a command.
    Parameters: 
        message (str): received command.

    Returns:
        string to display as a reply
    """

    balance = Balance('MANUAL')
    print("created new instance of Balance: {}".format(id(balance)))

    try:
        reply_info, start_date, end_date = balance.summary_for(message.text)
    except exceptions.NotCorrectMessage as e:
        await message.reply(str(e))
        return

    answer_message = (
        f"Binance spot wallet stats \nfrom {start_date} to {end_date}\n\n"
        "                  amount          change\n"
        f"{reply_info}"
    )
    await message.reply(answer_message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)