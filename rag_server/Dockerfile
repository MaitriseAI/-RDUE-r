# Utiliser une image Python 3.11 légère
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Mettre à jour pip
RUN pip install --upgrade pip

# Copier le dossier du cache local D'ABORD
COPY wheelhouse /wheelhouse

# Copier le fichier des dépendances
COPY requirements.txt .

# Installer les dépendances EN UTILISANT LE CACHE LOCAL
# --no-index : Empêche pip de chercher les paquets sur internet
# --find-links=/wheelhouse : Indique à pip de chercher les paquets dans notre dossier local
RUN pip install --find-links=/wheelhouse -r requirements.txt

# Copier le reste de l'application
COPY . .

# Exposer le port
EXPOSE 5000

# Lancer le serveur
CMD ["python", "app.py"]
