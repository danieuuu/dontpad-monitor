import requests
import time

# Configurações do Discord
WEBHOOK_URL = "https://discord.com/api/webhooks/1348142861127782420/iuxokzE5I7fcnnqbcTlfAqkPHc4vET6cUJuWd_Lbe3JASEO_f4VxSk-_bAx0f0eU1LQm"

def enviar_notificacao(mensagem):
    try:
        payload = {
            "content": mensagem
        }
        response = requests.post(WEBHOOK_URL, json=payload)
        
        if response.status_code == 204:
            print("✅ Notificação enviada para o Discord!")
        else:
            print(f"❌ Falha ao enviar notificação para o Discord: {response.status_code}")

    except Exception as e:
        print(f"❌ Erro ao enviar notificação para o Discord: {e}")

def monitor_dontpad(link, intervalo=10):
    url = f"http://dontpad.com/{link}"
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

                mensagem = f"🔗 Link: {url}\n\n📄 Novo conteúdo:\n{conteudo_atual}"
                enviar_notificacao(mensagem)
                
                conteudo_anterior = conteudo_atual

            time.sleep(intervalo)

        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar o link: {e}")
            time.sleep(intervalo)

# Monitorar links
links_para_monitorar = ["2defevereiro", "piguica", "splitfiction"]

for link in links_para_monitorar:
    monitor_dontpad(link)