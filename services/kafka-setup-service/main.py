from kafka import KafkaAdminClient
from kafka.cluster import ClusterMetadata
from kafka.errors import NoBrokersAvailable
from kafka.admin import NewTopic


def create_kafka_topic():
    try:
        metadata = ClusterMetadata(bootstrap_servers="kafka-broker:9092")
        brokers = metadata.brokers()

        if len(brokers) == 0:
            print("No brokers found.")

        for broker in brokers:
            print(f"Broker Node ID: {broker[0]}")
            print(f"Host: {broker[1]}")
            print(f"Port: {broker[2]}")
            print(f"Rack: {broker[3]}")
            print("-" * 40)  # Separator line for clarity

        admin = KafkaAdminClient(bootstrap_servers="kafka-broker:9092")

        topic_list = [
            NewTopic("track_updates", num_partitions=1, replication_factor=1)
            ]
        admin.create_topics(new_topics=topic_list)

        print("Topic(s) created successfully.")

    except NoBrokersAvailable as e:
        print(f"Error creating topic: {e}")
        raise e

if __name__ == "__main__":
    create_kafka_topic()
