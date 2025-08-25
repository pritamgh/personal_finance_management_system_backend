# Use official Python image
FROM python:3.10-slim

# Install netcat for entrypoint.sh
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only requirements first for caching
COPY ../requirements.txt .

# Install dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy all app source code from project root
COPY ../src ./src
COPY ../tests ./tests
COPY ../migrations ./migrations
COPY ../alembic.ini ./alembic.ini
COPY ../README.md ./README.md
COPY ../main.py ./main.py

# Copy entrypoint script
COPY docker/entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

# Expose port (FastAPI default is 8000)
EXPOSE 8000

# Run the app using your local command
# CMD ["python", "main.py"]
# Use custom entrypoint that runs migrations, then starts app
ENTRYPOINT ["./entrypoint.sh"]
