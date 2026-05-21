# News Portal Django App

A Django-based news application built as a capstone project.  
This README explains how to set up and run the project using either a Python virtual environment (venv) or Docker.

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

  * pip install -r requirements.txt

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

