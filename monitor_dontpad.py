import os
import time
import logging
import asyncio
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from telegram import Bot

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configurações do Telegram
BOT_TOKEN = os.getenv("8021907392:AAEWaAw2UJ4aT2kWg1LCTJn4AyETK3alH7Q")  # Certifique-se de definir essa variável no Railway
CHAT_ID = os.getenv("7173683946")
bot = Bot(token=BOT_TOKEN)

# Lista de páginas para monitorar
URLS = [
    "https://dontpad.com/piguica",
    "https://dontpad.com/outralink"
]

# Configuração do Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
service = Service(ChromeDriverManager().install())

def get_dontpad_content(url):
    """Tenta obter o conteúdo do Dontpad e reinicia o bot se falhar."""
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        time.sleep(3)
        content = driver.find_element("id", "text").text.strip()
        driver.quit()
        return content
    except Exception as e:
        logging.error(f"Erro ao acessar o Dontpad ({url}): {e}")
        return None

def restart_bot():
    """Reinicia o processo do bot."""
    logging.info("Reiniciando o bot...")
    os.execv(sys.executable, ['python'] + sys.argv)

def monitor_dontpad():
    last_content = {url: None for url in URLS}
    last_update = datetime.now()

    while True:
        for url in URLS:
            content = get_dontpad_content(url)
            
            if content is None:
                logging.error("Falha ao obter conteúdo. Reiniciando...")
                restart_bot()
            
            if last_content[url] is None:
                last_content[url] = content
                continue
            
            if content != last_content[url]:
                logging.info(f"Mudança detectada em {url}!")
                bot.send_message(chat_id=CHAT_ID, text=f"🟢 Atualização detectada em {url}")
                last_content[url] = content
                last_update = datetime.now()
            
        # Se passou 1 hora sem mudanças, enviar um aviso
        if datetime.now() - last_update > timedelta(hours=1):
            bot.send_message(chat_id=CHAT_ID, text="❌ Nenhuma atualização no Dontpad há 1 hora.")
            last_update = datetime.now()
        
        time.sleep(1800)  # Verifica a cada 1 minuto

if __name__ == "__main__":
    monitor_dontpad()
