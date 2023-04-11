# es-connector
The ES-connector is set of Docker containers used for updating our Elasticsearch nodes using API requests with optional notification to external parties.

## Architecture overview

## Getting started
After cloning this repo, you should have a map structure like this:

```
|-- Info.md
|-- api
|-- elasticsearch
|-- proxy
```

We need to do some configuration stuff first, we'll start in de elasticsearch map

### 1: Elasticsearch / Kibana

```
Before starting a container, configure the .env file by copying the env-example file to .env

# Password for the 'elastic' user (at least 6 characters)
ELASTIC_PASSWORD=dummypassword

# Password for the 'kibana_system' user (at least 6 characters)
KIBANA_PASSWORD=anotherdummypassword

# Version of Elastic products (8.6.1 is a version)
STACK_VERSION=8.6.1

# Set the cluster name
CLUSTER_NAME=my_es_cluster

# Set to 'basic' or 'trial' to automatically start the 30-day trial
LICENSE=basic

# Port to expose Elasticsearch HTTP API to the host (9200 is default)
ES_PORT=9200

# Port to expose Kibana to the host (5601 is default)
KIBANA_PORT=<5601

# Increase or decrease based on the available host memory (in bytes)
MEM_LIMIT=1073741824

# Project namespace (defaults to the current folder name if not set)
COMPOSE_PROJECT_NAME=es-cdn
```

The 'elasticsearch' map contains a couple of Docker compose files:

- docker-compose-dev.yml (development with only 1 network)
- docker-compose.yml (production with 2 networks)
- docker-compose-setup-force.yml (force renewal of SSL certificates within the setup)

If you need to run a compose file other then then default-compose.yml you should specify the -f param:
```
docker compose -f docker-compose-dev.yml -f docker-compose-setup-force.yml up --build
```


