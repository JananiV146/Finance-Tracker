from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from datetime import date
from auth import login_required
from db import (
    list_transactions as db_list_transactions,
    insert_transaction,
    find_transaction as db_find_transaction,
    update_transaction as db_update_transaction,
    delete_transaction as db_delete_transaction,
)

bp = Blueprint('transactions', __name__, url_prefix='/transactions')


@bp.route('/')
@login_required
def list_transactions():
    user = g.user
    txs = db_list_transactions(user['id'])
    return render_template('transactions/list.html', txs=txs)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    if request.method == 'POST':
        user = g.user
        date_str = request.form.get('date') or date.today().isoformat()
        ttype = request.form.get('type')
        amount = request.form.get('amount')
        category = request.form.get('category', 'General')
        description = request.form.get('description', '')
        try:
            amt = float(amount)
            if ttype not in ('income', 'expense'):
                raise ValueError('Invalid type')
        except Exception:
            flash('Please provide valid values.', 'danger')
            return render_template('transactions/add_edit.html', tx=None)
        insert_transaction(user['id'], date_str, ttype, amt, category, description)
        flash('Transaction added.', 'success')
        return redirect(url_for('transactions.list_transactions'))
    return render_template('transactions/add_edit.html', tx=None)


@bp.route('/<tx_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_transaction(tx_id: int):
    user = g.user
    tx = db_find_transaction(user['id'], str(tx_id))
    if not tx:
        flash('Transaction not found.', 'warning')
        return redirect(url_for('transactions.list_transactions'))
    if request.method == 'POST':
        date_str = request.form.get('date') or date.today().isoformat()
        ttype = request.form.get('type')
        amount = request.form.get('amount')
        category = request.form.get('category', 'General')
        description = request.form.get('description', '')
        try:
            amt = float(amount)
            if ttype not in ('income', 'expense'):
                raise ValueError('Invalid type')
        except Exception:
            flash('Please provide valid values.', 'danger')
            return render_template('transactions/add_edit.html', tx=tx)
        db_update_transaction(user['id'], str(tx_id), {
            'date': date_str,
            'type': ttype,
            'amount': amt,
            'category': category,
            'description': description,
        })
        flash('Transaction updated.', 'success')
        return redirect(url_for('transactions.list_transactions'))
    return render_template('transactions/add_edit.html', tx=tx)


@bp.route('/<tx_id>/delete', methods=['POST'])
@login_required
def delete_transaction(tx_id: int):
    user = g.user
    db_delete_transaction(user['id'], str(tx_id))
    flash('Transaction deleted.', 'info')
    return redirect(url_for('transactions.list_transactions'))
