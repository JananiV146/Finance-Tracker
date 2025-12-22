from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from auth import login_required
from db import (
    list_budgets as db_list_budgets,
    add_budget as db_add_budget,
    find_budget as db_find_budget,
    update_budget as db_update_budget,
    delete_budget as db_delete_budget,
)

bp = Blueprint('budgeting', __name__, url_prefix='/budgets')


@bp.route('/')
@login_required
def list_budgets():
    user = g.user
    budgets = db_list_budgets(user['id'])
    return render_template('budgets/list.html', budgets=budgets)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_budget():
    if request.method == 'POST':
        user = g.user
        month = (request.form.get('month') or '').strip()  # YYYY-MM
        category = (request.form.get('category') or '').strip() or None
        amount = request.form.get('amount')
        try:
            amt = float(amount)
            if not month or len(month) != 7 or month[4] != '-':
                raise ValueError('Invalid month')
        except Exception:
            flash('Please provide valid values.', 'danger')
            return render_template('budgets/add_edit.html', budget=None)
        try:
            res_id = db_add_budget(user['id'], month, amt, category)
            if not res_id:
                raise Exception('duplicate')
        except Exception:
            flash('Budget for this month/category already exists.', 'warning')
            return render_template('budgets/add_edit.html', budget=None)
        flash('Budget added.', 'success')
        return redirect(url_for('budgeting.list_budgets'))
    return render_template('budgets/add_edit.html', budget=None)


@bp.route('/<bid>/edit', methods=['GET', 'POST'])
@login_required
def edit_budget(bid: int):
    user = g.user
    budget = db_find_budget(user['id'], str(bid))
    if not budget:
        flash('Budget not found.', 'warning')
        return redirect(url_for('budgeting.list_budgets'))
    if request.method == 'POST':
        month = (request.form.get('month') or '').strip()
        category = (request.form.get('category') or '').strip() or None
        amount = request.form.get('amount')
        try:
            amt = float(amount)
            if not month or len(month) != 7 or month[4] != '-':
                raise ValueError('Invalid month')
        except Exception:
            flash('Please provide valid values.', 'danger')
            return render_template('budgets/add_edit.html', budget=budget)
        # Note: Keeping unique constraint; could conflict if changed month/category to an existing one
        try:
            ok = db_update_budget(user['id'], str(bid), month, amt, category)
            if not ok:
                raise Exception('conflict')
        except Exception:
            flash('A budget with this month/category already exists.', 'warning')
            return render_template('budgets/add_edit.html', budget=budget)
        flash('Budget updated.', 'success')
        return redirect(url_for('budgeting.list_budgets'))
    return render_template('budgets/add_edit.html', budget=budget)


@bp.route('/<bid>/delete', methods=['POST'])
@login_required
def delete_budget(bid: int):
    user = g.user
    db_delete_budget(user['id'], str(bid))
    flash('Budget deleted.', 'info')
    return redirect(url_for('budgeting.list_budgets'))
