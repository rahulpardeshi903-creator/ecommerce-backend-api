# 🛒 E-Commerce Backend API

A production-level e-commerce REST API built with **FastAPI**, **PostgreSQL**, **Redis**, and **PhonePe** payments.

## ✨ Features
- 🔐 JWT Authentication (register/login/roles: customer, admin, seller)
- 📦 Product Catalog with categories, search, and filters
- 🛒 Cart Management (add, update, remove items)
- 📋 Order Management (place, track, cancel orders)
- 💳 PhonePe Payment Integration (Indian payment gateway)
- 📧 Email Notifications (welcome + order confirmation)
- 🐳 Dockerized (one command to run everything)

## 🚀 Quick Start

### 1. Clone and setup environment
```bash
git clone <your-repo>
cd ecommerce-api
cp .env.example .env
# Edit .env with your credentials
```

### 2. Run with Docker (recommended)
```bash
docker-compose up --build
```
API will be live at: **http://localhost:8000**  
Swagger docs at: **http://localhost:8000/docs**

### 3. Run Locally (without Docker)
```bash
# Install dependencies
pip install -r requirements.txt

# Setup database migrations
alembic init alembic
alembic revision --autogenerate -m "initial"
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

## 📁 Project Structure
```
ecommerce-api/
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── api/
│   │   ├── deps.py              # Auth dependencies
│   │   └── v1/
│   │       ├── router.py        # Combines all routes
│   │       └── endpoints/
│   │           ├── auth.py      # Register, Login, Refresh
│   │           ├── users.py     # Profile management
│   │           ├── products.py  # Product CRUD + categories
│   │           ├── cart.py      # Cart management
│   │           ├── orders.py    # Order placement & tracking
│   │           └── payments.py  # PhonePe payment flow
│   ├── core/
│   │   ├── config.py            # All settings (from .env)
│   │   └── security.py          # JWT + password hashing
│   ├── db/
│   │   ├── base.py              # SQLAlchemy base
│   │   └── session.py           # DB connection
│   ├── models/                  # Database tables (SQLAlchemy)
│   ├── schemas/                 # Request/Response validators (Pydantic)
│   └── services/
│       ├── payment_service.py   # PhonePe API integration
│       ├── email_service.py     # Email notifications
│       └── redis_service.py     # Caching helpers
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## 🔑 API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/auth/register` | Register new user | Public |
| POST | `/api/v1/auth/login` | Login, get JWT tokens | Public |
| POST | `/api/v1/auth/refresh` | Refresh access token | Public |
| GET | `/api/v1/users/me` | Get my profile | User |
| GET | `/api/v1/products/` | List products | Public |
| POST | `/api/v1/products/` | Create product | Admin |
| GET | `/api/v1/cart/` | View cart | User |
| POST | `/api/v1/cart/items` | Add to cart | User |
| POST | `/api/v1/orders/` | Place order | User |
| POST | `/api/v1/payments/initiate` | Start PhonePe payment | User |
| POST | `/api/v1/payments/webhook` | PhonePe webhook | PhonePe |

## 💳 PhonePe Setup

1. Sign up at [PhonePe for Business](https://business.phonepe.com)
2. Get your `MERCHANT_ID` and `SALT_KEY` from the dashboard
3. Add them to your `.env` file
4. For testing, use the sandbox URL (already set in `.env.example`)

## 🌐 Environment Variables
See `.env.example` for all required variables.

## 👤 Default Roles
- `customer` — Default for all new registrations
- `admin` — Set manually in the database for admin users
- `seller` — For future seller features

---
Built with ❤️ using FastAPI + PostgreSQL + Redis + PhonePe
