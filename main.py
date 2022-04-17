import json
import ccxt

from datetime import datetime
from Telegram.telegram_bot import MyTelegramBot


def load_json(filepath):
    with open(filepath) as json_file:
        return json.load(json_file)

TRACKING_PERCENT = 3
INTERVAL = '5m'

CONFIG = 'config.json'

config_info = load_json(CONFIG)

TELEGRAM_BOT_API = config_info['telegram']['token']
CHANNELS = config_info['telegram']['channels']

myTelegram = MyTelegramBot(TELEGRAM_BOT_API, CHANNELS)

apikey = config_info['exchanges']['BinanceFuture']['key']
secret = config_info['exchanges']['BinanceFuture']['secret']
exchange = ccxt.binance({
            'apiKey': apikey,
            'secret': secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',        # future trading
                'adjustForTimeDifference': True
            }})

# coin : time
track_records = {}

def check_pump_dump(exchange, coin, lv1):
    global track_records
    info = None
    try:
        info = exchange.fetch_ohlcv(coin, INTERVAL, limit=1)
    except Exception as e:
        print(f'error get ohlc, {e}')
    
    if info:
        print(info)
        timestamp = info[0][0]
        open = info[0][1]
        high = info[0][2]
        low = info[0][3]
        close = info[0][4]
        pump = ((high-low)/low)*100
        dump = ((high-low)/high)*100
        print(f"{coin}: {pump}, {dump}")
        if open < close and pump > lv1:
            if coin in track_records and track_records[coin] == timestamp:
                pass
            else:
                print(f"Pump in {coin} at {timestamp} percent: {dump}")
                message  =  f"📈 {coin} is Dumping on Binance Future!\n" \
                            f"💰 <b>Percent:</b> {round(dump, 2)}%\n" \
                            f"📌 <b>Price:</b>   ${close}\n" \
                            f"⏰ <b>At:</b> {datetime.utcfromtimestamp(float(timestamp)/1000).strftime('%Y-%m-%d %H:%M:%S')}"
                print(myTelegram.send_message(message, parse_mode='HTML', disable_web_page_preview=1))
                track_records[coin] = timestamp
        
        elif open > close and dump > lv1:
            if coin in track_records and track_records[coin] == timestamp:
                pass
            else:
                print(f"Dump in {coin} at {timestamp} percent: {dump}")
                message  =  f"📉 {coin} is Pumping on Binance Future!\n" \
                            f"💰 <b>Percent:</b> {round(dump, 2)}%\n" \
                            f"📌 <b>Price:</b>   ${close}\n" \
                            f"⏰ <b>At:</b> {datetime.utcfromtimestamp(float(timestamp)/1000).strftime('%Y-%m-%d %H:%M:%S')}"
                print(myTelegram.send_message(message, parse_mode='HTML', disable_web_page_preview=1))
                track_records[coin] = timestamp



if __name__ == '__main__':
    all_coins = exchange.load_markets()

    for coin in all_coins:
        print(coin)

    while 1:
        for coin in all_coins:
            check_pump_dump(exchange, coin, TRACKING_PERCENT)
