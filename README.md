# Sakila Movie Database - Flask Web Application

A full-featured web application for managing the MySQL Sakila sample database (DVD rental store), built with Flask and designed to run as Docker containers communicating over a custom Docker network.

---

## Table of Contents

- [Application Overview](#application-overview)
- [Application Architecture](#application-architecture)
- [Docker Network Architecture](#docker-network-architecture)
- [How Container Communication Works](#how-container-communication-works)
- [Prerequisites](#prerequisites)
- [Step-by-Step Setup Guide](#step-by-step-setup-guide)
- [Application Features](#application-features)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

---

## Application Overview

This application provides a web-based interface for the Sakila DVD rental database. It includes:

- **Dashboard** with aggregate stats, revenue metrics, and interactive Chart.js visualizations
- **Film Management** - full CRUD operations, search/filter/pagination, CSV export
- **Actor Management** - CRUD with filmography view and popularity stats
- **Customer Management** - browse customers with rental history drill-down
- **Rental Tracking** - view active/returned rentals, mark returns
- **Inventory Management** - track stock availability across stores
- **Store & Staff Views** - location info, manager details, staff activity
- **Reports & Analytics** - revenue charts, top films, top customers, spending distribution

---

## Application Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER (Browser)                               │
│                     http://localhost:5000                            │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ HTTP Requests
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FLASK APPLICATION CONTAINER                       │
│                     (sakila-flask-app)                               │
│                                                                     │
│  ┌─────────────┐   ┌──────────────┐   ┌──────────────────────┐     │
│  │  app.py      │   │  config.py   │   │  templates/ (Jinja2) │     │
│  │  (Routes &   │   │  (DB Config) │   │  - dashboard.html    │     │
│  │   SQL Logic) │   │              │   │  - films.html        │     │
│  │              │   │  MYSQL_HOST = │   │  - actors.html       │     │
│  │  PyMySQL ────┼───│  "mysql-     │   │  - customers.html    │     │
│  │  Driver      │   │   container" │   │  - rentals.html      │     │
│  └──────┬───────┘   └──────────────┘   │  - reports.html      │     │
│         │                              │  - ...               │     │
│         │                              └──────────────────────┘     │
│         │           ┌──────────────────────┐                        │
│         │           │  static/             │                        │
│         │           │  - style.css         │                        │
│         │           │  - script.js         │                        │
│         │           └──────────────────────┘                        │
│         │                                                           │
│  Port: 5000 (exposed to host)                                       │
└─────────┼───────────────────────────────────────────────────────────┘
          │  MySQL Protocol (port 3306)
          │  Connection via container name DNS
          │
  ┌───────┼───────────────────────────────────────┐
  │       │     DOCKER NETWORK (sakila-network)   │
  │       │     Driver: bridge                     │
  │       │     Built-in DNS resolution            │
  │       │                                        │
  │       │  "mysql-container" ──► 172.18.0.2      │
  │       │  "sakila-flask-app" ──► 172.18.0.3     │
  └───────┼────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     MYSQL CONTAINER                                  │
│                    (mysql-container)                                 │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    MySQL Server 8.0                          │    │
│  │                                                             │    │
│  │  Database: sakila                                           │    │
│  │  ┌────────┐ ┌───────┐ ┌──────────┐ ┌────────┐ ┌─────────┐ │    │
│  │  │  film   │ │ actor │ │ customer │ │ rental │ │ payment │ │    │
│  │  └────────┘ └───────┘ └──────────┘ └────────┘ └─────────┘ │    │
│  │  ┌───────────┐ ┌───────┐ ┌───────┐ ┌──────────────────┐   │    │
│  │  │ inventory │ │ store │ │ staff │ │ category + more  │   │    │
│  │  └───────────┘ └───────┘ └───────┘ └──────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
│  Port: 3306 (internal, also exposed to host)                        │
│                                                                     │
│  Volume Mount: mysql-data ──► /var/lib/mysql (persistent storage)   │
└─────────────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Flask 2.3.3 (Python 3.9) |
| Database Driver | PyMySQL 1.1.0 |
| Database | MySQL 8.0 (Sakila sample DB) |
| Frontend | Bootstrap 5.1.3, Font Awesome 6, Chart.js 4.4 |
| Templating | Jinja2 |
| Containerization | Docker |

---

## Docker Network Architecture

This project demonstrates **Docker container networking** using a user-defined bridge network. Two containers communicate with each other over this shared network:

```
┌──────────────────────────────────────────────────────────┐
│                   HOST MACHINE                            │
│                                                          │
│   ┌──────────────────────────────────────────────────┐   │
│   │          sakila-network (bridge)                  │   │
│   │                                                  │   │
│   │  ┌─────────────────┐   ┌──────────────────┐     │   │
│   │  │ sakila-flask-app │   │ mysql-container  │     │   │
│   │  │                 │   │                  │     │   │
│   │  │  Flask App      │──►│  MySQL 8.0       │     │   │
│   │  │  Port 5000      │   │  Port 3306       │     │   │
│   │  └────────┬────────┘   └────────┬─────────┘     │   │
│   │           │                     │                │   │
│   └───────────┼─────────────────────┼────────────────┘   │
│               │                     │                    │
│          Port 5000             Port 3306                 │
│          (mapped)              (mapped)                  │
│                                                          │
│   ┌─────────────────────────────────────────┐            │
│   │        Docker Volume: mysql-data        │            │
│   │     (persistent MySQL data storage)     │            │
│   └─────────────────────────────────────────┘            │
└──────────────────────────────────────────────────────────┘
```

### Key Networking Concepts Demonstrated

1. **User-Defined Bridge Network**: `sakila-network` is a custom bridge network created with `docker network create`. Unlike the default bridge network, it provides **automatic DNS resolution** between containers.

2. **Container Name DNS**: The Flask app connects to MySQL using the hostname `mysql-container` (the container's name). Docker's embedded DNS server resolves this name to the container's internal IP address automatically.

3. **Isolated Communication**: Both containers can talk to each other over port 3306 on the internal network, without that port needing to be exposed to the host (though we expose it for optional external access).

4. **Docker Volume for Persistence**: A named volume `mysql-data` is mounted to `/var/lib/mysql` inside the MySQL container, ensuring database data survives container restarts or removal.

---

## How Container Communication Works

When the Flask application needs to query the database, the following happens:

```
Step 1: Flask app calls get_db_connection()
        ┌──────────────────────────────────────┐
        │  pymysql.connect(                    │
        │      host='mysql-container',  ◄────── Config.MYSQL_HOST
        │      user='root',                    │
        │      password='admin',               │
        │      database='sakila'               │
        │  )                                   │
        └──────────────┬───────────────────────┘
                       │
Step 2: Docker DNS resolves 'mysql-container' to internal IP
        ┌──────────────┼───────────────────────┐
        │  Docker DNS   │                       │
        │  "mysql-container" ──► 172.18.0.2     │
        └──────────────┼───────────────────────┘
                       │
Step 3: TCP connection on port 3306 over bridge network
        ┌──────────────┼───────────────────────┐
        │  sakila-network (bridge)              │
        │  172.18.0.3:random ──► 172.18.0.2:3306│
        └──────────────┼───────────────────────┘
                       │
Step 4: MySQL processes query, returns results
        ┌──────────────▼───────────────────────┐
        │  MySQL Server                         │
        │  Database: sakila                     │
        │  Query: SELECT * FROM film ...        │
        │  Result ──► Flask ──► HTML ──► Browser│
        └──────────────────────────────────────┘
```

**Why this works:**
- Both containers are attached to `sakila-network`
- Docker provides automatic DNS resolution for container names on user-defined networks
- The Flask app uses `mysql-container` as the hostname (matching the MySQL container's `--name`)
- No hardcoded IP addresses are needed - Docker DNS handles resolution dynamically

---

## Prerequisites

Before starting, make sure you have the following installed on your machine:

- **Docker Desktop** (v20.10 or later) - [Download here](https://www.docker.com/products/docker-desktop/)
- **Git** (optional, for cloning the repo)

Verify Docker is installed and running:

```bash
docker --version
docker info
```

---

## Step-by-Step Setup Guide

### Step 1: Clone or Navigate to the Project

```bash
cd /path/to/sakila_flask_app_2
```

### Step 2: Create the Docker Network

Create a user-defined bridge network so both containers can communicate by name:

```bash
docker network create sakila-network
```

Verify the network was created:

```bash
docker network ls
```

You should see `sakila-network` with the `bridge` driver in the list.

### Step 3: Create a Docker Volume for MySQL Data Persistence

```bash
docker volume create mysql-data
```

This volume ensures your database data persists even if the MySQL container is stopped or removed.

### Step 4: Start the MySQL Container

Pull and run the MySQL 8.0 container with the Sakila database:

```bash
docker run -d \
  --name mysql-container \
  --network sakila-network \
  -e MYSQL_ROOT_PASSWORD=admin \
  -p 3306:3306 \
  -v mysql-data:/var/lib/mysql \
  mysql:8.0
```

**What each flag does:**

| Flag | Purpose |
|------|---------|
| `-d` | Run in detached (background) mode |
| `--name mysql-container` | Assign the name `mysql-container` (used as DNS hostname) |
| `--network sakila-network` | Attach to our custom network |
| `-e MYSQL_ROOT_PASSWORD=admin` | Set the MySQL root password |
| `-p 3306:3306` | Map host port 3306 to container port 3306 |
| `-v mysql-data:/var/lib/mysql` | Mount the named volume for data persistence |

Wait for MySQL to fully start (takes about 15-30 seconds):

```bash
docker logs mysql-container 2>&1 | tail -5
```

Look for: `ready for connections` in the output.

### Step 5: Load the Sakila Sample Database

Download the Sakila database SQL files and import them into the MySQL container:

```bash
# Download the Sakila database
curl -L -o sakila-db.tar.gz https://downloads.mysql.com/docs/sakila-db.tar.gz

# Extract
tar -xzf sakila-db.tar.gz

# Import schema and data into MySQL container
docker exec -i mysql-container mysql -uroot -padmin < sakila-db/sakila-schema.sql
docker exec -i mysql-container mysql -uroot -padmin < sakila-db/sakila-data.sql
```

Verify the database was loaded:

```bash
docker exec -it mysql-container mysql -uroot -padmin -e "USE sakila; SHOW TABLES;"
```

You should see approximately 23 tables (film, actor, customer, rental, payment, etc.).

### Step 6: Build the Flask Application Image

From the project root directory:

```bash
docker build -t sakila-flask-app .
```

This uses the `Dockerfile` to:
1. Start from Python 3.9 slim base image
2. Install Flask, PyMySQL, WTForms, and cryptography
3. Copy the application code into the image
4. Expose port 5000

### Step 7: Run the Flask Application Container

```bash
docker run -d \
  --name sakila-flask-app \
  --network sakila-network \
  -p 5000:5000 \
  -e MYSQL_HOST=mysql-container \
  -e MYSQL_USER=root \
  -e MYSQL_PASSWORD=admin \
  -e MYSQL_DB=sakila \
  sakila-flask-app
```

**What each flag does:**

| Flag | Purpose |
|------|---------|
| `-d` | Run in detached mode |
| `--name sakila-flask-app` | Container name |
| `--network sakila-network` | Same network as MySQL (enables DNS resolution) |
| `-p 5000:5000` | Map host port 5000 to container port 5000 |
| `-e MYSQL_HOST=mysql-container` | Tell Flask to connect to MySQL via container name |

### Step 8: Verify Everything is Running

```bash
# Check both containers are running
docker ps

# Check they are both on the same network
docker network inspect sakila-network
```

The `docker network inspect` output should show both `mysql-container` and `sakila-flask-app` in the `Containers` section.

### Step 9: Access the Application

Open your browser and go to:

```
http://localhost:5000
```

You should see the Sakila Dashboard with film counts, actor counts, revenue stats, and interactive charts.

---

## Quick Reference - All Commands in One Go

```bash
# 1. Create network and volume
docker network create sakila-network
docker volume create mysql-data

# 2. Start MySQL
docker run -d \
  --name mysql-container \
  --network sakila-network \
  -e MYSQL_ROOT_PASSWORD=admin \
  -p 3306:3306 \
  -v mysql-data:/var/lib/mysql \
  mysql:8.0

# 3. Wait for MySQL to be ready (check logs)
sleep 20
docker logs mysql-container 2>&1 | tail -3

# 4. Load Sakila database
curl -L -o sakila-db.tar.gz https://downloads.mysql.com/docs/sakila-db.tar.gz
tar -xzf sakila-db.tar.gz
docker exec -i mysql-container mysql -uroot -padmin < sakila-db/sakila-schema.sql
docker exec -i mysql-container mysql -uroot -padmin < sakila-db/sakila-data.sql

# 5. Build and run Flask app
docker build -t sakila-flask-app .
docker run -d \
  --name sakila-flask-app \
  --network sakila-network \
  -p 5000:5000 \
  -e MYSQL_HOST=mysql-container \
  -e MYSQL_USER=root \
  -e MYSQL_PASSWORD=admin \
  sakila-flask-app

# 6. Open http://localhost:5000
```

---

## Stopping and Cleanup

```bash
# Stop containers
docker stop sakila-flask-app mysql-container

# Remove containers
docker rm sakila-flask-app mysql-container

# Remove network
docker network rm sakila-network

# Remove volume (WARNING: deletes all database data)
docker volume rm mysql-data

# Remove the Flask image
docker rmi sakila-flask-app
```

To restart after stopping (without removing):

```bash
docker start mysql-container
docker start sakila-flask-app
```

---

## Application Features

### Pages & Routes

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | `/` | Stats overview, revenue metrics, Chart.js visualizations |
| Films | `/films` | Browse, search, filter, paginate films |
| Add Film | `/films/add` | Create new film with category & actor selection |
| Edit Film | `/films/edit/<id>` | Update film details |
| Film Detail | `/films/<id>` | Full film info, cast, rental stats, revenue |
| Export Films | `/films/export` | Download all films as CSV |
| Actors | `/actors` | Browse actors with search, sort, pagination |
| Customers | `/customers` | Browse customers with search |
| Customer Rentals | `/customers/<id>/rentals` | View a customer's full rental history |
| Rentals | `/rentals` | View active/returned/all rentals, process returns |
| Staff | `/staff` | Staff directory with activity stats |
| Inventory | `/inventory` | Track stock by film, store, availability |
| Stores | `/stores` | Store locations with manager & inventory info |
| Reports | `/reports` | Revenue charts, top films, top customers, analytics |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/film/<id>` | GET | Film details as JSON (used by Quick View modal) |
| `/api/actor/<id>` | GET | Actor details and filmography as JSON |
| `/api/dashboard/charts` | GET | Chart data for dashboard visualizations |
| `/api/reports/charts` | GET | Chart data for reports page visualizations |
| `/rentals/return/<id>` | POST | Mark a rental as returned |

---

## Project Structure

```
sakila_flask_app_2/
├── Dockerfile              # Container build instructions
├── requirements.txt        # Python dependencies
├── config.py               # Database & app configuration (env var support)
├── app.py                  # Flask application (all routes & SQL logic)
├── static/
│   ├── style.css           # Custom styles
│   └── script.js           # Modal handlers, form validation, utilities
├── templates/
│   ├── base.html           # Base template (navbar, flash messages)
│   ├── dashboard.html      # Dashboard with stats & charts
│   ├── films.html          # Films listing with search/filter
│   ├── film_detail.html    # Individual film view
│   ├── film_form.html      # Add/edit film form
│   ├── actors.html         # Actors listing with modals
│   ├── customers.html      # Customers listing
│   ├── customer_rentals.html # Customer rental history
│   ├── rentals.html        # Rentals listing with return action
│   ├── staff.html          # Staff directory
│   ├── inventory.html      # Inventory management
│   ├── stores.html         # Store locations
│   └── reports.html        # Reports with charts
├── CLAUDE.md               # AI assistant context file
└── README.md               # This file
```

---

## Environment Variables

The application reads configuration from environment variables with fallback defaults:

| Variable | Default | Description |
|----------|---------|-------------|
| `MYSQL_HOST` | `mysql-container` | MySQL server hostname (container name in Docker network) |
| `MYSQL_USER` | `root` | MySQL username |
| `MYSQL_PASSWORD` | `admin` | MySQL password |
| `MYSQL_DB` | `sakila` | Database name |
| `SECRET_KEY` | `your-secret-key...` | Flask session secret key |

---

## Troubleshooting

### Flask app can't connect to MySQL

```bash
# Verify both containers are on the same network
docker network inspect sakila-network

# Test connectivity from Flask container to MySQL
docker exec sakila-flask-app python -c "
import pymysql
conn = pymysql.connect(host='mysql-container', user='root', password='admin', database='sakila')
print('Connection successful!')
conn.close()
"

# Check MySQL container logs
docker logs mysql-container
```

### MySQL container not starting

```bash
# Check logs for errors
docker logs mysql-container

# If port 3306 is already in use, stop local MySQL or use a different port:
docker run -d --name mysql-container --network sakila-network \
  -e MYSQL_ROOT_PASSWORD=admin -p 3307:3306 -v mysql-data:/var/lib/mysql mysql:8.0
```

### Container name conflict (already in use)

```bash
# Remove existing containers with the same name
docker rm -f sakila-flask-app mysql-container
```

### Database tables are empty or missing

```bash
# Re-import the Sakila database
docker exec -i mysql-container mysql -uroot -padmin < sakila-db/sakila-schema.sql
docker exec -i mysql-container mysql -uroot -padmin < sakila-db/sakila-data.sql

# Verify tables
docker exec -it mysql-container mysql -uroot -padmin -e "USE sakila; SELECT COUNT(*) FROM film;"
```

### Rebuild after code changes

```bash
docker stop sakila-flask-app && docker rm sakila-flask-app
docker build -t sakila-flask-app .
docker run -d --name sakila-flask-app --network sakila-network \
  -p 5000:5000 -e MYSQL_HOST=mysql-container sakila-flask-app
```
# trigger workflow
