import os
import signal
import sys
import threading

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, ProgrammingError

from src.cache.transaction import cache_categories
from src.dependencies import get_db
from src.kafka.consumer import KafkaConsumerWrapper
from src.kafka.producer import KafkaProducerWrapper
from src.routers import api_router


app = FastAPI()

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

KAFKA_SERVER = os.getenv("KAFKA_SERVER", "localhost:9093")
KAFKA_TOPIC = "create_transaction_topic"

kafka_producer = KafkaProducerWrapper(bootstrap_servers=KAFKA_SERVER)
kafka_consumer = KafkaConsumerWrapper(bootstrap_servers=KAFKA_SERVER, topic=KAFKA_TOPIC)


def start_consumer():
    """Run the Kafka consumer in a separate thread."""
    try:
        kafka_consumer.consume_messages()
    except Exception as e:
        print(f"Kafka consumer error: {e}")


def shutdown_handler(signum, frame):
    """
    Handle graceful shutdown by terminating the process when Ctrl+C or SIGTERM is received.
    """
    kafka_consumer.close()
    sys.exit(0)


def setup_signal_handlers():
    """
    Set up signal handlers for graceful shutdown (SIGINT for Ctrl+C, SIGTERM for termination).
    """
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)


def start_consumer_thread():
    """
    Start the Kafka consumer in a separate thread as a daemon so that it exits
    when the main process ends.
    """
    consumer_thread = threading.Thread(target=start_consumer, daemon=True)
    consumer_thread.start()


def setup_cache(db: Session):
    global cache_categories
    cache_categories.load_categories(db)


@app.on_event("startup")
def startup_event():
    """Executed when the app starts — handles missing DB/tables gracefully."""
    try:
        db = next(get_db())
        # Try setup cache only if DB is ready
        try:
            setup_cache(db)
        except (OperationalError, ProgrammingError) as e:
            print(f"Skipping setup_cache (DB not ready or tables missing): {e}")
    except Exception as e:
        print(f"Startup error: {e}")


def run_application():
    """Run application using Uvicorn."""
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    # Initialize signal handlers for graceful shutdown
    setup_signal_handlers()

    # Start Kafka consumer in a separate daemon thread
    start_consumer_thread()

    # Run application using: uvicorn main:app --reload
    run_application()
