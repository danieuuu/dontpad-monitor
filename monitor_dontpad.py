import os
import time
import asyncio
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from telegram import Bot

# 🔹 Configuração do bot do Telegram (usando variáveis de ambiente)
BOT_TOKEN = os.getenv("8021907392:AAEWaAw2UJ4aT2kWg1LCTJn4AyETK3alH7Q")
CHAT_ID = os.getenv("7173683946")

bot = Bot(token=BOT_TOKEN)

# 🔹 Lista de URLs do Dontpad para monitorar
DONT_PAD_URLS = [
    "https://dontpad.com/piguica",
    "https://dontpad.com/2defevereiro",
    "https://dontpad.com/splitfiction",
]

# 🔹 Dicionário para armazenar o último estado de cada link
last_content = {}

# 🔹 Configuração do Selenium (modo headless)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 🔹 Inicia o WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def get_dontpad_content(url):
    """Obtém o conteúdo do Dontpad usando Selenium."""
    try:
        driver.get(url)
        textarea = driver.find_element("id", "text")
        return textarea.get_attribute("value").strip()
    except Exception as e:
        print(f"Erro ao acessar {url}: {e}")
        return None

def send_telegram_notification(url):
    """Envia uma notificação para o Telegram quando o conteúdo for alterado."""
    try:
        asyncio.run(bot.send_message(chat_id=CHAT_ID, text=f"O conteúdo do Dontpad foi atualizado: {url}"))
        print(f"🔔 Notificação enviada: {url}")
    except Exception as e:
        print(f"⚠️ Erro ao enviar mensagem no Telegram: {e}")

print("🚀 Monitorando alterações no Dontpad...")

while True:
    for url in DONT_PAD_URLS:
        content = get_dontpad_content(url)

        if content is not None:
            if url not in last_content or content != last_content[url]:
                send_telegram_notification(url)
                last_content[url] = content

    time.sleep(10)  # Intervalo entre verificações
