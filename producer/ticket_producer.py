# --------------------------------------------------------------------------------
# SCRIPT PYTHON DU PRODUCTEUR
# Envoie des tickets de support enrichis vers Kafka.
# --------------------------------------------------------------------------------
from kafka import KafkaProducer
import json
import time
import random
from uuid import uuid4
from datetime import datetime

# --- CONFIGURATION ---
# ATTENTION : Pour se connecter depuis l'hôte (votre PC),
# on utilise le port exposé (9092), PAS le port interne (29092).
KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'client_tickets'

# Liste statique des IDs clients pour assurer le succès de la jointure PySpark
CLIENT_IDS = ["C1001", "C1002", "C1003", "C1004", "C1005", "C1006"]

def generate_ticket():
    """Génère un ticket de support avec des données réalistes."""
    priorities = ["Critique", "Haute", "Moyenne", "Basse"]
    statuses = ["Ouvert", "En Cours", "En Attente", "Fermé"]
    
    # Choisir un client ID qui existe dans notre table statique
    client_id = random.choice(CLIENT_IDS)
    
    # L'estimation de temps est essentielle pour le calcul de l'agrégation
    if client_id in ["C1001", "C1003", "C1005"]: # Clients Premium/Gold ont des tickets plus rapides
        resolution_estimate = random.randint(30, 180) # 30 mins à 3 heures
    else:
        resolution_estimate = random.randint(120, 480) # 2 heures à 8 heures

    return {
        "ticket_id": str(uuid4()),
        "client_id": client_id,
        "priority": random.choice(priorities),
        "status": random.choice(statuses),
        "initial_resolution_time_estimate": resolution_estimate,
        "timestamp": datetime.now().isoformat(timespec='milliseconds')
    }

def run_producer():
    """Initialise et exécute le producteur Kafka."""
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            api_version=(0, 10, 2)
        )
        print(f"Producteur Kafka connecté à {KAFKA_BROKER}")
        
        while True:
            ticket = generate_ticket()
            producer.send(KAFKA_TOPIC, value=ticket)
            print(f"Ticket {ticket['ticket_id']} envoyé pour le client {ticket['client_id']} ({ticket['priority']})")
            time.sleep(random.uniform(0.5, 1.5)) # Envoie un ticket toutes les 0.5 à 1.5 secondes

    except Exception as e:
        print(f"Erreur de connexion au Producteur Kafka: {e}")
        # Laisse un peu de temps avant de réessayer
        time.sleep(5) 
        run_producer()

if __name__ == "__main__":
    run_producer()
