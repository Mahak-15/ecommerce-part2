# ecommerce-part1 — FORMA Full-Stack Store + Admin Tools

A runnable full-stack e-commerce catalogue with a FastAPI/Python backend, SQLite database, FORMA storefront, admin visitor analytics, simulated IP-to-country mapping, and a live CSS generator with stylesheet download.

## 1. Requirements

- Windows 10/11, macOS, or Linux
- Python 3.10 or newer (Python 3.12 recommended)
- Internet connection only if product images / Google Fonts are loaded from external hosts
- VS Code is optional

Check Python:

```bash
python --version
```

On some macOS/Linux systems use `python3 --version`.

## 2. Extract and open the project

1. Extract `ecommerce-part1.zip`.
2. Open the extracted `ecommerce_part1` folder in VS Code.
3. Confirm the folder contains `app`, `sql`, `requirements.txt`, and `README.md`.
4. Open a terminal in that exact folder (the project root).

Do not run commands from the parent ZIP folder or from `app/static`.

## 3. Create a virtual environment

### Windows Command Prompt

```cmd
python -m venv .venv
.venv\Scripts\activate
```

If PowerShell is used:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt or run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

When activated, the terminal usually shows `(.venv)`.

## 4. Install dependencies

From the project root:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The required packages are FastAPI and Uvicorn. No external GeoIP package is required because demo country mapping uses local fixtures.

## 5. Configure the admin token

The application is configured for local learning/demo use. The default token is:

```text
forma-admin-local
```

For a safer local token, set an environment variable before starting the server.

Windows CMD (this terminal session only):

```cmd
set FORMA_ADMIN_TOKEN=choose-a-long-random-local-token
```

PowerShell:

```powershell
$env:FORMA_ADMIN_TOKEN="choose-a-long-random-local-token"
```

macOS/Linux:

```bash
export FORMA_ADMIN_TOKEN='choose-a-long-random-local-token'
```

If you do not set the variable, use the default `forma-admin-local` token. Never deploy the default token publicly. This demo uses a shared admin token, not a production user-account system.

## 6. Start the application

Run from the project root with the virtual environment active:

```bash
python -m uvicorn app.main:app --reload
```

Expected message includes:

```text
Uvicorn running on http://127.0.0.1:8000
```

Open these pages:

- Storefront: http://127.0.0.1:8000/
- Admin analytics: http://127.0.0.1:8000/admin/
- CSS Generator: http://127.0.0.1:8000/admin/css-generator
- Interactive API docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/api/health

Do not use VS Code Live Server (port 5500). FastAPI serves the frontend and API from the same origin.

To stop the server, focus the terminal and press `Ctrl+C`.

## 7. First run and database

On startup, FastAPI runs `initialise_database()` from `app/database.py`. The SQL script creates the product and analytics tables if missing. Existing product seed data is inserted if the products table is empty.

The SQLite file is:

```text
ecommerce.db
```

It is created in the project root. Do not delete it if you want to keep analytics records or imported products.

## 8. Use the FORMA storefront

1. Open http://127.0.0.1:8000/.
2. Browse the catalogue.
3. Search products using the search field.
4. Filter by category.
5. Change sort order.
6. Select a product card to open its details.
7. The page requests product data from FastAPI; it does not query SQLite directly.

## 9. Use the admin analytics dashboard

1. Open http://127.0.0.1:8000/admin/.
2. Enter the admin token configured in Step 5 (default: `forma-admin-local`).
3. Click **Connect**.
4. The dashboard loads total visits, unique IPs, simulated visits, country totals, daily counts and recent events from SQLite.
5. Enter a number between 1 and 500 in the simulation field.
6. Click **Generate visits**.
7. The simulator inserts that many sample events and refreshes the dashboard.
8. Each event is marked `SIMULATED`.

### Simulated IP-to-country mapping

The simulator uses the following documentation-only addresses:

| IP address | Demo country |
|---|---|
| 203.0.113.10 | Australia |
| 198.51.100.20 | India |
| 192.0.2.30 | United States |
| 203.0.113.40 | United Kingdom |
| 198.51.100.50 | Germany |

These are reserved documentation/test IP addresses. They are not real user addresses and have not been geolocated. The country mapping is a deterministic fixture for demonstration.

The dashboard currently analyses generated events. It does not claim to identify the actual country of real visitors. Real GeoIP would require a separate licensed/current GeoIP database and privacy review.

## 10. Use the CSS Generator

1. Open http://127.0.0.1:8000/admin/css-generator.
2. Change primary, accent, background and text colours.
3. Select a font.
4. Adjust font size, content width, page padding, card radius, card gap, button radius and section spacing.
5. Watch the preview update immediately.
6. Review the generated CSS text.
7. Click **Reset defaults** to restore the FORMA starting values.
8. Click **Download CSS** to save `forma-custom-theme.css`.

