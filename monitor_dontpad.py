import time
import asyncio
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
CHECK_INTERVAL = 600  # Tempo em segundos entre verificações

bot = Bot(token=BOT_TOKEN)

# Dicionário para armazenar o último conteúdo de cada link
last_contents = {url: "" for url in DONT_PAD_URLS}


def get_dontpad_content_selenium(url):
    """Acessa o Dontpad e retorna o texto digitado lá."""
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
    except Exception as e:
        print(f"⚠️ Erro ao acessar o Dontpad ({url}): {e}")
        return None


async def send_telegram_notification(url):
    """Envia uma mensagem para o Telegram informando que houve atualização."""
    message = f"📢 O conteúdo do Dontpad foi atualizado!\n🔗 {url}"
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        print(f"⚠️ Erro ao enviar mensagem no Telegram: {e}")


print("🚀 Monitorando múltiplos links do Dontpad...")

# Criar um loop assíncrono para rodar sem fechar
loop = asyncio.get_event_loop()

while True:
    for url in DONT_PAD_URLS:
        content = get_dontpad_content_selenium(url)

        if content is not None:
            print(f"🔍 [{url}] Texto atualizado!")  # Debug: imprime no terminal

            if content != last_contents[url]:
                loop.run_until_complete(send_telegram_notification(url))
                last_contents[url] = content  # Atualiza o último conteúdo

    time.sleep(CHECK_INTERVAL)  # Aguarda antes da próxima verificação
