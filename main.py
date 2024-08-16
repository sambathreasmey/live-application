import websockets
import json
import asyncio
import requests

from telegram_service import TelegramService

URL = "wss://stream.binance.com/stream"
TOKEN = "6757658881:AAEBla5WjW-L5VLYHLMM95ltPeatMV1QbG0"
CHAT_ID = "-1002027452267,-1002041524355,-1002028043556".split(",")

symbol = [{"BTCUSDT"},
        {"ETHUSDT"},
        {"SANDUSDT","ADAUSDT","BNBUSDT","DOGEUSDT","ARBUSDT","NOTUSDT"}]

def sendMessage(token, chat_id, text_message):
    if text_message == "":
        return "Message is empty"
    url = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text_message}&parse_mode=Markdown'
    response = requests.get(url)
    if response.status_code == 200:
        res = response.json()
        #print(f"Message sent to {res['result']['sender_chat']['title']} successfully!")
        return res
    else:
        print("An error occurred:", response.status_code, response.text)
        return response.json()
    
def editMessage(token, chat_id, message_id, new_text_message):
    if new_text_message == "":
        return "Message is empty"
    url = f'https://api.telegram.org/bot{token}/editMessageText'
    data = {
    "chat_id": chat_id,
    "message_id": message_id,
    "text": new_text_message,
    "parse_mode": "Markdown"
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        res = response.json()
        #print(f"Message edited to {res['result']['sender_chat']['title']} successfully!")
    else:
        print("An error occurred:", response.status_code, response.text)
    
def check_string_equality(str1, str2):
    str1 = str1.lower().strip()
    str2 = str2.lower().strip()
    return str1 == str2

async def live_coin():
    async with websockets.connect(URL) as websocket:
        payload = {
            "id": 1,
            "method": "SUBSCRIBE",
            "params": [
                "!miniTicker@arr@3000ms"
            ]
        }
        print(json.dumps(payload))
        await websocket.send(json.dumps(payload))

        #telegram setting
        refresh = [True,True,True]
        delay = [0,0,0]
        message_id = [0,0,0]
        old_message = ["","",""]

        first = True
        check_other = True
        i = -1
        while True:
            message = await websocket.recv()
            rec = json.loads(message)
            if first:
                # skip request to web socket
                first = False
            else:
                i+=1
                chat_id = CHAT_ID[i]
                helpers = []
                for filler in rec["data"]:
                    # check other coin
                    if i == 2:
                        if filler['s'] in symbol[i]:
                            helpers.append("*" + filler['s'][:-4] + "* " + str(filler['c'][:-3]) + "\n")
                        check_other = True
                    else:
                        # specific coin
                        if filler['s'] in symbol[i]:
                            message = filler['c'][:-3]
                            check_other = False
                if check_other:
                    message = "".join(helpers)

                # message handle
                try:
                    if refresh[i]:
                        if not check_string_equality(old_message[i], message):
                            data = sendMessage(TOKEN, chat_id, message)
                            message_id[i] = data['result']['message_id']
                            refresh[i] = False
                        else:
                            print("the sented message is duplicated !!!")
                    else:
                        # check duplicated message
                        if not check_string_equality(old_message[i], message):
                            editMessage(TOKEN, chat_id, message_id[i], message)
                            delay[i] += 1
                            # check delay edit message
                            if delay[i] == 150:
                                refresh[i] = True
                                delay[i] = 0
                            old_message[i] = message
                        else:
                            print("the edited message is duplicated !!!")
                except Exception as e: 
                    print("Exception !!! " + str(e))
                    TelegramService.sendException(method='live_crypto', message='internal server error!', exception=str(e))
                # check and set scope
                if i == 2:
                    i = -1


while True:
    try:
        print("Service is starting ...")
        asyncio.run(live_coin())
    except Exception as e: 
        print("Exception from Main !!! " + str(e))
        TelegramService.sendException(method='live_crypto', message='internal server error!', exception=str(e))