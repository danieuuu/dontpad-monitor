import time
import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from telegram import Bot

# Configuração
DONT_PAD_URLS = [
    "https://dontpad.com/piguica",

]
BOT_TOKEN = "8021907392:AAEWaAw2UJ4aT2kWg1LCTJn4AyETK3alH7Q"
CHAT_ID = "7173683946"
CHECK_INTERVAL = 10 # Tempo entre verificações (30 minutos)
bot = Bot(token=BOT_TOKEN)
last_contents = {url: "" for url in DONT_PAD_URLS}
last_update = datetime.now()

# Criar um loop assíncrono global
loop = asyncio.get_event_loop()

# Configuração do ChromeDriver
def create_driver():
    """Cria e retorna uma nova instância do ChromeDriver"""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except WebDriverException as e:
        logging.error(f"Erro ao iniciar o ChromeDriver: {e}")
        return None

driver = create_driver()  # Inicializa o driver

def get_dontpad_content(url):
    """Obtém o conteúdo do Dontpad usando Selenium"""
    global driver
    try:
        if driver is None:
            driver = create_driver()  # Tenta recriar o driver

        if driver is not None:
            driver.get(url)
            time.sleep(3)  
            textarea = driver.find_element(By.ID, "text")
            return textarea.get_attribute("value").strip()
    except WebDriverException as e:
        logging.error(f"Erro ao acessar {url}: {e}")
        driver.quit()  # Fecha o driver quebrado
        driver = None  # Marca como None para recriar depois
        return None

async def send_telegram_notification(url, content):
    """Envia mensagem para o Telegram com a atualização"""
    message = f"📢 O conteúdo do Dontpad foi atualizado!\n🔗 {url}\n📝 Conteúdo:\n\n{content}"
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        logging.error(f"Erro ao enviar mensagem no Telegram: {e}")

while True:
    for url in DONT_PAD_URLS:
        content = get_dontpad_content(url)

        if content is not None:
            if content != last_contents[url]:
                loop.run_until_complete(send_telegram_notification(url, content))
                last_contents[url] = content  
                last_update = datetime.now()  

    # Se passou 1 hora sem mudanças, enviar um aviso
    if datetime.now() - last_update > timedelta(hours=1):
        loop.run_until_complete(bot.send_message(chat_id=CHAT_ID, text="❌ Nenhuma atualização no Dontpad há 1 hora."))
        last_update = datetime.now()

    time.sleep(CHECK_INTERVAL)  
