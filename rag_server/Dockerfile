FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# On copie le reste des fichiers (app.py ET mon_document.pdf)
COPY . .

# On expose le port sur lequel Flask va tourner
EXPOSE 5000

CMD ["python", "app.py"]