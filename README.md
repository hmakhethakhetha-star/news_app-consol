# News Portal Django App

A Django-based news application built as a capstone project.  
This README explains how to set up and run the project using either a Python virtual environment (venv) or Docker.

---
## ⚙️ Prerequisites
- Python 3.10+  
- pip (Python package manager)  
- Git  
- Docker (for containerized setup)

---

## 🔹 Manual Setup (Virtual Environment)

Follow these steps to run the project manually:

1. **Clone the repository**
   ```bash
   git clone https://github.com/hmakhethakhetha-star/news_app-consol.git
  
## 🚀 Setup with venv

1. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows

---

  * pip install -r requirements.txt
---

  ## Apply migrations
 - python manage.py migrate

  ## Run the development server
  - python manage.py runserver

  ## 🔹 Docker Setup
  This project can also be run inside a Docker container.

**1. Build the Docker image**
docker build -t django-capstone .

**2. Run the container**
docker run -p 8000:8000 django-capstone

**Open your browser at:http://127.0.0.1:8000 (127.0.0.1 in Bing)**

## 🔹 Documentation
Documentation is generated using Sphinx and stored in the docs/ folder.
To regenerate: make html

## Database Connector

This project uses **mysqlclient** as the database connector for MariaDB/MySQL.  
Ensure it is installed via `requirements.txt`:

```bash
pip install -r requirements.txt

---

## API Testing

Use Django REST Framework’s browsable API at /api/
Example endpoints:

GET /api/articles/
POST /api/articles/ (requires authentication)

**Test with Postman or curl:**
curl http://127.0.0.1:8000/api/articles/

---

news_portal/
├── manage.py
├── news/                # Core app (models, views, serializers)
├── news_portal/         # Project settings, URLs, WSGI/ASGI
├── requirements.txt
├── Dockerfile
├── .dockerignore
docs/                    # Sphinx documentation
README.md

---

Deployment Notes
Ensure database settings in settings.py are updated for production.
For Docker + MariaDB/MySQL, set DATABASE_HOST=host.docker.internal.
Use environment variables for secrets.

👥 Roles:
Publisher: Manages articles and subscriptions
Journalist: Creates and edits articles
Editor: Reviews and approves content
Reader: Subscribes to newsletters and reads articles