The downloaded file is a theme stylesheet. It does not automatically overwrite the live site. To apply it to the storefront:

1. Copy `forma-custom-theme.css` into `app/static/`.
2. Open `app/static/index.html`.
3. Add this line after the existing `/static/styles.css` link:

   ```html
   <link rel="stylesheet" href="/static/forma-custom-theme.css">
   ```

4. Save and refresh the storefront with `Ctrl+F5`.

Keep a backup of your original `styles.css`. The generated CSS uses a controlled set of CSS variables and selectors; it does not accept arbitrary CSS code.

## 11. API endpoints

### Existing product API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Check server status |
| GET | `/api/categories` | List categories |
| GET | `/api/products` | Search/filter/sort/page products |
| GET | `/api/products/{product_id}` | Product details |

### Admin analytics API

All admin endpoints require this HTTP header:

```http
Authorization: Bearer forma-admin-local
```

Replace the example token if you configured `FORMA_ADMIN_TOKEN`.

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/admin/analytics/simulate` | Insert 1–500 simulated visits |
| GET | `/api/admin/analytics/summary` | Totals, countries and daily counts |
| GET | `/api/admin/analytics/events` | Recent events; supports `limit` and `offset` |
| DELETE | `/api/admin/analytics` | Clear analytics events |

Example simulation body:

```json
{"count": 25}
```

You can test protected endpoints in `/docs`: click **Authorize** if available, or use a REST client and provide the Authorization header. The admin UI sends the header automatically after you connect.

## 12. Project structure

```text
ecommerce_part1/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   └── static/
│       ├── index.html
│       ├── styles.css
│       ├── app.js
│       └── admin/
│           ├── index.html
│           ├── admin.css
│           ├── analytics.js
│           ├── css-generator.html
│           ├── css-generator.css
│           └── css-generator.js
├── sql/
│   ├── schema.sql
│   └── seed.sql
├── tests/
├── screenshots/
├── requirements.txt
├── ecommerce.db
└── README.md
```

## 13. Troubleshooting

### `python` is not recognised

Install Python from https://www.python.org/downloads/ and enable **Add Python to PATH** during installation. Close and reopen the terminal, then check `python --version`. On Windows, `py --version` may also work; if so, use `py -m ...` in place of `python -m ...`.

### `No module named fastapi`

Activate `.venv` and run:

```bash
python -m pip install -r requirements.txt
```

### `Could not import module "app.main"`

Make sure the terminal is in the project root containing the `app` directory. Run:

```bash
dir
```

On macOS/Linux use `ls`. You should see `app`, `sql`, and `requirements.txt`.

### Port 8000 is already in use

Stop the other server, or run:

```bash
python -m uvicorn app.main:app --reload --port 8001
```

Then use `http://127.0.0.1:8001/` and corresponding admin URLs.

### Admin says 401 / token incorrect

The token in the admin page must exactly match `FORMA_ADMIN_TOKEN` in the terminal that started Uvicorn. If the environment variable was set after the server started, stop and restart Uvicorn. Re-enter the token and click Connect.

### Dashboard has no visits

Connect with the token, then click **Generate visits**. Analytics starts empty; this is expected.

### Product list is empty

Check that `ecommerce.db` exists and that `sql/seed.sql` contains seed products. The database is initialised on application startup. If the project was supplied with an existing populated DB, do not delete it.

### CSS download does not visibly change the live storefront

The download creates a file only. Follow Step 10 to copy it into `app/static/` and link it after `styles.css`.

## 14. Important security and privacy notes

This is an educational/local demo, not a production-ready commerce platform.

- The default admin token is public in this README; change it before use beyond localhost.
- Use HTTPS, real admin accounts, password hashing, secure sessions, and role-based authorization before public deployment.
- Do not trust arbitrary `X-Forwarded-For` headers.
- IP addresses can be personal data. Minimise collection, limit access, document retention, and follow applicable privacy law.
- The simulated country fixture is not real geolocation.
- The simulator is an admin-only test endpoint and should be disabled or tightly protected in production.

## 15. Quick start summary

Windows CMD:

```cmd
cd path\to\ecommerce_part1
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
set FORMA_ADMIN_TOKEN=your-local-secret
python -m uvicorn app.main:app --reload
```

Then browse to `http://127.0.0.1:8000/`.

Admin: `http://127.0.0.1:8000/admin/`  
CSS Generator: `http://127.0.0.1:8000/admin/css-generator`

If you omit the `set FORMA_ADMIN_TOKEN=...` command, use the demo token `forma-admin-local`.
