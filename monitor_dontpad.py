import time
import os
import sys
import asyncio
import logging
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from telegram import Bot

# 🔗 Links a serem monitorados
DONT_PAD_URLS = [
    "https://dontpad.com/piguica",
]

BOT_TOKEN = "8021907392:AAEWaAw2UJ4aT2kWg1LCTJn4AyETK3alH7Q"
CHAT_ID = "7173683946"
TIMEOUT = 600  # Tempo máximo de espera por mudanças (10 min)
ALERT_INTERVAL = 3600  # Tempo para alertar sobre falta de mudanças (1 hora)

bot = Bot(token=BOT_TOKEN)
last_contents = {url: "" for url in DONT_PAD_URLS}
last_update = datetime.now()

# Configuração do logging
logging.basicConfig(level=logging.INFO)

def restart_bot():
    """ Reinicia o processo do bot caso o Selenium trave """
    logging.error("🚨 Selenium crashou! Reiniciando o bot...")
    os.execv(sys.executable, ['python'] + sys.argv)

def get_dontpad_content_selenium(url, driver):
    """ Acessa o Dontpad e retorna o texto digitado lá """
    try:
        driver.get(url)
        textarea = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "text"))
        )
        return textarea.get_attribute("value").strip()
    except Exception as e:
        logging.error(f"⚠️ Erro ao acessar o Dontpad ({url}): {e}")
        restart_bot()  # Reinicia o bot caso o Selenium trave
        return None

async def send_telegram_notification(url, content):
    """ Envia uma mensagem para o Telegram informando que houve atualização """
    message = f"📢 O conteúdo do Dontpad foi atualizado!\n🔗 {url}\n\n📜 **Conteúdo:**\n{content}"
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        logging.error(f"⚠️ Erro ao enviar mensagem no Telegram: {e}")

async def send_no_update_alert():
    """ Envia alerta caso nenhuma atualização ocorra por 1 hora """
    global last_update
    if datetime.now() - last_update > timedelta(seconds=ALERT_INTERVAL):
        try:
            await bot.send_message(chat_id=CHAT_ID, text="❌ Nenhuma atualização no Dontpad há 1 hora.")
            last_update = datetime.now()
        except Exception as e:
            logging.error(f"⚠️ Erro ao enviar alerta de inatividade: {e}")

def main():
    """ Loop principal que monitora continuamente os links do Dontpad """
    global last_update
    logging.info("🚀 Iniciando monitoramento do Dontpad...")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    loop = asyncio.get_event_loop()

    while True:
        for url in DONT_PAD_URLS:
            content = get_dontpad_content_selenium(url, driver)

            if content is not None:
                if content != last_contents[url]:  # Se houver mudança
                    loop.run_until_complete(send_telegram_notification(url, content))
                    last_contents[url] = content
                    last_update = datetime.now()  # Atualiza o tempo da última mudança

        loop.run_until_complete(send_no_update_alert())  # Verifica se deve enviar alerta

if __name__ == "__main__":
    main()
