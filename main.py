import json
import time
import ccxt
import threading

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

# coin : time
track_records = {}


def get_all_echanges(info):
    # global key
    response = []
    for exchange in info:
        response.append(exchange)
    return response


def check_pump_dump(exchange, exchange_name, coin, lv1):
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

        current = time.time()
        if timestamp < current*1000 - 10*60:
            return
        if open < close and pump > lv1:
            if coin in track_records[exchange_name] and track_records[exchange_name][coin] == timestamp:
                pass
            else:
                print(f"{exchange_name}: Pump in {coin} at {timestamp} percent: {dump}")
                message  =  f"📈 {coin} is Dumping on {exchange_name}!\n" \
                            f"💰 <b>Percent:</b> {round(dump, 2)}%\n" \
                            f"📌 <b>Price:</b>   ${close}\n" \
                            f"⏰ <b>At:</b> {datetime.utcfromtimestamp(float(timestamp)/1000).strftime('%Y-%m-%d %H:%M:%S')}"
                print(myTelegram.send_message(message, parse_mode='HTML', disable_web_page_preview=1))
                track_records[coin] = timestamp
        
        elif open > close and dump > lv1:
            if coin in track_records[exchange_name] and track_records[exchange_name][coin] == timestamp:
                pass
            else:
                print(f"{exchange_name}: Dump in {coin} at {timestamp} percent: {dump}")
                message  =  f"📉 {coin} is Pumping on {exchange_name}!\n" \
                            f"💰 <b>Percent:</b> {round(dump, 2)}%\n" \
                            f"📌 <b>Price:</b>   ${close}\n" \
                            f"⏰ <b>At:</b> {datetime.utcfromtimestamp(float(timestamp)/1000).strftime('%Y-%m-%d %H:%M:%S')}"
                print(myTelegram.send_message(message, parse_mode='HTML', disable_web_page_preview=1))
                track_records[coin] = timestamp



def thread_handle_exchange(exchange, exchange_name, all_coins, percent):
    while True:
        for coin in all_coins:
            check_pump_dump(exchange, exchange_name, coin, TRACKING_PERCENT)


if __name__ == '__main__':
    all_echanges = get_all_echanges(config_info['exchanges'])

    for exchange_name in all_echanges:
        track_records[exchange_name] = {}
    
        apikey = config_info['exchanges'][exchange_name]['key']
        secret = config_info['exchanges'][exchange_name]['secret']
        exchange = None
        if exchange_name == 'BinanceFuture':
            exchange = ccxt.binance({
                        'apiKey': apikey,
                        'secret': secret,
                        'enableRateLimit': True,
                        'options': {
                            'defaultType': 'future',        # future trading
                            'adjustForTimeDifference': True
                        }})
        elif exchange_name == 'Binance':
            exchange = ccxt.binance({
                        'apiKey': apikey,
                        'secret': secret,
                        'enableRateLimit': True,
                        'options': {
                            # 'defaultType': 'future',        # future trading
                            'adjustForTimeDifference': True
                        }})
        else:
            print('Not support for this exchange yet')

        if exchange:
            all_coins = exchange.load_markets()
            for coin in all_coins:
                print(coin)

            t = threading.Thread(target=thread_handle_exchange, args=(exchange, exchange_name, all_coins, TRACKING_PERCENT))
            t.daemon = True
            t.start()

    while True:
        time.sleep(10)
