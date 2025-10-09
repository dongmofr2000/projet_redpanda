# Utilisation de l'image stable jupyter/pyspark-notebook qui inclut Python, Spark et Java.
FROM jupyter/pyspark-notebook

# Définir le répertoire de travail à l'intérieur du conteneur
WORKDIR /opt/app

# Installer les dépendances Python nécessaires pour Kafka et MongoDB (kafka-python et pymongo)
RUN pip install kafka-python pymongo

# NOTE: La commande 'install_packages pip' a été supprimée car elle n'est pas
# disponible dans l'image de base jupyter et pip est déjà présent.

# Ajouter votre code d'application (décommenter la section ci-dessous si vous avez des fichiers à copier)
# COPY . /opt/app
# CMD ["/opt/spark/bin/spark-submit", "votre_script_spark.py"]
