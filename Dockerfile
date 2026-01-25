FROM python:3.9-slim

# Instala mdbtools (Driver do Access) e gunicorn (Servidor Web)
RUN apt-get update && apt-get install -y \
    mdbtools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copia o código do servidor
COPY api_server.py .

# Expõe a porta e roda o servidor com Gunicorn (Produção)
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "api_server:app"]
