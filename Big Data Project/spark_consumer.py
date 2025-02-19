from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType

# MySQL Configuration
MYSQL_CONFIG = {
    'url': 'jdbc:mysql://192.168.101.83:3306/bigdata',
    'user': 'remote_user',
    'password': 'manager',
    'dbtable': 'media_stream',
    'driver': 'com.mysql.cj.jdbc.Driver'
}

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("KafkaToSparkToMySQL") \
    .getOrCreate()

# Define Schema for Incoming Kafka Data
schema = StructType([
    StructField("user_id", StringType(), True),
    StructField("session_id", StringType(), True),
    StructField("device_id", IntegerType(), True),
    StructField("video_id", IntegerType(), True),
    StructField("duration_watched", DoubleType(), True),
    StructField("genre", StringType(), True),
    StructField("country", StringType(), True),
    StructField("age", IntegerType(), True),
    StructField("gender", StringType(), True),
    StructField("subscription_status", StringType(), True),
    StructField("ratings", IntegerType(), True),
    StructField("languages", StringType(), True),
    StructField("device_type", StringType(), True),
    StructField("location", StringType(), True),
    StructField("playback_quality", StringType(), True),
    StructField("interaction_events", IntegerType(), True),
    StructField("timestamp", StringType(), True)
])

# Read data from Kafka
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "media_stream") \
    .load()

# Convert Kafka messages from binary to string
kafka_df = kafka_df.selectExpr("CAST(value AS STRING)")

# Parse JSON data
json_df = kafka_df.select(from_json(col("value"), schema).alias("data")).select("data.*")

# Apply transformation (filter invalid durations)
transformed_df = json_df.filter(col("duration_watched") > 0)

# Print incoming data to console for debugging
query_console = transformed_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .start()

# Function to write data to MySQL
def write_to_mysql(batch_df, batch_id):
    batch_df.write \
        .format("jdbc") \
        .option("url", MYSQL_CONFIG['url']) \
        .option("dbtable", MYSQL_CONFIG['dbtable']) \
        .option("user", MYSQL_CONFIG['user']) \
        .option("password", MYSQL_CONFIG['password']) \
        .option("driver", MYSQL_CONFIG['driver']) \
        .mode("append") \
        .save()

# Start MySQL writing process
query_mysql = transformed_df.writeStream \
    .foreachBatch(write_to_mysql) \
    .outputMode("append") \
    .start()

# Wait for queries to terminate
query_console.awaitTermination()
query_mysql.awaitTermination()