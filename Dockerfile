FROM python:3.10-slim

# Instalar bibliotecas do sistema necessárias para o OpenSlide
RUN apt-get update && apt-get install -y \
    libopenslide0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expor a porta 5000
EXPOSE 5000

# Comando para rodar o servidor em produção com Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "viewer:app"]
