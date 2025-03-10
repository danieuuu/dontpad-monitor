import time
import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from telegram import Bot

# 📝 Lista de links a serem monitorados
DONT_PAD_URLS = [
    "https://dontpad.com/piguica",
    "https://dontpad.com/2defevereiro",
    "https://dontpad.com/splitfiction"
]

BOT_TOKEN = "8021907392:AAEWaAw2UJ4aT2kWg1LCTJn4AyETK3alH7Q"
CHAT_ID = "7173683946"
CHECK_INTERVAL = 1800  # 30 minutos
NO_UPDATE_ALERT_INTERVAL = 3600  # 1 hora

bot = Bot(token=BOT_TOKEN)

# Dicionários para armazenar o último conteúdo e o tempo da última atualização
last_contents = {url: "" for url in DONT_PAD_URLS}
last_update_times = {url: datetime.now() for url in DONT_PAD_URLS}


def get_dontpad_content_selenium(url):
    """Acessa o Dontpad e retorna o texto digitado lá."""
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)

        time.sleep(3)  # Espera o JavaScript carregar

        textarea = driver.find_element(By.ID, "text")
        text_content = textarea.get_attribute("value").strip()

        driver.quit()
        return text_content
    except Exception as e:
        print(f"⚠️ Erro ao acessar o Dontpad ({url}): {e}")
        return None


def restart_bot():
    """Reinicia o processo do bot em caso de falha contínua."""
    logging.info("Reiniciando o bot...")
    os.execv(sys.executable, ['python'] + sys.argv)


async def send_telegram_notification(url):
    """Envia uma mensagem para o Telegram informando que houve atualização."""
    message = f"📢 O conteúdo do Dontpad foi atualizado!\n🔗 {url}"
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        print(f"⚠️ Erro ao enviar mensagem no Telegram: {e}")


async def send_no_update_alert():
    """Envia um alerta se nenhuma atualização ocorreu no último intervalo."""
    try:
        await bot.send_message(chat_id=CHAT_ID, text="❌ Nenhuma atualização no Dontpad há 1 hora.")
    except Exception as e:
        print(f"⚠️ Erro ao enviar alerta de inatividade: {e}")


async def monitor_dontpad():
    """Monitora os links do Dontpad periodicamente."""
    print("🚀 Monitorando múltiplos links do Dontpad...")

    while True:
        for url in DONT_PAD_URLS:
            content = get_dontpad_content_selenium(url)

            if content is not None:
                print(f"🔍 [{url}] Verificado!")  # Debug: imprime no terminal

                if content != last_contents[url]:
                    await send_telegram_notification(url)
                    last_contents[url] = content  # Atualiza o último conteúdo
                    last_update_times[url] = datetime.now()  # Atualiza o tempo da última mudança

                # Verifica se faz mais de 1 hora sem mudanças e envia alerta
                if datetime.now() - last_update_times[url] > timedelta(seconds=NO_UPDATE_ALERT_INTERVAL):
                    await send_no_update_alert()
                    last_update_times[url] = datetime.now()  # Reseta o timer do alerta

        await asyncio.sleep(CHECK_INTERVAL)  # Aguarda antes da próxima verificação


# Executa o monitoramento assíncrono
if __name__ == "__main__":
    try:
        asyncio.run(monitor_dontpad())
    except Exception as e:
        print(f"🚨 Ocorreu um erro inesperado: {e}")
        restart_bot()
