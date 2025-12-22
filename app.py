from flask import Flask, render_template, redirect, url_for
from flask import g
from datetime import date
import os
from dotenv import load_dotenv

from db import ensure_indexes, totals as db_totals, recent_transactions, budgets_for_month, spend_by_category
from auth import bp as auth_bp, get_current_user, login_required


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')

    # Initialize DB indexes (MongoDB)
    ensure_indexes()

    # Register blueprints
    app.register_blueprint(auth_bp)

    # Lazy imports to avoid circular deps for blueprints
    from transactions import bp as tx_bp
    from budgeting import bp as budget_bp
    from reports import bp as reports_bp

    app.register_blueprint(tx_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(reports_bp)

    @app.before_request
    def load_user():
        g.user = get_current_user()

    @app.route('/')
    def home():
        if g.user:
            return redirect(url_for('dashboard'))
        return render_template('home.html')

    @app.route('/dashboard')
    @login_required
    def dashboard():
        user = g.user
        # Totals
        t = db_totals(user['id'])
        income_total = t.get('income', 0.0)
        expense_total = t.get('expense', 0.0)
        balance = income_total - expense_total

        # Recent transactions
        recent = recent_transactions(user['id'], limit=10)

        # Current month for budgets
        month = date.today().strftime('%Y-%m')
        budgets = budgets_for_month(user['id'], month)

        # Spend per category for month
        spend_map = spend_by_category(user['id'], month)

        return render_template(
            'dashboard.html',
            balance=balance,
            income_total=income_total,
            expense_total=expense_total,
            recent=recent,
            budgets=budgets,
            spend_map=spend_map,
            month=month
        )

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
