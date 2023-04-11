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

### 1: Elasticsearch / Kibana
We need to do some configuration stuff first, we'll start in de elasticsearch map:

```
.
|-- docker-compose-dev.yml
|-- docker-compose-setup-force.yml
|-- docker-compose.yml
|-- env-example
|-- setup.txt
```

Before starting a container, configure the .env file by copying the env-example file to .env and open in your favourite editor

```
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

You might have noticed several Docker compose files:

- docker-compose-dev.yml (development with 2 nodes but only 1 network)
- docker-compose.yml (production with 2 nodes and 2 ACC / PROD networks)
- docker-compose-setup-force.yml (force renewal of SSL certificates within the setup)

If you need to run a compose file other then then default-compose.yml you should specify the -f param:
```
docker compose -f docker-compose-dev.yml -f docker-compose-setup-force.yml up --build -d

[+] Running 4/4
 ✔ Container es-cdn-setup-1  Created                                                                                                                                                                                                  0.1s 
 ✔ Container es-db           Created                                                                                                                                                                                                  0.2s 
 ✔ Container es-db2          Created                                                                                                                                                                                                  0.1s 
 ✔ Container es-kibana       Created                                                                                                                                                                                                  0.1s 
Attaching to es-cdn-setup-1, es-db, es-db2, es-kibana
es-cdn-setup-1  | Remove old ca (config/certs/ca.zip)
es-cdn-setup-1  | Remove old ca (config/certs/certs.zip)
es-cdn-setup-1  | Creating CA
es-db           | Created elasticsearch keystore in /usr/share/elasticsearch/config/elasticsearch.keystore
es-db2          | Created elasticsearch keystore in /usr/share/elasticsearch/config/elasticsearch.keystore
es-cdn-setup-1  | Archive:  config/certs/ca.zip
es-cdn-setup-1  |    creating: config/certs/ca/
es-cdn-setup-1  |   inflating: config/certs/ca/ca.crt  
es-cdn-setup-1  |   inflating: config/certs/ca/ca.key  
es-cdn-setup-1  | Creating certs
es-cdn-setup-1  | Archive:  config/certs/certs.zip
es-cdn-setup-1  |    creating: config/certs/esnode1/
es-cdn-setup-1  |   inflating: config/certs/esnode1/esnode1.crt  
es-cdn-setup-1  |   inflating: config/certs/esnode1/esnode1.key  
es-cdn-setup-1  |    creating: config/certs/esnode2/
es-cdn-setup-1  |   inflating: config/certs/esnode2/esnode2.crt  
es-cdn-setup-1  |   inflating: config/certs/esnode2/esnode2.key  
es-cdn-setup-1  | Setting file permissions
..
..
..
es-cdn-setup-1  | Good to go!
es-cdn-setup-1 exited with code 0
..
..
es-kibana       | [2023-04-11T13:19:18.289+00:00][INFO ][status] Kibana is now available
```





