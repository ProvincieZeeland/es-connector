# es-connector
The ES-connector is set of Docker containers used for updating our Elasticsearch nodes using API requests with optional notification to external parties. My first Python project after 23 years using PHP code :-) 
 
## Version history

### 0.1 Proof of Concept
The PoC is a fully functional but pretty basic solution which supports:

- Different environments (development, accept, production) using .env / Docker compose files.
- Authentication based on Bearer tokens using decorators.
- Receive and validate posted JSON data and map it to an Elasticsearch structure.
- Add, update and delete mapped metadata in Elasticsearch.
- If referred content is a PDF file; get PDF from Sharepoint storage, extract text and add to metadata for full text searches.
- Notify external parties about the change (webhook).
- Serve metadata (JSON format) and content (eg PDF) format upon request.

**TODO**

- Support for API versioning (should we use a decicated API gateway like Kong or Tyk ?).
- Swagger / OpenAPI specs.
- Cockpit container for observability (logging, monitoring, display transactions, stats).
- Research for log management (filebeat, metricbeat, Logstash etc).
- Token management (JWT payloads).
- Elasticsearch performance tuning.
- Elasticsearch security best practices.
- Perfomance tuning Python / Flask.
- Best practices / tuning Docker containers.
- Search endpoint

## Architecture overview

## Getting started
After cloning this repo, you should have a map structure like this:

```
|-- Info.md
|-- api
|-- elasticsearch
|-- proxy
```
 
- [1: Configure Elasticsearch / Kibana](https://github.com/ProvincieZeeland/es-connector/wiki/1:-Configure-Elasticsearch--&-Kibana-nodes)
- [2: Setup Elasticsearch mappings etc.](https://github.com/ProvincieZeeland/es-connector/wiki/2:-Setup-Elasticsearch-mappings-etc.)
- [3: Configure the API](https://github.com/ProvincieZeeland/es-connector/wiki/3:-Configure-the-API)
- [4: Firing up the proxy](https://github.com/ProvincieZeeland/es-connector/wiki/4:-Firing-up-the-proxy)

