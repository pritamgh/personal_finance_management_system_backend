import json
from contextlib import contextmanager

from kafka import KafkaConsumer
from src.budget.services import budget_tracker
from src.dependencies import get_db
from src.models import Transaction


# Context manager to handle session manually for Kafka consumer
@contextmanager
def get_db_session():
    """
    Context manager to handle the lifecycle of a database session.

    This is used to manage the database session manually when consuming messages
    from Kafka. It ensures that the session is opened and closed properly, even
    in the event of an exception.

    Yields:
    - db: A database session instance.
    """
    db = next(get_db())  # Get the db session from get_db
    try:
        yield db
    finally:
        db.close()  # Ensure the session is closed after use


class KafkaConsumerWrapper:
    """
    A wrapper class for consuming messages from a Kafka topic and processing them.

    This class manages the KafkaConsumer and handles the deserialization of the messages.
    It also provides methods for consuming messages, processing them, and managing the
    lifecycle of a Kafka consumer connection.

    Attributes:
    - bootstrap_servers (str): The address of the Kafka broker.
    - topic (str): The Kafka topic to consume messages from.
    - consumer (KafkaConsumer): An instance of KafkaConsumer that reads messages
      from the Kafka topic.

    Methods:
    - __init__(self, bootstrap_servers: str, topic: str): Initializes the KafkaConsumerWrapper
      with the Kafka broker address and the topic name.
    - consume_messages(self): Starts consuming messages from the Kafka topic and processes them.
    - process_message(self, message: dict): Processes the consumed message and updates the budget.
    - close(self): Closes the KafkaConsumer connection.
    """

    def __init__(self, bootstrap_servers: str, topic: str):
        """
        Initializes the KafkaConsumerWrapper with the provided Kafka broker address and topic.

        Args:
        - bootstrap_servers (str): The address of the Kafka broker to connect to.
        - topic (str): The Kafka topic from which messages will be consumed.
        """
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        # Initialize the KafkaConsumer to consume messages from the specified topic
        self.consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id="budget-group",  # Consumer group ID for Kafka
            enable_auto_commit=True,  # Automatically commit offsets after processing
            value_deserializer=lambda x: json.loads(
                x.decode("utf-8")
            ),  # Deserialize messages from JSON
        )

    def consume_messages(self):
        """
        Starts consuming messages from the Kafka topic and processes each one.

        This method enters an infinite loop where it continuously consumes messages
        from Kafka, processes them, and commits the message offset to Kafka.
        It is typically called in the background to listen for and handle incoming messages.
        """
        print(f"Starting to consume messages from {self.topic}...")
        # Continuously consume messages from the Kafka topic
        for message in self.consumer:
            self.process_message(message.value)
            # Commit the offset after processing the message
            self.consumer.commit()

    def process_message(self, message: dict):
        """
        Processes the consumed Kafka message and updates the budget status.

        The message is assumed to contain a transaction, which is then used to update the
        budget status in the database.

        Args:
        - message (dict): The consumed message, expected to be a dictionary containing transaction data.
        """
        # Get the db session manually using the context manager
        with get_db_session() as db:
            print(f"Processing message: {message}")
            # Create a Transaction object from the message
            transaction = Transaction(**message)
            # Update the budget based on the transaction
            budget_tracker(transaction, db)

    def close(self):
        """
        Closes the KafkaConsumer connection.
        """
        self.consumer.close()
