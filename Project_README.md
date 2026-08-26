# Jensen IoT Platform

[![CI](https://github.com/muhaka-1/jensen-IOT-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/muhaka-1/jensen-IOT-lab/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-REST_API-000000?logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-Cache-DC382D?logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Orchestration-326CE5?logo=kubernetes&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI-2088FF?logo=githubactions&logoColor=white)

# About This Project
A complete **containerized IoT data platform** developed as a final project for
the JENSEN IoT & Embedded Systems program.

The project demonstrates an end-to-end IoT backend architecture where
simulated devices send measurements to a REST API, data is validated and
persisted in PostgreSQL, frequently accessed latest measurements are served
through Redis, and the application is tested and built automatically through
GitHub Actions.

The application is also deployed to a local Kubernetes cluster using Minikube,
with multiple replicas, a Kubernetes Service, horizontal scaling and
self-healing.

### Author

Muhammad Jubayer Akanda

IoT & Embedded Systems Student
Sweden

Technical Focus

IoT · Embedded Systems · Python · C/C++ · REST APIs · Docker ·
PostgreSQL · Redis · Kubernetes · CI/CD · GitHub Actions

---

## Project at a Glance

```text
IoT Sensors
     │
     │ HTTP POST /measurements
     ▼
┌─────────────────────┐
│      Flask API      │
│                     │
│ • REST endpoints    │
│ • Validation        │
│ • Cache-aside       │
└──────┬─────────┬────┘
       │         │
       │ SQL     │ Cache read/write
       ▼         ▼
┌────────────┐ ┌────────────┐
│ PostgreSQL │ │   Redis    │
│            │ │            │
│ Historical │ │ Latest     │
│ data       │ │ measurement│
└────────────┘ └────────────┘


             Git Push / PR
                  │
                  ▼
        ┌───────────────────┐
        │   GitHub Actions  │
        │                   │
        │ pytest + Docker   │
        └───────────────────┘


          Kubernetes / Minikube
                  │
                  ▼
        ┌───────────────────┐
        │ Kubernetes Service│
        └─────────┬─────────┘
                  │
                  ▼
        ┌───────────────────┐
        │    Deployment     │
        │                   │
        │   3 API replicas  │
        └───┬────┬────┬────┘
            │    │    │
           Pod  Pod  Pod

📐 Detailed architecture:
docs/architecture.md

🖼️ Architecture diagram:
docs/architecture.png

### Why This Project Matters

This project was designed to demonstrate practical engineering skills across
the complete lifecycle of an IoT backend system:

Device → API → Validation → Database → Cache → Testing → CI → Containers → Kubernetes

Rather than implementing only an API, the project focuses on how the
components work together as a distributed system.

# Project Structure

jensen-IOT-lab/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── api/
│   ├── app.py
│   ├── cache.py
│   ├── db.py
│   ├── validation.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pytest.ini
│   │
│   ├── templates/
│   │   └── index.html
│   │
│   └── tests/
│       └── test_validation.py
│
├── database/
│   └── init.sql
│
├── docs/
│   ├── architecture.md
│   ├── architecture.png
│   ├── lab-guide.md
│   ├── reflection.md
│   ├── sql-queries.sql
│   │
│   └── screenshots/
│       ├── M1_API_Validation.pdf
│       ├── M1_Measurments.pdf
│       ├── M1_SQL.pdf
│       ├── M2_rediskeys_cache-hitt_cache-miss.pdf
│       ├── M3_CI.pdf
│       ├── M3_Minikube_service.pdf
│       ├── M3_Scaling.pdf
│       ├── M3_Self-healing.pdf
│       └── M3_dashboard.pdf
│
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
│
├── simulator/
│   ├── simulator.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker-compose.yml
├── README.md
└── .gitignore

### The implementation demonstrates:

REST API development
IoT data ingestion
Input validation
Persistent data storage
Cache-aside architecture
Containerization
Automated testing
Continuous Integration
Kubernetes orchestration
Horizontal scaling
Self-healing
Technical documentation
Technical Highlights
1. REST API

The backend is implemented using Python and Flask.

### The API provides endpoints for:

GET  /health
GET  /devices
GET  /measurements
POST /measurements
GET  /devices/{device_id}/measurements
GET  /devices/{device_id}/latest

The API acts as the controlled entry point for all sensor data.

This prevents IoT devices from accessing the database directly and provides a
clear boundary for validation, business logic and persistence.

### 2. Input Validation

Incoming measurements are validated before they are stored.

The validation layer checks the structure and values of incoming data and
prevents invalid measurements from entering PostgreSQL.

Example valid measurement:

        {
        "device_id": "sensor-001",
        "temperature": 27.5,
        "humidity": 55.0,
        "battery": 85
        }

Invalid data is rejected using appropriate HTTP status codes.

Validation logic:

        api/validation.py

Automated tests:

        api/tests/

### 3. PostgreSQL Persistent Storage

PostgreSQL is used as the system of record for IoT measurements.

The database stores historical measurements so that data remains available
after application or cache restarts.

Database initialization:

        database/init.sql

The architecture deliberately separates:

        PostgreSQL = persistent historical data
        Redis      = performance optimization

This means Redis can be lost without losing the historical measurement data.

### 4. Redis Cache-Aside Architecture

Redis is used to improve access to the latest measurement for each device.

The implementation follows the cache-aside pattern.

                GET /devices/{id}/latest
                            │
                            ▼
                     ┌─────────────┐
                     │    Redis    │
                     └──────┬──────┘
                            │
                    ┌───────┴───────┐
                    │               │
                   HIT             MISS
                    │               │
                    ▼               ▼
                 Return       PostgreSQL
                 cached            │
                 value             ▼
                              Store in Redis
                                   │
                                   ▼
                                Return

This provides fast access to frequently requested latest measurements while
keeping PostgreSQL as the persistent source of truth.

### 5. Docker & Docker Compose

The complete local platform runs using Docker Compose.

The environment consists of:

            ┌──────────────────────────────────────┐
            │          Docker Compose              │
            │                                      │
            │  ┌───────┐  ┌───────────┐            │
            │  │  API  │  │ Simulator │            │
            │  └───────┘  └───────────┘            │
            │                                      │
            │  ┌────────────┐  ┌─────────┐         │
            │  │ PostgreSQL │  │  Redis  │         │
            │  └────────────┘  └─────────┘         │
            │                                      │
            └──────────────────────────────────────┘

Start the complete environment:

        docker compose up --build -d

Check services:

        docker compose ps

Expected services:

        api
        simulator
        db
        redis
### 6. IoT Sensor Simulator

The project contains three simulated IoT sensors.

        sensor-001
        sensor-002
        sensor-003

The simulator sends measurements containing:

        Temperature
        Humidity
        Battery
        Device ID
        Timestamp

The simulator communicates with the backend through the REST API rather than
accessing PostgreSQL directly.

This reflects a more realistic IoT architecture where devices communicate
with an application/API layer.

# ##7. Automated Testing

The project uses pytest for automated testing.

Run the test suite:

        docker compose exec api python -m pytest -q

The tests verify application behaviour, including input validation.

Testing is integrated into the CI pipeline so that changes are automatically
verified before being considered complete.

### 8. Continuous Integration

GitHub Actions provides automated CI.

Workflow:

        Developer
        │
        │ git push / pull request
        ▼
        GitHub
        │
        ▼
        GitHub Actions
        │
        ├── Checkout repository
        │
        ├── Setup Python 3.12
        │
        ├── Install dependencies
        │
        ├── Run pytest
        │
        └── Build Docker image

Workflow configuration:

        .github/workflows/ci.yml

The CI pipeline ensures that:

Dependencies can be installed.
Automated tests pass.
The application Docker image can be built.
CI Status

The badge at the top of this README displays the current CI status.

### 9. Kubernetes Deployment

The application is also deployed to Kubernetes using Minikube.

Kubernetes resources:

k8s/
├── deployment.yaml
└── service.yaml

The Deployment runs three API replicas.

                 Kubernetes Service
                        │
             ┌──────────┼──────────┐
             │          │          │
             ▼          ▼          ▼
          ┌─────┐    ┌─────┐    ┌─────┐
          │Pod 1│    │Pod 2│    │Pod 3│
          └─────┘    └─────┘    └─────┘

Check the deployment:

kubectl get deployment

Check the pods:

kubectl get pods -l app=jensen-iot-api

Check the Service:

kubectl get service jensen-iot-api
 
### 10. Kubernetes Scaling

The Deployment can be horizontally scaled.

Example:

        kubectl scale deployment jensen-iot-api --replicas=5

Verify:

        kubectl get pods -l app=jensen-iot-api

The deployment can then be returned to three replicas:

        kubectl scale deployment jensen-iot-api --replicas=3

This demonstrates horizontal scaling using Kubernetes.

### 11. Kubernetes Self-Healing

Kubernetes maintains the desired number of replicas.

To demonstrate self-healing:

        kubectl get pods -l app=jensen-iot-api

Delete one Pod:

        kubectl delete pod <POD-NAME>

Then check the Pods again:

        kubectl get pods -l app=jensen-iot-api

Kubernetes automatically creates a replacement Pod.

This demonstrates the reconciliation behaviour of the Kubernetes Deployment
controller.

### 12. SQL

The project includes the three mandatory SQL operations required by the
assignment:

        Count all measurements
        SELECT COUNT(*)
        FROM measurements;
        Calculate average temperature
        SELECT AVG(temperature)
        FROM measurements;
        Retrieve measurements from the last 24 hours
        SELECT *
        FROM measurements
        WHERE created_at >= NOW() - INTERVAL '24 hours';

The queries are documented in:

        docs/sql-queries.sql

Running PostgreSQL

Open the PostgreSQL client:

        docker compose exec db psql -U student -d jensen_iot

Run the SQL queries and exit with:

        \q
API Verification

Health check:

        curl.exe http://localhost:5001/health

Expected:

        {
        "status": "ok"
        }

List devices:

curl.exe http://localhost:5001/devices

List measurements:

curl.exe http://localhost:5001/measurements


Quick Start
1. Clone the repository
git clone <YOUR-REPOSITORY-URL>
cd jensen-IOT-lab
2. Start Docker Compose
docker compose up --build -d
3. Verify services
docker compose ps
4. Run tests
docker compose exec api python -m pytest -q
5. Test the API
curl.exe http://localhost:5001/health
6. View simulator logs
docker compose logs -f simulator
Kubernetes Quick Start

Start Minikube:

minikube start --driver=docker

Load the application image:

minikube image load jensen-iot-api:lab

Deploy:

kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

Check:

kubectl get deployment
kubectl get pods
kubectl get service

Get the Service URL:

minikube service jensen-iot-api --url
Documentation
Document	Description
Architecture	System architecture and data flows
Architecture Diagram	Visual representation of the platform
Reflection	Technical reflection and design decisions
SQL Queries	Mandatory SQL queries
Lab Guide	Original course instructions
docs/screenshots/	Milestone verification evidence
Milestone Completion
Milestone 1 — IoT Data API

Implemented:

REST API
Device endpoints
Measurement endpoints
Input validation
HTTP status codes
PostgreSQL persistence
Measurement retrieval
Latest measurement endpoint
Automated tests
Milestone 2 — Database & Cache

Implemented:

PostgreSQL integration
Redis integration
Cache-aside strategy
Cache hit behaviour
Cache miss behaviour
PostgreSQL fallback
Latest-measurement caching
Persistent historical measurements
Milestone 3 — CI & Kubernetes

Implemented:

GitHub Actions CI
Automated pytest execution
Docker image build
Kubernetes Deployment
Three API replicas
Kubernetes Service
Horizontal scaling
Self-healing
Minikube deployment
Milestone 4 — Documentation

Completed:

Professional project README
Architecture documentation
Architecture diagram
SQL documentation
Reflection
Verification evidence
CI configuration
Kubernetes documentation
Engineering Decisions
API instead of direct database access

### IoT devices communicate with the API instead of connecting directly to
PostgreSQL.

This provides a controlled application boundary where authentication,
validation, business rules and persistence logic can be introduced without
requiring changes to the database architecture.

### PostgreSQL as the source of truth

Historical measurements require reliable persistent storage.

PostgreSQL is therefore used as the primary data store.

Redis is deliberately treated as a cache rather than the authoritative
database.

### Redis for latest measurements

The latest measurement is frequently requested and is therefore a suitable
candidate for caching.

Using Redis reduces unnecessary database reads while PostgreSQL continues to
provide durable historical storage.

### Kubernetes replicas

Multiple API replicas improve availability and demonstrate how the application
can scale horizontally.

If one Pod fails, Kubernetes replaces it to maintain the desired state.

Reliability Model

The system separates persistent storage from caching:

                 ┌───────────────┐
                 │     Redis     │
                 │   Cache       │
                 └───────┬───────┘
                         │
                     Performance
                         │
                         ▼
                 ┌───────────────┐
                 │  Flask API    │
                 └───────┬───────┘
                         │
                      Persistent
                         │
                         ▼
                 ┌───────────────┐
                 │  PostgreSQL   │
                 │ Source of     │
                 │ Truth         │
                 └───────────────┘

If Redis becomes unavailable, PostgreSQL remains the persistent source of
historical data.

If PostgreSQL becomes unavailable, new measurements cannot be persisted and
cache misses cannot be resolved from the database.

Known Limitations

This is an educational project designed to demonstrate IoT, backend,
containerization and orchestration concepts.

It is not intended as a production deployment.

### urrent limitations include:

IoT devices are simulated.
Minikube is used instead of a production Kubernetes cluster.
No production ingress or external load balancer is configured.
Authentication and authorization are outside the project scope.
TLS is not configured.
Redis is used as a cache rather than persistent storage.
CI builds the Docker image but does not publish it to a container registry.
Production monitoring and centralized logging are not implemented.

These limitations are intentional or outside the scope of the course project.

### Skills Demonstrated
Backend Development        Python               Flask          REST APIs       HTTP                JSON
Input validation           Error handling       Databases      PostgreSQL      SQL                 CRUD operations
Persistent storage         Aggregation queries  Caching         Redis          Cache-aside pattern  Cache hit/miss behaviour
Database fallback           DevOps              Docker         Docker Compose      Git              GitHub
GitHub Actions          Continuous Integration  Kubernetes      Deployments     Pods                Services
Replicas                    Scaling             Self-healing    Minikube        kubectl             Software Engineering
Modular application       Automated testing     Architecture documentation                          Technical troubleshooting
System design               Failure analysis

### What I Learned

Through this project I gained practical experience in designing and operating
a small distributed IoT platform.

The most important engineering concepts demonstrated by the project are:

Separating device communication from database access through an API.
Validating data before persistence.
Separating durable storage from caching.
Using cache-aside to optimize frequently accessed data.
Automating verification through CI.
Packaging applications using Docker.
Deploying replicated services with Kubernetes.
Demonstrating scaling and self-healing behaviour.
Documenting architecture and technical decisions.
Project Evidence

Verification screenshots and demonstration evidence are available in:

        docs/screenshots/

### The evidence covers:

API validation
PostgreSQL measurements
SQL queries
Redis cache hit/miss
CI execution
Kubernetes Service
Kubernetes scaling
Kubernetes self-healing
Kubernetes dashboard


License

This project was developed for educational purposes as part of the JENSEN
IoT & Embedded Systems program.
