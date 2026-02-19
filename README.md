# Vulnerable vs. Secure Storefront

This is a **Demonstration Project** designed to showcase the difference between secure and insecure coding practices in a web application. It features two parallel implementations of an online store: one built with standard security controls, and another deliberately engineered with OWASP Top 10 vulnerabilities.

**WARNING: DO NOT DEPLOY THE INSECURE VERSION TO A PRODUCTION ENVIRONMENT.**

## Project Overview

The application is built with **Django 5.x** and serves two distinct paths:

*   **Secure Path (`/store/secure/`)**: Implements strict session management (Redis), `Argon2` password hashing, parameterized ORM queries, and CSRF protection.
*   **Insecure Path (`/store/insecure/`)**: Intentionally vulnerable to SQL Injection, Cross-Site Scripting (XSS), insecure session management (Base64 cookies), and Broken Access Control.

## Features

| Feature | Secure Implementation | Insecure Implementation |
| :--- | :--- | :--- |
| **Login** | `/login/secure/` | `/login/insecure/` |
| **Authentication** | Django Auth + Argon2 Hashing | Custom SQL + MD5 (Weak) |
| **Session Storage** | Server-side (Redis) | Client-side Cookie (Base64) |
| **Database Queries** | Django ORM (Parameterized) | Raw SQL String Concatenation |
| **Shopping Cart** | Stored in Redis Session | Stored in manipulation-prone Cookie |
| **Input Validation** | Strict Form Validation | None / Reflected Input |
| **XSS Protection** | Auto-escaping ON | Auto-escaping OFF (`|safe`) |

## etting Started

### Option A: Docker (Recommended)
This spins up the Django App, PostgreSQL, and Redis in isolated containers.

```bash
# 1. Build and Start Containers
docker compose up --build -d

# 2. Initialize Database (Run migrations inside the container)
docker compose exec web python manage.py migrate

# 3. Seed Data (Creates Admin & Test Products)
docker compose exec web python seed_db.py
```

Access the app at: `http://localhost:8000`

### Option B: Local Development
If you prefer running it locally without Docker (uses SQLite by default):

```bash
# 1. Create and Activate Virtual Environment
python3 -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Initialize Database
python manage.py migrate

# 4. Seed Data
python seed_db.py

# 5. Run Server
python manage.py runserver
```

## Usage

### 1. Registration
Go to `/register/` to create an account. This uses the **secure** method by default but also generates a weak hash for the insecure demonstration.

### 2. Exploring Vulnerabilities
*   **SQL Injection**: Go to `/login/insecure/`. Enter Username: `admin' --` (and any password). You will bypass authentication.
*   **Reflected XSS**: Go to `/store/insecure/`. Search for: `<script>alert(1)</script>`.
*   **Stored XSS**: The product "Insecure Dagger" has a malicious payload in its description. Hover over it in the insecure store to trigger it.
*   **Cart Tampering**: Add an item in the insecure store. Inspect your cookies (`insecure_cart`). Decode, modify the price/quantity, encode, and reload.

### 3. Admin Dashboard
Log in to the **Secure** area with the admin account created by `seed_db.py` (User: `admin`, Pass: `adminpass`). Access the dashboard at `/dashboard/`.

## Security Testing
A script is included to verify the vulnerabilities in the insecure path.

```bash
pip install requests
python testing/verify_vulns.py
```
