# Security Testing Plan

## 1. Objective
To validate the security posture of the Secure Storefront and confirm the exploitability of the Insecure Storefront, demonstrating the real-world impact of OWASP Top 10 vulnerabilities.

## 2. Scope
*   **Target Application**: Django Storefront (Localhost:8000)
    *   Secure Path: `/store/secure/`, `/login/secure/`
    *   Insecure Path: `/store/insecure/`, `/login/insecure/`
*   **Excluded**: DOS attacks, infrastructure-level attacks on the host machine.

## 3. Test Cases & Methodology

### 3.1. SQL Injection (A03:2021)
*   **Target**: `/login/insecure/` (POST body `username`)
*   **Method**: Authentication Bypass.
*   **Tool**: `sqlmap`, `curl`, Manual.
*   **Payload**: `admin' --` or `' OR 1=1 --`
*   **Expected Result**:
    *   **Insecure**: Logs in as the first user (likely admin) without a valid password.
    *   **Secure**: Returns "Invalid credentials".

### 3.2. Cross-Site Scripting (XSS) (A03:2021)
*   **Target**: `/store/insecure/`
*   **Method**: Reflected XSS (Search) & Stored XSS (Product Description).
*   **Tool**: Browser Console, `ffuf`.
*   **Payload**: `<script>alert(1)</script>`
*   **Expected Result**:
    *   **Insecure**: Alert box pops up.
    *   **Secure**: Characters are escaped (`&lt;script&gt;`).

### 3.3. Broken Access Control / Insecure Session (A01/A07)
*   **Target**: User Session Cookie (`insecure_sess`).
*   **Method**: Cookie Decoding/Tampering.
*   **Tool**: CyberChef, Browser DevTools.
*   **Attack**: Decode Base64 cookie, change `role` from 'user' to 'admin', re-encode, and refresh `/dashboard/` (if accessible) or `/store/insecure/`.
*   **Expected Result**: Privilege escalation.

## 4. Execution Steps (Kali Linux / Local)

1.  **Start Environment**:
    ```bash
    docker-compose up -d
    ```

2.  **Verify Insecure Login (SQLi)**:
    ```bash
    curl -X POST http://localhost:8000/login/insecure/ \
         -d "username=admin' --&password=anything" \
         -v
    ```
    *Look for a 302 Redirect and `Set-Cookie` header.*

3.  **Run Static Analysis**:
    ```bash
    pip install bandit
    bandit -r . -f txt -o testing/bandit_report.txt
    ```

4.  **Run Dynamic Scan (Optional)**:
    Use OWASP ZAP to spider `http://localhost:8000/login/insecure/`.

## 5. Automated Verification Script
A Python script `verify_vulns.py` is provided in the `testing/` directory to automatically assert that the vulnerabilities are present (for educational grading).
