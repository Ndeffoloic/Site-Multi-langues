# Utiliser l'image officielle de Python 3.11
FROM python:3.11-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /multilang_site

# Copier le fichier requirements.txt dans le conteneur
COPY requirements.txt .

# Mettre à jour pip et installer les dépendances avec un temps limite augmenté
RUN pip install --upgrade pip
RUN pip install --default-timeout=1000 -r requirements.txt

# Copier tout le contenu du projet dans le conteneur
COPY . .

# Exposer le port que Django utilise par défaut
EXPOSE 8000

# Commande pour démarrer le serveur Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
