# Ce script est exécuté par spark-submit dans l'environnement Docker
# Il lit les données Kafka, agrège le nombre de tickets par priorité dans une fenêtre glissante,
# et exporte les résultats en Parquet dans un dossier partagé.

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, window, to_timestamp
from pyspark.sql.types import (
    StructType, StructField, StringType, TimestampType, IntegerType, LongType
)

# 1. Initialisation de la session Spark
spark = SparkSession.builder \
    .appName("KafkaMongoStreamingProcessor") \
    .getOrCreate()

# Ajuster le niveau de log pour ne voir que les WARN et les erreurs
spark.sparkContext.setLogLevel("WARN")

print("Spark Session créée avec succès.")

# 2. Définition du Schéma (doit correspondre à votre producteur)
ticket_schema = StructType([
    StructField("ticket_id", StringType(), False),
    StructField("client_id", StringType(), False),
    StructField("priority", StringType(), True),
    StructField("status", StringType(), True),
    StructField("initial_resolution_time_estimate", LongType(), True),
    StructField("timestamp", StringType(), True),
    StructField("client_tier", StringType(), True),
    StructField("client_city", StringType(), True),
    StructField("support_team", StringType(), True),
])

# 3. Lecture en Streaming depuis Kafka
kafka_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka-broker:29092") \
    .option("subscribe", "support_tickets") \
    .option("startingOffsets", "latest") \
    .load()

# 4. Traitement et Agrégation
processed_df = kafka_df \
    .select(col("value").cast("string").alias("value"), col("timestamp").alias("kafka_time"))

# Appliquer le schéma pour extraire les données du champ 'value' (JSON)
json_df = processed_df \
    .select(from_json(col("value"), ticket_schema).alias("ticket_data"), col("kafka_time")) \
    .select("ticket_data.*", "kafka_time")

# Convertir le champ 'timestamp' en type Timestamp pour l'utiliser dans la fenêtre
data_stream = json_df.withColumn(
    "timestamp", 
    to_timestamp(col("timestamp"), "yyyy-MM-dd HH:mm:ss.SSS")
)

# Agrégation : Compte le nombre de tickets par priorité sur une fenêtre glissante
ticket_counts_df = data_stream \
    .withWatermark("timestamp", "1 minute") \
    .groupBy(
        # Fenêtre d'agrégation : 1 minute de durée, glissement toutes les 30 seconds
        window(col("timestamp"), "1 minute", "30 seconds").alias("time_window"),
        col("priority")
    ) \
    .count() \
    .withColumnRenamed("count", "total_tickets") \
    .orderBy(col("time_window").desc(), col("total_tickets").desc())


# 5. Écriture en Streaming dans un fichier Parquet
# Le chemin de sortie utilise le répertoire monté : /opt/app/
parquet_output_path = "file:///opt/app/output/ticket_counts"
checkpoint_path = "file:///opt/app/checkpoints/ticket_counts"

print(f"Les résultats de l'agrégation seront exportés en Parquet vers : {parquet_output_path}")

# Écrire les résultats en mode 'complete' pour les fenêtres glissantes
# ATTENTION: Le format Parquet ne supporte que les modes 'append' ou 'complete'
query = ticket_counts_df.writeStream \
    .format("parquet") \
    .option("path", parquet_output_path) \
    .option("checkpointLocation", checkpoint_path) \
    .outputMode("complete") \
    .trigger(processingTime='5 seconds') \
    .start()

# Attendre la fin du streaming (bloquant)
print("Démarrage du traitement de streaming...")
query.awaitTermination()
