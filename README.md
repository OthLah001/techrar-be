# Techrar Notification Service - Backend

This is the **backend** for the Techrar Notification Service project. It provides API endpoints to fetch campaigns, create campaigns, and check the status of the notificationq.

## Features

✅ Multi-Channel Messaging  
✅ Merchant API 
✅ Web Dashboard
✅ Scheduling & Delivery
✅ Performance & Scalability
✅ Persistence
✅ Security

---

## Installation Guide

### **Clone the Repository**

```bash
git clone https://github.com/OthLah001/techrar-be.git
cd techrar-be
```

### **Install PostgreSQL & Python**

Make sure you have:

- **PostgreSQL** (version 14 or later) → [Download Here](https://www.postgresql.org/download/)
- **Python** (version 3.9 or later) → [Download Here](https://www.python.org/downloads/)
- **Redis** (version 6.0 or later) → [Download Here](https://redis.io/downloads/)

### **Create a Python Virtual Environment**

```bash
python -m venv env
source env/bin/activate   # On macOS/Linux
env\Scripts\activate      # On Windows
```

### **Install Dependencies**

Make sure you are in the project directory, then install all required packages:

```bash
pip install -r requirements.txt
```

### **Set Up PostgreSQL Database**

- Create a new PostgreSQL database

### Environment Variables

Create a **`config/.env` file** to store your API keys & secrets:

```
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=postgres://your_db_user:your_db_password@localhost:5432/your_db_name
REDIS_URL=redis://localhost:6379/0
LIVE_ENV=False
```

### **Apply Migrations**

```bash
python manage.py migrate
```

### **Start Celery (for background tasks)**

```bash
celery -A config worker --loglevel=info
```

### **Run the Django Server**

```bash
python manage.py runserver
```

The backend will be available at **`http://127.0.0.1:8000/`**

## API Documentation

Django Ninja auto-generates API docs.  
Visit **`http://127.0.0.1:8000/api/docs/`** to explore the available endpoints.

---