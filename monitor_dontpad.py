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

# Configurar logging para debug
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 📝 Lista de links a serem monitorados
DONT_PAD_URLS = [
    "https://dontpad.com/piguica",
]

BOT_TOKEN = "8021907392:AAEWaAw2UJ4aT2kWg1LCTJn4AyETK3alH7Q"
CHAT_ID = "7173683946"
CHECK_INTERVAL = 1800  # Tempo entre verificações (30 min)
NO_UPDATE_WARNING_TIME = 3600  # Tempo sem atualizações antes de mandar alerta (1 hora)

bot = Bot(token=BOT_TOKEN)

# Dicionário para armazenar o último conteúdo de cada link
last_contents = {url: "" for url in DONT_PAD_URLS}
last_update = datetime.now()  # Última atualização válida


def restart_bot():
    """Reinicia o bot caso ocorra erro crítico."""
    logging.info("🔄 Reiniciando o bot devido a erro...")
    os.execv(sys.executable, ['python'] + sys.argv)


def get_dontpad_content_selenium(url):
    """Acessa o Dontpad e retorna o texto digitado lá."""
    global last_update

    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Roda sem abrir o navegador
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)

        time.sleep(3)  # Espera o JavaScript carregar

        textarea = driver.find_element(By.ID, "text")
        text_content = textarea.get_attribute("value").strip()

        driver.quit()
        return text_content

    except WebDriverException as e:
        logging.error(f"⚠️ Erro ao acessar o Dontpad ({url}): {e}")
        
        # Se for erro do ChromeDriver, reiniciar o bot
        if "chromedriver unexpectedly exited" in str(e):
            restart_bot()
        
        return None


async def send_telegram_notification(url):
    """Envia uma mensagem para o Telegram informando que houve atualização."""
    global last_update
    message = f"📢 O conteúdo do Dontpad foi atualizado!\n🔗 {url}"
    
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
        last_update = datetime.now()  # Atualiza o tempo da última mudança
    except Exception as e:
        logging.error(f"⚠️ Erro ao enviar mensagem no Telegram: {e}")


async def send_no_update_warning():
    """Envia um aviso se não houver atualização por 1 hora."""
    global last_update
    if datetime.now() - last_update > timedelta(seconds=NO_UPDATE_WARNING_TIME):
        try:
            await bot.send_message(chat_id=CHAT_ID, text="❌ Nenhuma atualização no Dontpad há 1 hora.")
            logging.warning("❌ Nenhuma atualização no Dontpad há 1 hora.")
            last_update = datetime.now()  # Atualiza o tempo para não enviar várias vezes seguidas
        except Exception as e:
            logging.error(f"⚠️ Erro ao enviar aviso no Telegram: {e}")


# Criar um loop assíncrono para rodar sem fechar
loop = asyncio.get_event_loop()

logging.info("🚀 Monitorando múltiplos links do Dontpad...")

while True:
    for url in DONT_PAD_URLS:
        content = get_dontpad_content_selenium(url)

        if content is not None:
            logging.info(f"🔍 [{url}] Verificado!")

            if content != last_contents[url]:
                loop.run_until_complete(send_telegram_notification(url))
                last_contents[url] = content  # Atualiza o último conteúdo

    loop.run_until_complete(send_no_update_warning())  # Verifica se precisa mandar aviso

    time.sleep(CHECK_INTERVAL)  # Aguarda antes da próxima verificação
