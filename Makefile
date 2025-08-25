# # Default environment (can be overridden via command line ex: make ENV=local up)
# ENV ?= local

# # Compose file paths (relative to Makefile)
# COMPOSE = docker-compose -f docker/docker-compose.yml -f docker/docker-compose.$(ENV).yml

# # Commands
# up:
# 	$(COMPOSE) up -d --build

# down:
# 	$(COMPOSE) down

# restart: down up

# logs:
# 	$(COMPOSE) logs -f

# migrate:
# 	$(COMPOSE) exec fastapi alembic revision --autogenerate -m "Create initial tables"

# upgrade:
# 	$(COMPOSE) exec fastapi alembic upgrade head

# bash:
# 	$(COMPOSE) exec fastapi /bin/bash

# config:
# 	$(COMPOSE) config


# Build Docker image for deployment (used by CI/CD)
docker-build:
	docker build -f docker/Dockerfile -t $(REGISTRY)/$(ECR_REPOSITORY):$(IMAGE_TAG) docker/

# Push Docker image to ECR (used by CI/CD)
docker-push:
	docker push $(REGISTRY)/$(ECR_REPOSITORY):$(IMAGE_TAG)
