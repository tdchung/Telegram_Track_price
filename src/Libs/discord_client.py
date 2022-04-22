import discord
import asyncio
# from threading import Thread

import threading

client = discord.Client()

discord_loop = None
gToken = ""
gChannel = 0

def init(token, channel):
    global gToken, gChannel
    global discord_loop
    gToken = token
    gChannel = channel

    try:
        # asyncio.get_child_watcher()

        discord_loop = asyncio.get_event_loop()

        thread = threading.Thread(target=discord_loop.run_forever)
        thread.start()

        asyncio.run_coroutine_threadsafe(start(), discord_loop)
    except Exception as e:
        print(f"Error: init {e}")


async def start():
    global gToken, gChannel
    await client.start(gToken)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    print(f"on_message content: {message.content}, channel: {message.channel}")
    # await message.channel.send('Hello!')


@client.event
async def on_ready():
    global gToken, gChannel
    try:
        print(f"Discord bot has logged in as: {client.user.name}, id: {client.user.id}")
        send_message_to_discord("Auto bot is running... ")
    except Exception as e:
        print(f"Error: on_ready {e}")


def send_message_to_discord(message):
    res = False
    try:
        if discord_loop and client:
            asyncio.run_coroutine_threadsafe(client.get_channel(gChannel).send(message), discord_loop)
            res = True
        else:
            print('Discord not ready')
    except Exception as e:
        print(f"Error: send_message_to_discord {e}")
        

def send_message(message):
    return send_message_to_discord(message)
