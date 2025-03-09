# Usa uma imagem leve do Python
FROM python:3.12-slim

# Instala pacotes necessários para o Chrome e o ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    fonts-liberation \
    libgbm-dev \
    libu2f-udev \
    libxi6 \
    libgconf-2-4 \
    && rm -rf /var/lib/apt/lists/*

# Baixa e instala o Google Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb || apt-get -fy install

# Baixa o ChromeDriver compatível
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1) && \
    wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}.0.0/linux64/chromedriver-linux64.zip" && \
    unzip chromedriver-linux64.zip && \
    mv chromedriver-linux64/chromedriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf chromedriver-linux64.zip chromedriver-linux64

# Define a variável de ambiente para o Selenium
ENV PATH="/usr/local/bin:$PATH"

# Define o diretório do app
WORKDIR /app
COPY . .

# Instala dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando para rodar o script
CMD ["python", "monitor_dontpad.py"]