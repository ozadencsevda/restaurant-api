# 🍴 Restaurant Menu API

A RESTful API for restaurant menu management, built with **FastAPI** and **SQL Server**. Features JWT-based authentication, role-based access control, and advanced menu querying capabilities.

---

## Features

- **JWT Authentication** — Secure register/login with bcrypt password hashing
- **Role-Based Access Control** — Admin-only endpoints for create, update, and delete operations
- **Menu Management** — Full CRUD for categories and menu items
- **Advanced Filtering** — Filter by category, price range, dietary options (vegetarian, vegan, gluten-free), availability, and featured status
- **Search & Autocomplete** — Full-text search and prefix-based suggestion endpoint
- **Pagination** — Configurable skip/limit on listing endpoints
- **Health Check** — `/health` endpoint reporting API and database status

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | Microsoft SQL Server |
| ORM | SQLAlchemy |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Config | Pydantic Settings |
| Testing | pytest, requests |

---

## Project Structure

```
RESTAURANT-API/
├── app/
│   ├── api/          # Route handlers (auth, categories, menu_items, search, suggest...)
│   ├── core/         # Config, dependencies, security utilities
│   ├── db/           # Database connection and session management
│   ├── models/       # SQLAlchemy ORM models
│   └── schemas/      # Pydantic request/response schemas
├── main.py               # App entrypoint, router registration, startup events
├── test_api.py           # Endpoint integration tests
├── comprehensive_test.py # Extended test suite
└── requirements.txt
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Microsoft SQL Server instance

### Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/restaurant-api.git
cd restaurant-api

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=mssql+pyodbc://<user>:<password>@<host>/<dbname>?driver=ODBC+Driver+17+for+SQL+Server
JWT_SECRET=your-secret-key-here
JWT_ALG=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
APP_ENV=dev
```

### Run

```bash
uvicorn main:app --reload
```

API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

---

## API Overview

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | ✗ | Register new user |
| POST | `/auth/login` | ✗ | Login, receive JWT token |
| GET | `/api/v1/me` | ✓ | Get current user profile |
| GET | `/api/v1/categories` | ✗ | List all categories |
| POST | `/api/v1/categories` | Admin | Create category |
| GET | `/api/v1/menu-items` | ✗ | List menu items (with filters) |
| POST | `/api/v1/menu-items` | Admin | Create menu item |
| PUT | `/api/v1/menu-items/{id}` | Admin | Update menu item |
| DELETE | `/api/v1/menu-items/{id}` | Admin | Delete menu item |
| GET | `/api/v1/menu-items/search` | ✗ | Full-text search |
| GET | `/api/v1/menu-items/suggest` | ✗ | Autocomplete suggestions |
| GET | `/health` | ✗ | API and DB health status |

---

## Example Requests

```bash
# Get vegetarian menu items under 100 TL
GET /api/v1/menu-items?is_vegetarian=true&max_price=100

# Autocomplete suggestion
GET /api/v1/menu-items/suggest?q=mer&limit=5
```

---

## Testing

The project includes an integration test suite that covers all major endpoints.

```bash
# Make sure the server is running first
uvicorn main:app --reload

# Run the test script
python test_api.py
```

**What the tests cover:**
- Health check (API and database status)
- User registration and login
- JWT token validation
- Authenticated endpoint access (`/api/v1/me`)
- Unauthorized access rejection (401 handling)
- Swagger documentation availability

A comprehensive test suite (`comprehensive_test.py`) is also included for extended coverage.

---

## License

MIT
