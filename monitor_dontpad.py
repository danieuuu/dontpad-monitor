import requests
import time
from telegram import Bot

# Configurações
DONT_PAD_URL = "https://dontpad.com/piguicinha.text"
BOT_TOKEN = "8021907392:AAHf16JeFTa090Op9RLsUoqKPgiscDyYwpM"
CHAT_ID = "7173683946"
CHECK_INTERVAL = 10  # Tempo em segundos entre verificações

bot = Bot(token=BOT_TOKEN)
last_content = ""

def get_dontpad_content():
    try:
        response = requests.get(DONT_PAD_URL)
        if response.status_code == 200:
            return response.text.strip()
    except requests.RequestException as e:
        print(f"Erro ao acessar o Dontpad: {e}")
    return None

def send_telegram_notification(message):
    try:
        bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        print(f"Erro ao enviar mensagem no Telegram: {e}")

print("Monitorando alterações no Dontpad...")
while True:
    content = get_dontpad_content()
    if content is not None and content != last_content:
        send_telegram_notification(f"O conteúdo do Dontpad foi alterado:\n\n{content}")
        last_content = content
    time.sleep(CHECK_INTERVAL)
