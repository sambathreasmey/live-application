import os
import requests
from dotenv import load_dotenv
import time

#Load environment
load_dotenv()
telegram_token = os.getenv('telegram.token')
telegram_chat_id = os.getenv('telegram.chat_id')
telegram_exception_chat_id = os.getenv('telegram.exception.chat_id')

class TelegramService:

    def sendException(method, message, exception):
        json_res = {
            "exception": exception
        }
        text_format = []
        text_format.append("🔴 ")
        text_format.append("*WEB SOCKET Exception")
        text_format.append("*")
        text_format.append("\n\n")
        text_format.append("method : ")
        text_format.append("*")
        text_format.append(method)
        text_format.append("*")
        text_format.append("\n")
        text_format.append("error : ")
        text_format.append("*")
        text_format.append(message)
        text_format.append("*")
        text_format.append("\n")
        text_format.append("```json")
        text_format.append("\n")
        text_format.append(str(json_res))
        text_format.append("```")
        text = "".join(text_format)
        url = f'https://api.telegram.org/bot{telegram_token}/sendMessage?chat_id={telegram_exception_chat_id}&text={text}&parse_mode=Markdown'
        response = requests.get(url)
        if response.status_code == 200:
            res = response.json()
            return res
        else:
            return response.json()