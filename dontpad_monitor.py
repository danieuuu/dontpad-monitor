import requests
import time
import os
import threading

# Configurações do Telegram
TELEGRAM_TOKEN = os.getenv("8021907392:AAHf16JeFTa090Op9RLsUoqKPgiscDyYwpM")
CHAT_ID = os.getenv("7173683946")

def enviar_notificacao(mensagem):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": mensagem}
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print("✅ Notificação enviada para o Telegram!")
        else:
            print(f"❌ Falha ao enviar notificação: {response.status_code}")

    except Exception as e:
        print(f"❌ Erro ao enviar notificação: {e}")

def monitor_dontpad(link, intervalo=10):
    url = f"http://dontpad.com/{link}.body"
    conteudo_anterior = ""

    print(f"🔎 Monitorando: {url}")

    while True:
        try:
            resposta = requests.get(url)
            resposta.raise_for_status()
            
            conteudo_atual = resposta.text.strip()

            if conteudo_atual != conteudo_anterior:
                print(f"\n🔔 Alteração detectada em {link}!")
                print(f"Novo conteúdo:\n{conteudo_atual}\n")

                mensagem = f"🚨 *Alteração detectada no Dontpad!*\n\n🔗 Link: {url}\n\n📄 *Novo conteúdo:*\n{conteudo_atual}"
                enviar_notificacao(mensagem)
                
                conteudo_anterior = conteudo_atual

            time.sleep(intervalo)

        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar o link: {e}")
            time.sleep(intervalo)

# 🟢 Monitorar múltiplos links
links_para_monitorar = ["2defevereiro", "piguica", "splitfiction"]

for link in links_para_monitorar:
    thread = threading.Thread(target=monitor_dontpad, args=(link, 10))
    thread.start()
