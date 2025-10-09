# Utilise une image Python légère et stable pour le producteur Kafka.
# L'utilisation de python:3.9-slim est un bon choix pour réduire la taille du conteneur.
FROM python:3.9-slim

# Définit le répertoire de travail à l'intérieur du conteneur.
WORKDIR /app

# Installe la dépendance nécessaire pour communiquer avec Kafka.
RUN pip install kafka-python

# Copie tous les fichiers du répertoire local 'ticket-producer' dans le répertoire /app du conteneur.
# Assurez-vous que votre script Python (ex: producer.py) est bien dans ce dossier.
COPY . /app/

# Commande par défaut pour exécuter le script du producteur.
# Remplacez 'producer.py' par le nom réel de votre fichier si nécessaire.
CMD ["python", "producer.py"]
