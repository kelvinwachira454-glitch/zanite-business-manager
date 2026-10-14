# Zanite Business Manager

Web-based business management system for SMEs — sales, inventory, expenses, customers, debts, suppliers and reports.

## Stack

Flask, SQLAlchemy, SQLite, Flask-Login, Chart.js, ReportLab, Pandas/openpyxl.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set a real `SECRET_KEY`.

## Run

```bash
python3 app.py
```

Visit `http://127.0.0.1:5000`. The database and tables are created automatically on first run at `database/business.db`.

## Structure

```
app.py                 App factory, blueprint registration
config.py               App configuration
models/                 SQLAlchemy models (business, user, product, sale, expense, customer, debt, supplier)
routes/                 Blueprints: auth, dashboard, inventory, sales, expenses, customers, reports, employees, suppliers, settings
templates/               Jinja2 templates
static/css/style.css     Stylesheet
static/js/app.js         Global JS
utils/decorators.py      Permission enforcement decorator
```

## Roles & Permissions

- **Owner**: full access to everything, including Employees and Settings.
- **Employee**: access is limited to the permissions granted (sales, inventory, expenses, customers, reports), set from the Employees page.

## Notes

- Monetization/billing was intentionally left out of this build.
- Multi-tenant by design: every table is scoped by `business_id`, so each registered business only ever sees its own data.
- CSRF protection is enabled on every form (Flask-WTF), and every POST route rejects requests without a valid token.
- `SECRET_KEY` auto-generates a random key on first run and saves it to `instance/secret_key.txt` if you don't set one in `.env`. That file is gitignored — back it up before redeploying, or every session will be invalidated. In production, set `SECRET_KEY` explicitly in `.env` instead of relying on the auto-generated file.
- Production hardening still needed before going live: a production WSGI server (e.g. gunicorn), migrating to PostgreSQL, automated backups, and a real reverse-proxy TLS setup.

## Deploying over HTTPS

Once your host gives you a real domain with SSL (most platforms — Render, Railway, PythonAnywhere, a VPS behind Caddy/Nginx — handle the TLS termination for you), set these two in your production `.env`:

```
FORCE_HTTPS=true
SESSION_COOKIE_SECURE=true
```

`FORCE_HTTPS=true` redirects any stray `http://` request to `https://`. `SESSION_COOKIE_SECURE=true` stops the browser from ever sending your login cookie over an unencrypted connection. Leave both `false` while developing locally over `http://127.0.0.1` — with `SESSION_COOKIE_SECURE=true` the browser won't set the cookie at all over plain HTTP, so you'd get logged out immediately.

## Deploying to a server

The host must provide Python 3.10+, HTTPS, and a disk that survives restarts and redeploys, because the database is a single file. Hosts with an ephemeral filesystem will erase all business data on every restart.

1. Upload the project. Do not upload `.env`, `database/`, `instance/` or `backups/`.
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` on the server:

```
SECRET_KEY=<paste output of: python -c "import secrets; print(secrets.token_hex(32))">
DATABASE_URL=sqlite:////path/on/persistent/disk/business.db
BACKUP_DIR=/path/on/persistent/disk/backups
FORCE_HTTPS=true
SESSION_COOKIE_SECURE=true
BACKUP_ENABLED=true
```

4. Start the app with gunicorn: `gunicorn app:app --workers 1 --threads 4 --bind 0.0.0.0:$PORT`
   Keep `--workers 1`: SQLite allows one writer at a time, and the built-in backup scheduler starts once per worker.
5. Open the site and register the owner account.
6. Confirm persistence: add a product, restart the service, and check the product is still there.

Do not run `python app.py` on a server. That starts the development server with debug mode on.

## Backups

Your business data lives entirely in `database/business.db`. There's no redundancy for it beyond what you set up yourself. Two ways to back it up, use either or both:

**Option A — automatic, built into the app.** Set these in `.env`:

```
BACKUP_ENABLED=true
BACKUP_INTERVAL_HOURS=24
BACKUP_RETENTION_COUNT=14
```

While `app.py` is running, it takes a safe snapshot of the database (using SQLite's own backup API, so it's never caught mid-write) into a `backups/` folder, on the interval you set, keeping the most recent `BACKUP_RETENTION_COUNT` copies and deleting older ones automatically. The first backup runs as soon as the app starts, then repeats on that interval. This only backs up to the *same server* the app runs on — it protects you against database corruption or an accidental bad write, but not against the whole server/disk failing. Copy the `backups/` folder off-server periodically (or point it at a mounted cloud drive) for real disaster protection.

**Option B — scheduled externally.** Run `python backup_db.py` (or `python3 backup_db.py`) from the project folder — it takes one backup and exits, so it's meant to be triggered by something else on a schedule:
- **Windows**: Task Scheduler → create a task that runs `python backup_db.py` with "Start in" set to your project folder, on whatever schedule you like.
- **Linux/Mac**: a cron job, e.g. `0 2 * * * cd /path/to/zanite-business-manager && venv/bin/python backup_db.py` for a nightly 2am backup.
- Most hosting platforms (Render, Railway, PythonAnywhere, etc.) also offer their own scheduled-job feature that can run this same command.

**Restoring from a backup**: stop the app, replace `database/business.db` with the backup file you want to restore (rename it to exactly `business.db`), then start the app again.