# Binance wallet-stats telegram bot.
Bot returns value of Binance spot wallet for different periods.

##### Command supported by bot: 

**/start** or **/help** - for help
**/day[_n_]** - account value change comparing to the "n" days ago\
**/week[_n_]** - account value change comparing to the "n" weeks ago\
**/month[_n_]** - account value change comparing to the "n" months ago\


##### Constants used in code

`TELEGRAM_API_TOKEN` — bot API token

`TELEGRAM_ACCESS_ID` — Authorized Telegram ID, all other will be ignored

======================\
**config.py** file should have the following variables:

telegram api tocken
```
api_tocken = "1111111:XXXXXXXXXXXXX"
```
telgram account id
```
telgram_client_id = 111111111
```
postgres connect string
```
db_sn_url = "postgres://user:password@host"
```
======================