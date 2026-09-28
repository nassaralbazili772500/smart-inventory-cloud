# Smart Inventory Cloud API

A production-style containerized inventory management REST API built for the Cloud Computing & Containerization course project.

The system demonstrates RESTful API development, PostgreSQL persistence, Docker image optimization, Nginx reverse proxying, Docker Compose orchestration, custom networking, persistent named volumes, health checks, failure recovery, and container registry publishing.

---

## Architecture

```text
                    Client / Browser / cURL
                              |
                              | HTTP :8081
                              v
                    +-------------------+
                    |       NGINX       |
                    |   Reverse Proxy   |
                    |       :80         |
                    +---------+---------+
                              |
                              | Internal Docker Network
                              v
                    +-------------------+
                    |      FastAPI      |
                    |    REST API       |
                    |      :8000        |
                    |    Non-root       |
                    +---------+---------+
                              |
                              | PostgreSQL Protocol
                              v
                    +-------------------+
                    |    PostgreSQL     |
                    |       :5432       |
                    +---------+---------+
                              |
                              v
                    +-------------------+
                    | Docker Named      |
                    | Volume: db-data   |
                    +-------------------+
```

Only Nginx publishes a host port.

The FastAPI service and PostgreSQL database are accessible only through the internal Docker bridge network.

---

## Technology Stack

- Python 3.14
- FastAPI
- SQLAlchemy
- Pydantic
- PostgreSQL 17
- Psycopg 3
- Docker
- Docker Compose
- Nginx
- Docker Hub
- Git / GitHub

---

## Project Structure

```text
smart-inventory-cloud/
│
├── api/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   └── schemas.py
│   │
│   ├── Dockerfile
│   ├── .dockerignore
│   └── requirements.txt
│
├── nginx/
│   └── nginx.conf
│
├── compose.yaml
├── .env.example
├── .gitignore
├── README.md
│
└── docs/
    └── Technical-Report.pdf
```

---

## Main Features

- Complete CRUD operations
- PostgreSQL database integration
- Input validation
- Product search
- Low-stock alerts
- Database-aware health check
- Automatic database table creation
- Nginx reverse proxy
- Internal Docker network
- Persistent database storage
- API and database port isolation
- Non-root API container
- Docker health checks
- Docker Compose orchestration
- Failure recovery testing
- Semantic Docker image versioning

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API information |
| GET | `/health` | API and database health check |
| GET | `/api/products` | Get all products |
| GET | `/api/products/{product_id}` | Get a product by ID |
| POST | `/api/products` | Create a new product |
| PUT | `/api/products/{product_id}` | Update a product |
| DELETE | `/api/products/{product_id}` | Delete a product |
| GET | `/api/products/alerts/low-stock` | Get low-stock products |
| GET | `/api/products/filter/search?name=value` | Search products by name |

---

## HTTP Status Codes

The API demonstrates appropriate REST response codes including:

- `200 OK`
- `201 Created`
- `204 No Content`
- `404 Not Found`
- `422 Unprocessable Entity`
- `503 Service Unavailable`

---

## Prerequisites

Install:

- Docker Desktop or Docker Engine
- Docker Compose v2
- Git

Verify Docker:

```bash
docker --version
docker compose version
docker run --rm hello-world
```

---

## Environment Configuration

Create a `.env` file in the project root.

Example:

```env
POSTGRES_DB=smart_inventory
POSTGRES_USER=inventory_user
POSTGRES_PASSWORD=change_me
```

Do not commit the real `.env` file to GitHub.

---

## Run the Complete System

Start the complete multi-container application using:

```bash
docker compose up -d
```

Check container status:

```bash
docker compose ps
```

The application is available through Nginx at:

```text
http://localhost:8081
```

Swagger API documentation:

```text
http://localhost:8081/docs
```

Health check:

```text
http://localhost:8081/health
```

Stop the complete stack:

```bash
docker compose down
```

---

## Docker Services

The Compose deployment contains three services:

### Nginx

External entry point.

```text
Host :8081 -> Nginx :80
```

### FastAPI

Internal application service.

```text
api:8000
```

The API port is not published to the host.

### PostgreSQL

Internal database service.

```text
database:5432
```

The database port is not published to the host.

---

## Docker Network

The project uses a custom bridge network:

```text
smart-inventory-cloud_app-network
```

Inspect it using:

```bash
docker network ls
docker network inspect smart-inventory-cloud_app-network
```

Docker service-name discovery is used:

```text
Nginx -> api:8000
API -> database:5432
```

---

## Persistent Storage

PostgreSQL uses the named Docker volume:

```text
smart-inventory-cloud_db-data
```

Inspect it:

```bash
docker volume ls
docker volume inspect smart-inventory-cloud_db-data
```

Database data survives:

```bash
docker compose down
docker compose up -d
```

Do not use the following command unless database deletion is intended:

```bash
docker compose down -v
```

because `-v` removes the persistent volume.

---

## Security Practices

The project implements:

- Non-root application execution
- Lightweight Python slim base image
- Internal-only API port
- Internal-only PostgreSQL port
- Nginx as the controlled entry point
- Read-only Nginx configuration mount
- Environment-based database credentials
- `.env` excluded from Git
- Custom bridge network
- Specific Docker image versions
- Minimal Docker build context using `.dockerignore`

Verify non-root execution:

```bash
docker run --rm smart-inventory-api:v1.0.0 id
```

Expected user:

```text
uid=10001(appuser)
```

---

## Docker Image Optimization

The Dockerfile copies dependency files before application source files.

Conceptually:

```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
```

This allows Docker to reuse the dependency layer when only application source code changes.

Inspect image layers:

```bash
docker image history smart-inventory-api:v1.0.0
```

---

## Health Checks

The PostgreSQL container uses `pg_isready`.

The API health check validates both:

- FastAPI availability
- PostgreSQL connectivity

Successful response:

```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

## Failure Scenarios Tested

### API Failure

```bash
docker compose stop api
```

Nginx remains running but cannot reach the backend.

Recovery:

```bash
docker compose start api
```

### Database Failure

```bash
docker compose stop database
```

The API returns:

```json
{
  "detail": "Database unavailable"
}
```

Recovery:

```bash
docker compose start database
```

### Container Recreation

```bash
docker compose down
docker compose up -d
```

Database records remain available because PostgreSQL uses a named volume.

---

## Docker Hub Registry

Docker Hub repository:

```text
docker.io/nassaralbazili/smart-inventory-api
```

Published tags:

```text
v1.0.0
latest
```

Pull the versioned image:

```bash
docker pull nassaralbazili/smart-inventory-api:v1.0.0
```

Version `v1.0.0` digest:

```text
sha256:18ecbf53f5101b27c0355a2ae0ced02e3a3f68a27583fb4acc5416a9e8d51728
```

---

## Version

Current release:

```text
v1.0.0
```

---

## Repository

GitHub:

```text
https://github.com/nassaralbazili772500/smart-inventory-cloud
```

---

## Team Members

Add the names of all team members here before final submission.

Example:

```text
1. Nassar Yahya
2. Team Member 2
3. Team Member 3
```

---

## Course Project

Cloud Computing & Containerization

Final Course Project:

**Design, Containerize, Secure, Orchestrate, and Publish a Production-Grade RESTful Service**