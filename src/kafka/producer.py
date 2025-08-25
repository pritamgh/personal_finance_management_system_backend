import json

from kafka import KafkaProducer


class KafkaProducerWrapper:
    """
    A wrapper class around KafkaProducer to simplify the process of sending
    JSON-encoded messages to a Kafka topic.

    Attributes:
    - bootstrap_servers (str): The address of the Kafka broker to connect to.
    - producer (KafkaProducer): An instance of the KafkaProducer used for sending messages.

    Methods:
    - __init__(self, bootstrap_servers: str): Initializes the KafkaProducerWrapper with
      the given bootstrap servers.
    - send_message(self, topic: str, message: dict): Sends a JSON-encoded message to the
      specified Kafka topic.
    - close(self): Closes the KafkaProducer connection.
    """

    def __init__(self, bootstrap_servers: str):
        """
        Initializes the KafkaProducerWrapper with the provided Kafka broker address.

        Args:
        - bootstrap_servers (str): The address of the Kafka broker to connect to.
        """
        self.bootstrap_servers = bootstrap_servers
        # Initialize the KafkaProducer with the provided bootstrap_servers.
        # The value_serializer ensures that the message is serialized into JSON and encoded as UTF-8.
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

    def send_message(self, topic: str, message: dict):
        """
        Sends a message to the specified Kafka topic. The message is serialized into
        JSON format before sending.

        Args:
        - topic (str): The Kafka topic to which the message will be sent.
        - message (dict): The message to be sent, in dictionary format. It will be
          serialized to JSON before sending.
        """
        print(f"Sending message {message} to Kafka topic {topic}")
        # Send the message to the specified Kafka topic
        self.producer.send(topic, message)
        # Ensure that the message is flushed to Kafka immediately
        self.producer.flush()

    def close(self):
        """
        Closes the KafkaProducer connection.
        """
        self.producer.close()
