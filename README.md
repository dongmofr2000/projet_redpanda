🚀 Projet : Pipeline de Streaming PySpark & Redpanda (Kafka)
Ce document sert de documentation pour la preuve de concept (POC) d'un pipeline d'analyse de données de support client en temps réel.
Il montre l'ingestion de données de tickets via Redpanda (Kafka), leur traitement par PySpark Streaming avec agrégation en fenêtre glissante, 
et l'exportation vers des fichiers Parquet pour le stockage analytique.


🏗️ 1. Architecture du Pipeline (Diagramme Mermaid)
Le diagramme de flux ci-dessous illustre l'architecture de votre pipeline de données, de la source (Producteur Python) au stockage final (Parquet).


<img width="1288" height="604" alt="image" src="https://github.com/user-attachments/assets/5f45bea3-191a-482f-b8da-d2ec20edd563" />
graph LR
    subgraph Producteur
        P[Producteur Python]
    end

    subgraph Broker_Kafka
        K(Redpanda / Kafka)
    end

    subgraph Processeur_Spark
        S[PySpark Streaming]
    end

    subgraph Destination
        D[Fichiers Parquet (Agrégations)]
    end

    P -->|Envoie Tickets JSON| K
    K -->|Lit en Temps Réel| S
    S -->|Fenêtrage 1 min / Watermark| S
    S -->|Écrit Résultats| D

Description du Flux :
1.	Producteur (P) : Génère des tickets de support fictifs au format JSON.
2.	Broker (K) : Redpanda (compatible Kafka) ingère et met en file d'attente les messages sur le topic support_tickets.
3.	Processeur (S) : PySpark lit le flux, applique une fenêtre glissante d'une minute sur l'horodatage (timestamp) pour compter les tickets par priorité,
4.	et utilise un watermark d'une minute pour gérer les données en retard.
5.	Destination (D) : Les résultats agrégés sont écrits sur le système de fichiers dans des fichiers Parquet.
🛠️ 2. Composants et Exécution du POC
Ce projet est entièrement conteneurisé. Les instructions ci-dessous supposent que vous êtes dans le répertoire racine du projet et que Docker Compose est installé.
A. Démarrage de l'Environnement
Le fichier docker-compose.yml construit les images Producteur et Processeur et démarre le broker Redpanda.
# 1. Construire les images et démarrer tous les services en arrière-plan
docker-compose up --build -d

B. Lancement du Producteur (Source)
Le producteur commence à envoyer des tickets au topic Kafka (support_tickets).
# 2. Exécuter le script du producteur dans son conteneur
docker exec -it ticket-producer python ticket_producer.py

C. Lancement du Processeur PySpark (ETL)
Le processeur Spark lit le flux, effectue l'agrégation, et écrit en mode append dans le répertoire d'export.
# 3. Exécuter le script PySpark (en s'assurant d'inclure les packages Kafka)
docker exec -it spark-processor /spark/bin/spark-submit \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0 \
    /opt/app/final_processor.py

D. Validation des Résultats
Après environ 90 à 120 secondes (pour que Spark clôture la première fenêtre de 1 minute), vous pouvez vérifier les fichiers Parquet :
# 4. Entrer dans le conteneur du processeur
docker exec -it spark-processor bash

# 5. Lister les fichiers Parquet exportés
ls -R /opt/app/output/ticket_counts

Vous devriez voir des fichiers nommés part-0000x-***.parquet.


🎥 3. Vidéo de Démonstration
Cette courte vidéo explique le fonctionnement du pipeline, depuis le lancement du producteur jusqu'à la vérification des fichiers Parquet générés par Spark.
Support Vidéo : Loom
Description	Lien d'Intégration
Démonstration du Pipeline ETL	[[Lien vers la Vidéo Loom de Démonstration]](https://www.loom.com/share/eb1422faadf04df5b8ca10dd998e974d?sid=055f35e1-9314-47e9-b45c-2915a90c930e)



