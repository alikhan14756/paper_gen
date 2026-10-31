# ExamForge AI — Production Deployment & DevOps Guide

> **Author**: **Muhammad Ali** (Frontend Developer & Web Developer | [alibuild.site](https://alibuild.site))  
> **Target Environment**: Production Linux (Ubuntu 22.04 LTS / Debian 12), Docker, PostgreSQL, S3

---

## 1. System Requirements & Topology

### Hardware Specifications
- **Minimum**: 2 vCPU, 4 GB RAM, 20 GB SSD
- **Recommended**: 4 vCPU, 8 GB RAM, 80 GB SSD (supports high-throughput PyMuPDF concurrent extraction)

### Architecture Diagram
```
+-------------------------------------------------------------+
|                     Cloudflare / DNS                        |
+------------------------------+------------------------------+
                               | HTTPS (443)
                               v
+-------------------------------------------------------------+
|                 Nginx / Caddy Reverse Proxy                 |
|       - SSL Termination (Let's Encrypt)                     |
|       - Request Rate Limiting                               |
+-------------------+---------------------+-------------------+
                    |                     |
     /api/*         v                     v       /*
+-----------------------+             +-----------------------+
|  FastAPI Backend      |             |  Next.js 16 Web App   |
|  Uvicorn (Gunicorn)   |             |  Node.js 20+ Runtime  |
|  Port: 8000           |             |  Port: 3000           |
+-----------+-----------+             +-----------------------+
            |
            +-------------------------+
            |                         |
            v                         v
+-----------------------+ +-----------------------+
|  PostgreSQL 15+       | |  AWS S3 / MinIO       |
|  (RDS / Supabase)     | |  (Textbook Storage)   |
+-----------------------+ +-----------------------+
```

---

## 2. Environment Configuration

Create a `.env` file in the project root:

```ini
# Application Mode
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=CHANGE_THIS_TO_A_64_CHAR_HEX_SECRET_IN_PRODUCTION

# Database Connection (PostgreSQL)
DATABASE_URL=postgresql+psycopg://examforge_user:StrongPasswordHere@localhost:5432/examforge_prod

# AI Provider API Keys
GEMINI_API_KEY=AIzaSyYourGeminiApiKeyHere
ANTHROPIC_API_KEY=sk-ant-YourAnthropicApiKeyHere
DEFAULT_AI_PROVIDER=gemini-2.5-flash

# Security & Tokens
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALLOWED_ORIGINS=https://examforge.ai,https://admin.examforge.ai

# File Storage (Local or S3)
STORAGE_BACKEND=local
LOCAL_STORAGE_DIR=/var/data/examforge/uploads
# Or for AWS S3:
# STORAGE_BACKEND=s3
# AWS_ACCESS_KEY_ID=...
# AWS_SECRET_ACCESS_KEY=...
# AWS_S3_BUCKET_NAME=examforge-textbooks
# AWS_REGION=ap-south-1

# Creator Attribution
APP_NAME=ExamForge AI
CREATOR_NAME=Muhammad Ali
CREATOR_PORTFOLIO=https://alibuild.site
```

---

## 3. Docker Deployment (`docker-compose.yml`)

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_USER: examforge_user
      POSTGRES_PASSWORD: StrongPasswordHere
      POSTGRES_DB: examforge_prod
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    restart: always
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql+psycopg://examforge_user:StrongPasswordHere@db:5432/examforge_prod
      - ENVIRONMENT=production
    volumes:
      - uploads_data:/var/data/examforge/uploads
    ports:
      - "8000:8000"

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    restart: always
    depends_on:
      - backend
    environment:
      - NEXT_PUBLIC_API_URL=https://api.examforge.ai
    ports:
      - "3000:3000"

volumes:
  pgdata:
  uploads_data:
```

---

## 4. Production Checklist

- [ ] **Secret Key**: Generate using `python -c "import secrets; print(secrets.token_hex(32))"`.
- [ ] **Database Migrations**: Execute `alembic upgrade head` before serving traffic.
- [ ] **Nginx Reverse Proxy**: Configure client maximum body size (`client_max_body_size 50M;`) for PDF textbook uploads.
- [ ] **SSL / TLS**: Enforce TLS 1.3 with automated certificate renewal via Certbot.
- [ ] **Systemd / Process Supervisor**: Run backend under Gunicorn with Uvicorn worker class:
  ```bash
  gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
  ```
- [ ] **Regular Backups**: Automate PostgreSQL `pg_dump` daily snapshots.

---

## 5. Creator Attribution

Engineered by:  
**Muhammad Ali**  
Frontend Developer & Web Developer | Founder of **AliBuild**  
Portfolio: [https://alibuild.site](https://alibuild.site)  
Email: [alikhanwebdeveloper@gmail.com](mailto:alikhanwebdeveloper@gmail.com)
