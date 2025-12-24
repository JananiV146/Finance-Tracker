# Deploying Finance Tracker

This app is a Flask + PyMongo project, ready to deploy on Render, Railway, or Heroku.

## Requirements
- `wsgi.py` exposes `app = create_app()` (present)
- `requirements.txt` includes `gunicorn` (present)
- Set env vars on the platform (do not commit `.env`):
  - `SECRET_KEY`
  - `MONGODB_URI`
  - `MONGODB_DB` (e.g., `finance_tracker`)

## Option A: Render (Recommended)
1. Push the project to GitHub.
2. In Render, create a New Web Service and connect your repo.
3. Settings:
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn wsgi:app`
4. Add Environment Variables:
   - `SECRET_KEY`: your strong secret
   - `MONGODB_URI`: your MongoDB Atlas connection string
   - `MONGODB_DB`: e.g., `finance_tracker`
5. Deploy. Render will provide a URL.

## Option B: Railway
1. Push to GitHub.
2. Create a new Railway project from the repo.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn wsgi:app`
5. Add Environment Variables as above.
6. Deploy.

## Option C: Heroku
1. Ensure `Procfile` exists with:
   ```
   web: gunicorn wsgi:app --log-file - --workers 2 --threads 2 --timeout 60
   ```
2. Push to GitHub and connect the repo in Heroku, or use the CLI.
3. Set Config Vars:
   - `SECRET_KEY`, `MONGODB_URI`, `MONGODB_DB`
4. Deploy.

## Verifying after deploy
- Open the app URL.
- Sign up, log in, add transactions and budgets.
- Check MongoDB Atlas to see new documents in `users`, `transactions`, `budgets`.

## Troubleshooting
- 500 errors on startup: verify env vars are set.
- Mongo connection fails: whitelist IP in Atlas or enable "Access from anywhere (0.0.0.0/0)" for testing.
- Static assets not loading: ensure `templates/base.html` links to `/static/css/styles.css`.
