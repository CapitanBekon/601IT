# System Outline: Vulnerable Online Storefront (Expanded)

## 1. Overview
The application is a comprehensive online storefront built with Django 5.x, explicitly designed to demonstrate the stark contrast between secure and insecure coding practices. It features two distinct authentication pathways affecting the entire user session lifecycle, from login to checkout.

## 2. Core Architecture

### 2.1. Dual-Path Logic
The application will serve two versions of critical features based on the entry point:
*   **Green Path (Secure)**: Access via `/secure/*`. Enforces strict security controls.
*   **Red Path (Insecure)**: Access via `/insecure/*`. Deliberately bypasses controls, exposing OWASP Top 10 vulnerabilities.

### 2.2. Pages & Routing

#### Public Area
*   **Home Page (`/`)**: 
    *   Landing page with a clear visual split: "Enter Secure Store" vs. "Enter Vulnerable Store".
    *   System status indicator (Database connection, Redis status).
*   **Product Catalog (`/store/`)**:
    *   **Secure View**: Products rendered with auto-escaping. Price/ID validation before rendering.
    *   **Insecure View**: Vulnerable to XSS (e.g., product descriptions containing raw HTML/JS). ID parameter vulnerable to SQLi (`/store/product?id=1 OR 1=1`).

#### Authentication Modules
*   **Secure Login (`/login-secure/`)**:
    *   **Form**: Username, Password, MFA Token (simulated/optional).
    *   **Backend**: Uses `django.contrib.auth`.
    *   **Validation**: Server-side validation of input length/type.
    *   **Feedback**: Generic error messages ("Invalid credentials").
    *   **Protection**: CSRF tokens required. Rate-limited (5 attempts/min).
*   **Insecure Login (`/login/`)**:
    *   **Form**: Username, Password.
    *   **Backend**: Custom raw SQL query construction.
    *   **Vulnerability**: SQL Injection (`' OR '1'='1`).
    *   **Feedback**: Verbose error checking ("User found, password incorrect").
    *   **Protection**: CSRF exempt. No rate limiting.

#### User Operations
*   **Registration (`/register/`)**:
    *   Creates a single user record but generates **two** password hashes:
        1.  `password_hash_secure`: Argon2id (via `cryptography.hazmat` or Django's default).
        2.  `password_hash_insecure`: MD5 (via `hashlib`, unsalted).
*   **Shopping Cart (`/cart/`)**:
    *   **Secure**: Stores items in Redis key keyed by a signed session ID. Validates stock and pricing on checkout.
    *   **Insecure**: Stores cart serialized in a base64 cookie. Vulnerable to "Cookie Replay" or price tampering (user edits cookie to change price to 0).

#### Administration
*   **Admin Dashboard (`/dashboard/`)**:
    *   **Access Control**: `@user_passes_test(is_superuser)` decorator.
    *   **Features**:
        *   **User Inspector**: View all users. Show raw MD5 hashes (demonstrating why fast hashes are bad) vs Argon2 hashes.
        *   **SQL Monitor**: Log of the last 10 executed SQL queries to visualize the injection vs parameterized difference.
        *   **Session Spy**: View active session cookies for insecure users.

### 2.3. Data Model (Detailed)

*   **Custom User Model (`AppUser`)**:
    *   `username` (String, Unique)
    *   `email` (String)
    *   `password_secure` (TextField): Django standard hash (PBKDF2/Argon2).
    *   `password_insecure` (TextField): Raw MD5 hash (simulated legacy storage).
    *   `is_admin` (Boolean)

*   **Product Model**:
    *   `name` (String)
    *   `description` (TextField): May contain HTML for XSS demo.
    *   `price` (Decimal)
    *   `stock_qty` (Integer)

*   **Order Model**:
    *   `user` (ForeignKey)
    *   `total` (Decimal)
    *   `status` (Enum: Pending, Paid)
    *   `created_at` (Timestamp)

*   **Cart (Redis/Session)**:
    *   Structure: `{ "user_id": 123, "items": [{"id": 1, "qty": 2, "price": 10.00}] }`

## 3. Technology Stack specifics

*   **Backend**: Django 5.x.
*   **Database**: PostgreSQL (Production-grade for Docker), SQLite (Local dev fallback).
*   **Caching/Session**: Redis 7.x (Critical for secure session management).
*   **Containerization**:
    *   `web` (Django + Gunicorn/Uvicorn)
    *   `db` (Postgres 16)
    *   `cache` (Redis 7)
    *   `nginx` (Reverse proxy - optional, but good for demonstrating headers).
*   **Security Libraries**:
    *   **Secure**: `cryptography`, `bcrypt`, `argon2-cffi`.
    *   **Insecure**: `hashlib` (standard lib, used incorrectly).
