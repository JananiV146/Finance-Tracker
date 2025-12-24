# Finance Tracker (Flask)

A simple full-stack finance tracker with authentication, transaction management, budgeting, and reports with Chart.js.

## Features
- Authentication: signup, login, logout (session-based)
- Dashboard: balance, totals, recent transactions, monthly budgets progress
- Transactions: add/edit/delete income and expenses with categories
- Budgets: monthly and category-specific budgets
- Reports: income vs expenses trend and category breakdown (Chart.js)

## Getting Started

1. Create and activate a virtual environment (optional but recommended)

```bash
python -m venv .venv
. .venv/Scripts/activate  # on Windows PowerShell: .venv\Scripts\Activate.ps1
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app

```bash
python app.py
```

4. Open http://127.0.0.1:5000 in your browser

- Sign up first, then start adding transactions and budgets.

## Notes
- Uses SQLite database stored at `finance.db` in the project root.
- Default `SECRET_KEY` in `app.py` is for development. Change it for production.
- For OAuth, you can later integrate providers (Google/GitHub) via libraries like `authlib`.
