# 💸 Personal Finance Management System (PFMS)

**Framework**: FastAPI
**Database**: PostgreSQL
**Messaging**: Kafka
**Containerized With**: Docker & Docker Compose
**Project Entry Point**: `main.py`

## 📦 Overview

This is a **Personal Finance Management Application (PFMS)** that helps users:

- Record transactions
- Set and track budgets
- Visualize spending via statistics
- View financial summaries on a dashboard
- Manage users and administrators

All data is persisted in **PostgreSQL**. When a new transaction is created or updated, a **Kafka consumer** processes the message and updates the **`BudgetExpense`** table based on any relevant budget definitions.

## 🧩 Features

### 🔹 Modules

**User** User registration, login, and management
**Transaction** Full CRUD operations for income and expense tracking
**Budget** Set budget limits per category within a time range
**Stat** Generate analytical insights, pie charts, and line graphs
**Dashboard** Summarized view of financial health, recent activities, budget
**Admin** Manage access, roles, or audit data (future scope or optional)

### 🔄 Kafka Integration

- Kafka listens for **transaction creation or updates**
- When triggered, it checks if the transaction matches an existing **budget rule**
- If matched, it updates the `BudgetExpense` table accordingly

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL
- **Messaging**: Kafka + Zookeeper
- **ORM & Migration**: SQLAlchemy + Alembic
- **Containerization**: Docker & Docker Compose
- **Build tools**: Makefile (for automation)

---

📦 Docker Compose Files

- `docker-compose.yml`: base services (Kafka, Zookeeper)
- `docker-compose.local.yml`: includes FastAPI with local config
- `docker-compose.dev.yml`: includes PostgreSQL, FastAPI for development

Used together via the Makefile like this:

```bash
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.$(ENV).yml
```

## Run in local:

- make ENV=local up (Make sure that Kafka and Zookeeper running in Docker)
- Activate the venv
- Run: python main.py

## Run in Docker (All services by docker-compose):

🛠️ Docker Build & Entrypoint Logic:

📄 `docker/Dockerfile`

- Uses `python:3.10-slim`
- Installs `netcat-openbsd` to wait for PostgreSQL
- Copies source code and dependencies
- Uses `entrypoint.sh` to run migrations and launch app

🔄 Alembic Migrations (Only If table changes)

Create a New Migration:

```bash
make ENV=dev migrate
-> docker-compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml exec fastapi alembic revision --autogenerate -m "Your message"
```

Apply Migrations:

```bash
make ENV=dev upgrade
-> docker-compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml exec fastapi alembic upgrade head
```

Run:

```bash
make ENV=dev up
```

## Check for all services are running properly in Docker

✈️ Test:

- Use POSTMAN to test API endpoints.
