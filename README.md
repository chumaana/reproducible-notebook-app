# Reproducible Notebook Application

A web platform for creating, executing, and analyzing R Markdown notebooks with automated reproducibility tooling.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Vue](https://img.shields.io/badge/vue-3.x-green.svg)
![Docker](https://img.shields.io/badge/docker-required-blue.svg)

---

## Overview

This application enables researchers and data scientists to write R Markdown notebooks directly in the browser, execute them in isolated Docker environments, and automatically analyze their reproducibility. The system detects common reproducibility issues, tracks dependencies, and generates Docker-based packages for sharing computational workflows.

**Key Features:**

- 📝 **Browser-based R Markdown editor** with split-pane view (code + rendered output)
- 🐳 **Isolated execution** in Docker containers for reproducible results
- 🔍 **Automated reproducibility analysis** detecting randomness, hardcoded paths, timestamps, and secrets
- 📦 **One-click package generation** with Dockerfile, Makefile, and dependency manifest
- 🔄 **Semantic diff visualization** comparing notebook outputs across executions
- 📥 **Export notebooks** as `.Rmd` files or complete reproducibility packages (ZIP)

---

## Quick Start

### Prerequisites

- Docker 20.10+ and Docker Compose  5.0.0+
- 4GB RAM (8GB recommended)
- 5GB free disk space

### Installation

**1. Clone repository**

```bash
git clone https://github.com/chumaana/reproducible-notebook-app.git
cd reproducible-notebook-app
```

**2. Configure environment**

Create `.env` file inside backed directory:

```bash
cat > backend/.env << EOF
DEBUG=True
SECRET_KEY=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 50)
DB_NAME=notebooks
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
EOF
```

**3. Start application**

```bash
docker compose up --build
```

First build takes 5-10 minutes (installs R, Python packages, compiles r4r/rdiff tools).

**4. Access application**

- **Frontend:** [http://localhost:5173](http://localhost:5173)
- **Backend API:** [http://localhost:8000/api/](http://localhost:8000/api/)
- **Admin Panel:** [http://localhost:8000/admin](http://localhost:8000/admin)

**5. Create admin account** _(optional)_

```bash
docker compose exec backend python manage.py createsuperuser
```

**6. Stop application**

```bash
# Press Ctrl+C, then:
docker compose down

# Remove all data (clean slate):
docker compose down -v
```

---

## Usage Guide

### Creating Your First Notebook

1. **Register/Login** at http://localhost:5173
2. Click **"New Notebook"** in the navigation
3. Enter notebook title: `My First Analysis`
4. Write R code in the editor:

```r
# Load libraries
library(ggplot2)

# Generate data
set.seed(123)
data <- data.frame(
  x = 1:100,
  y = cumsum(rnorm(100))
)

# Create plot
ggplot(data, aes(x, y)) +
  geom_line(color = "blue") +
  theme_minimal() +
  labs(title = "Random Walk")
```

5. Click **"Save"** (auto-saves every 2 seconds)
6. Click **"Run"** to execute notebook
7. View rendered output in right pane

### Analyzing Reproducibility

1. After executing notebook, click **"Analysis"**
2. Review detected issues:
   - ✅ Proper `set.seed()` usage
   - ⚠️ Missing system dependencies
   - 🔴 Hardcoded secrets or paths
3. Click **"Generate Package"** to create:
   - `Dockerfile` with exact R + package versions
   - `Makefile` for reproducible builds
   - Dependency manifest (r4r data)
4. Download ZIP package for sharing

### Comparing Executions

1. Execute notebook multiple times with different code
2. Click **"Diff"** to generate semantic comparison
3. View highlighted differences in modal
4. Use rdiff visualization to understand changes

---

## API Documentation

### Authentication

| Method  | Endpoint              | Description                                   |
| ------- | --------------------- | --------------------------------------------- |
| `POST`  | `/api/auth/register/` | Register new user (username, email, password) |
| `POST`  | `/api/auth/login/`    | Login and receive auth token                  |
| `GET`   | `/api/auth/profile/`  | Get current user profile                      |
| `PATCH` | `/api/auth/profile/`  | Update user profile                           |

### Notebooks

| Method   | Endpoint               | Description               |
| -------- | ---------------------- | ------------------------- |
| `GET`    | `/api/notebooks/`      | List user's notebooks     |
| `POST`   | `/api/notebooks/`      | Create new notebook       |
| `GET`    | `/api/notebooks/{id}/` | Get notebook details      |
| `PATCH`  | `/api/notebooks/{id}/` | Update notebook (partial) |
| `DELETE` | `/api/notebooks/{id}/` | Delete notebook           |

### Execution & Analysis

| Method | Endpoint                                | Description                            |
| ------ | --------------------------------------- | -------------------------------------- |
| `POST` | `/api/notebooks/{id}/execute/`          | Execute R Markdown notebook            |
| `POST` | `/api/notebooks/{id}/generate_package/` | Generate reproducibility package       |
| `POST` | `/api/notebooks/{id}/generate_diff/`    | Generate semantic diff                 |
| `GET`  | `/api/notebooks/{id}/executions/`       | Get execution history                  |
| `GET`  | `/api/notebooks/{id}/reproducibility/`  | Get analysis data (r4r, static issues) |

### Downloads

| Method | Endpoint                                | Description                              |
| ------ | --------------------------------------- | ---------------------------------------- |
| `GET`  | `/api/notebooks/{id}/download/`         | Download `.Rmd` file                     |
| `GET`  | `/api/notebooks/{id}/download_package/` | Download ZIP package (Dockerfile + deps) |

**Authentication:** All notebook endpoints require `Authorization: Token <token>` header.

---

## Database Setup

### Automatic (Docker)

The database is **automatically configured** when running `docker compose up`:

- PostgreSQL 15 container starts with health checks
- Database `notebooks` is created on first run
- Django migrations execute via `entrypoint.sh`
- **No manual setup required** 

### Verify Database

```bash
# Check database logs
docker compose logs db

# Should see: "database system is ready to accept connections"

# Access PostgreSQL shell
docker compose exec db psql -U postgres -d notebooks

# List tables
\dt

# View notebooks
SELECT id, title, author_id FROM notebook_api_notebook;

# Exit
\q
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend runs at http://localhost:5173

---

**Built with ❤️ for reproducible data science**
