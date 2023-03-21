import json
import time
import ccxt
import threading

import concurrent.futures
from datetime import datetime
from Libs.telegram_bot import MyTelegramBot
# import Libs.discord_client as discord_client


def load_json(filepath):
    with open(filepath) as json_file:
        return json.load(json_file)

TRACKING_PERCENT = 5
INTERVAL = '5m'


MAX_WORKERS = 2

CONFIG = 'config.json'

config_info = load_json(CONFIG)

TELEGRAM_BOT_API = config_info['telegram']['token']
TELEGRAM_CHANNELS = config_info['telegram']['channels']


DISCORD_TOKEN = config_info['discord']['token']
DISCORD_CHANNEL = config_info['discord']['channel']


myTelegram = MyTelegramBot(TELEGRAM_BOT_API, TELEGRAM_CHANNELS)
myDiscordCient = None
# myDiscordCient = discord_client
# myDiscordCient.init(DISCORD_TOKEN, DISCORD_CHANNEL)

# wait for discord start
time.sleep(10)
# myDiscordCient.send_message_to_discord("Test 1234 ")

# coin : time
track_records = {}


def get_all_exchanges(info):
    # global key
    response = []
    for exchange in info:
        response.append(exchange)
    return response


def send_message(mydiscord, mytelegram, message):
    # mydiscord.send_message_to_discord(message.replace('<b>', '**').replace('</b>', '**'))
    myTelegram.send_message(message, parse_mode='HTML', disable_web_page_preview=1)


def check_pump_dump(exchange, exchange_name, coin, lv1):
    global track_records
    info = None
    try:
        info = exchange.fetch_ohlcv(coin, INTERVAL, limit=1)
    except Exception as e:
        # print(f'error get ohlc, {e}')
        pass
    
    if info:
        # print(info)
        timestamp = info[0][0]
        open = info[0][1]
        high = info[0][2]
        low = info[0][3]
        close = info[0][4]
        pump = ((high-low)/low)*100
        dump = ((high-low)/high)*100
        # print(f"{coin}: {pump}, {dump}")

        current = time.time()
        if int(timestamp/1000) < current - 10*60:
            # print(f'Invalid timestamp. delta: {current*1000-timestamp}')
            return
        if open < close and pump > lv1:
            if coin in track_records[exchange_name] and track_records[exchange_name][coin] == timestamp:
                pass
            else:
                print(f"{exchange_name}: Pump in {coin} at {timestamp} percent: {dump}")
                message  =  f'📈 {coin} is Pumping on <b>{exchange_name}</b>!\n' \
                            f"💰 <b>Percent:</b> {round(dump, 2)}%\n" \
                            f"📌 <b>Price:</b>   ${close}\n" \
                            f"⏰ <b>At:</b> {datetime.utcfromtimestamp(float(timestamp)/1000).strftime('%Y-%m-%d %H:%M:%S')}"
                track_records[coin] = timestamp
                send_message(myDiscordCient, myTelegram, message)
        
        elif open > close and dump > lv1:
            if coin in track_records[exchange_name] and track_records[exchange_name][coin] == timestamp:
                pass
            else:
                print(f"{exchange_name}: Dump in {coin} at {timestamp} percent: {dump}")
                message  =  f'📉 {coin} is Dumping on <b>{exchange_name}</b>!\n' \
                            f"💰 <b>Percent:</b> {round(dump, 2)}%\n" \
                            f"📌 <b>Price:</b>   ${close}\n" \
                            f"⏰ <b>At:</b> {datetime.utcfromtimestamp(float(timestamp)/1000).strftime('%Y-%m-%d %H:%M:%S')}"
                track_records[coin] = timestamp
                send_message(myDiscordCient, myTelegram, message)



def thread_handle_exchange(exchange, exchange_name, all_coins, percent):
    while True:
        # for coin in all_coins:
        #     check_pump_dump(exchange, exchange_name, coin, TRACKING_PERCENT)
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                    futures = []
                    for coin in all_coins:
                            futures.append(
                                executor.submit(
                                    check_pump_dump, exchange=exchange, exchange_name=exchange_name, coin=coin, lv1=TRACKING_PERCENT
                                )
                            )
                    for future in concurrent.futures.as_completed(futures):
                        try:
                            pass
                        except Exception as e:
                            print(e)


def main():
    all_echanges = get_all_exchanges(config_info['exchanges'])
    send_message(myDiscordCient, myTelegram, 'test tset test ')
    for exchange_name in all_echanges:

        try:
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
            # elif exchange_name == 'Binance':
            #     exchange = ccxt.binance({
            #                 'apiKey': apikey,
            #                 'secret': secret,
            #                 'enableRateLimit': True,
            #                 'options': {
            #                     # 'defaultType': 'future',        # future trading
            #                     'adjustForTimeDifference': True
            #                 }})
            elif exchange_name == 'Huobi':
                exchange = ccxt.huobi({
                            'apiKey': apikey,
                            'secret': secret,
                            'enableRateLimit': True,
                            'options': {
                                'adjustForTimeDifference': True
                            }})
            elif exchange_name == 'MEXC':
                exchange = ccxt.mexc({
                            'apiKey': apikey,
                            'secret': secret,
                            'enableRateLimit': True,
                            'options': {
                                'adjustForTimeDifference': True
                            }})
            # elif exchange_name == 'Kucoin':
            #     exchange = ccxt.kucoin({
            #                 'apiKey': apikey,
            #                 'secret': secret,
            #                 'enableRateLimit': True,
            #                 'options': {
            #                     'adjustForTimeDifference': True
            #                 }})
            # elif exchange_name == 'FTX':
            #     exchange = ccxt.ftx({
            #                 'apiKey': apikey,
            #                 'secret': secret,
            #                 'enableRateLimit': True,
            #                 'options': {
            #                     'adjustForTimeDifference': True
            #                 }})
            # elif exchange_name == 'GateIo':
            #     exchange = ccxt.gateio({
            #                 'apiKey': apikey,
            #                 'secret': secret,
            #                 'enableRateLimit': True,
            #                 'options': {
            #                     'adjustForTimeDifference': True
            #                 }})
            else:
                print('Not support for this exchange yet')

            if exchange:
                all_coins = exchange.load_markets()
                # for coin in all_coins:
                #     print(coin)

                t = threading.Thread(target=thread_handle_exchange, args=(exchange, exchange_name, all_coins, TRACKING_PERCENT))
                t.daemon = True
                t.start()
        except Exception as e:
            print(f"Error exception: {e}")

    while True:
        time.sleep(10)


if __name__ == '__main__':
    main()
