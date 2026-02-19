# Security Constraints and Implementation Guide (Expanded)

This document serves as the "Blue Team" vs "Red Team" specification. It details the precise implementation of controls and the corresponding flaws.

## 1. Authentication & Session Management (OWASP A07:2021)

### A. Secure Implementation (`/login-secure/`)
*   **Password Hashing**: 
    *   Algorithm: **Argon2id** (memory-hard).
    *   Salt: Unique random salt per user (16 bytes min).
    *   Iterations: Adaptive (minimum 2 iterations, 64MB memory).
    *   Library: `django.contrib.auth.hashers.Argon2PasswordHasher`.
*   **Session Storage**:
    *   Engine: `django.contrib.sessions.backends.cache` (Redis).
    *   ID Generation: High-entropy random string (Django default).
*   **Cookie Attributes**:
    *   `SESSION_COOKIE_HTTPONLY = True`: Prevents XSS theft.
    *   `SESSION_COOKIE_SECURE = True`: HTTPS only.
    *   `SESSION_COOKIE_SAMESITE = 'Strict'`: Prevents CSRF.
*   **MFA**:
    *   Optional expansion: Check for a valid Time-based OTP (TOTP) after password verification.

### B. Insecure Implementation (`/login/`)
*   **Password Hashing**:
    *   Algorithm: **MD5** or **SHA-1**.
    *   Salt: **None** (or a static hardcoded salt like "mysalt").
    *   Implementation: `hashlib.md5(password.encode()).hexdigest()`.
*   **Session Storage**:
    *   **Broken Implementation**: Instead of a server-side session, the implementation sets a generic cookie named `auth_token`.
    *   Format: `base64(username + ":" + md5_password)`. 
    *   Risk: **Privilege Escalation** (attacker decodes, changes username to 'admin', re-encodes).
*   **Cookie Attributes**:
    *   `HttpOnly = False`: Accessible via `document.cookie`.
    *   `SameSite = None` or loose.

## 2. Injection Flaws (OWASP A03:2021)

### A. Secure Implementation
*   **SQL Queries**:
    *   Strict usage of Django ORM methods: `User.objects.get(username=cleaned_data['username'])`.
    *   If raw SQL is needed: `cursor.execute("SELECT * FROM table WHERE id = %s", [param])`.
*   **Input Validation**:
    *   Django Forms (`forms.Form`): Automatic validation of types (Integer, Email).
    *   `clean()` methods to sanitize specific constraints.

### B. Insecure Implementation
*   **SQL Vulnerability**:
    *   Direct string concatenation in a custom View.
    *   Code: `query = f"SELECT * FROM users_appuser WHERE username = '{username}' AND password_insecure = '{weak_hash}'"`
    *   Payload: `admin' --` bypasses password check.
*   **Product Search**:
    *   Code: `cursor.execute("SELECT * FROM products WHERE name LIKE '%" + search_term + "%'")`
    *   Payload: `UNION SELECT 1, database(), 3, 4 --` to extract DB metadata.

## 3. Cryptographic Failures (OWASP A02:2021)

### A. Secure Implementation
*   **Data in Transit**: Enforce HTTPS (via Nginx or Middleware configuration). HSTS header enabled.
*   **Sensitive Data**: Credit Card fields (if mock-implemented) are masked or tokenized.

### B. Insecure Implementation
*   **Data in Transit**: Mixed content allowed. No HSTS.
*   **Sensitive Data**: The "Checkout" form saves Credit Card numbers in plain text in the `Order` model (for demonstration) or logs them to the console.

## 4. Security Misconfiguration & Logging (OWASP A05:2021 / A09:2021)

### A. Secure Implementation
*   **Debug Mode**: `DEBUG = False`.
*   **Headers**:
    *   `X-Content-Type-Options: nosniff`
    *   `X-Frame-Options: DENY`
    *   `Content-Security-Policy`: Default-src 'self'.
*   **Logging**:
    *   Logs generic "Failed login attempt for user X from IP Y".
    *   No sensitive data in logs.

### B. Insecure Implementation
*   **Debug Mode**: `DEBUG = True` (Exposes stack traces and environment variables on 500 errors).
*   **Headers**: Missing strict headers.
*   **Logging**:
    *   Logs full request parameters including passwords!
    *   `print(f"DEBUG: Login attempt with password: {request.POST.get('password')}")`

## 5. Vulnerable Component Management (OWASP A06:2021)

### B. Insecure Implementation (Planned Obsolescence)
*   We will intentionally import an older, vulnerable version of a library (e.g., `PyYAML < 5.4` or `pillow`) in `requirements_insecure.txt` to demonstrate how `pip-audit` or `safety` checks flag it.
