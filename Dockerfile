# ===================================
# Dockerfile pour Django + Celery
# ===================================

# Image de base
FROM python:3.12-slim

# Variables d'environnement pour Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Définir le répertoire de travail
WORKDIR /app/backend

# Installer les dépendances système
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev curl  netcat-openbsd make && \
    apt-get clean

# Copier les fichiers requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --upgrade pip
RUN pip install  -r requirements.txt

# Copier tout le projet
COPY . .

# Exposer le port de Django
EXPOSE 8000
# Set up the entrypoint
COPY scripts/entrypoint.sh /entrypoint.sh

COPY scripts/production_data.sh /production_data.sh
RUN chmod +x /entrypoint.sh /production_data.sh

# Commande par défaut

ENTRYPOINT ["/entrypoint.sh"]
