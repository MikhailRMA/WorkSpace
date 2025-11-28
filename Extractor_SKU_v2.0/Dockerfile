FROM python:3.11-slim

# Устанавливаем необходимые системные пакеты
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements и устанавливаем Python-зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы
COPY . .

# Запускаем приложение
CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0