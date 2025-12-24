from flask import Blueprint, render_template, g
from datetime import date, timedelta
from collections import defaultdict
from auth import login_required
from db import month_income_expense, spend_by_category

bp = Blueprint('reports', __name__, url_prefix='/reports')


def month_sequence(n: int):
    today = date.today().replace(day=1)
    months = []
    y, m = today.year, today.month
    for _ in range(n):
        months.append(f"{y:04d}-{m:02d}")
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    return list(reversed(months))


@bp.route('/')
@login_required
def index():
    user = g.user
    months = month_sequence(6)

    # Income/Expense per month for last 6 months (MongoDB)
    month_ie = month_income_expense(user['id'], months)

    # Category breakdown for current month (expenses)
    curr_month = months[-1]
    spend_map = spend_by_category(user['id'], curr_month)
    cat_rows = sorted([
        {'category': k, 'total': v} for k, v in spend_map.items()
    ], key=lambda x: x['total'], reverse=True)

    return render_template(
        'reports/index.html',
        months=months,
        month_income=[month_ie[m]['income'] for m in months],
        month_expense=[month_ie[m]['expense'] for m in months],
        categories=[r['category'] for r in cat_rows],
        cat_totals=[float(r['total']) for r in cat_rows],
        curr_month=curr_month,
    )
