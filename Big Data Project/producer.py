from kafka import KafkaProducer
import pandas as pd
import json
import time


KAFKA_BROKER = "localhost:9092"
FUSED_TOPIC = "media_stream"


df = pd.read_csv(r"/home/sunbeam/Desktop/BigData_Project/Project_2/media_data.csv")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_data_to_kafka():
    try:
        for _, row in df.iterrows():
            event = {
                "user_id": row["User_ID"],
                "session_id": row["Session_ID"],
                "device_id": row["Device_ID"],
                "video_id": row["Video_ID"],
                "duration_watched": round(row["Duration_Watched (minutes)"] * 60, 2),  # Convert to seconds
                "genre": row["Genre"],
                "country": row["Country"],
                "age": int(row["Age"]),
                "gender": row["Gender"],
                "subscription_status": row["Subscription_Status"],
                "ratings": row["Ratings"],
                "languages": row["Languages"],
                "device_type": row["Device_Type"],
                "location": row["Location"],
                "playback_quality": row["Playback_Quality"],
                "interaction_events": int(row["Interaction_Events"]),
                "timestamp": pd.Timestamp.now().isoformat(),  # Generate live timestamp
            }

            producer.send(FUSED_TOPIC, value=event)
            print(f"Sent to {FUSED_TOPIC}: {event}")

            time.sleep(1)
    except KeyboardInterrupt:
        print("Data streaming stopped.")
    finally:
        producer.close()

if __name__ == "__main__":
    print(f"Starting Kafka producer, streaming data from CSV to topic '{FUSED_TOPIC}'...")
    send_data_to_kafka()
