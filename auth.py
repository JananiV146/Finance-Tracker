from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from typing import Optional
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from db import create_user, find_user_by_username, find_user_by_id, update_user_password

bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


def get_current_user() -> Optional[dict]:
    uid = session.get('user_id')
    if not uid:
        return None
    row = find_user_by_id(uid)
    return row if row else None


def get_serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(secret_key=current_app.config['SECRET_KEY'], salt='auth-reset')


def validate_password(password: str) -> Optional[str]:
    """Return None if OK, else an error message describing the first failed rule."""
    if len(password) < 8:
        return 'Password must be at least 8 characters long.'
    if not any(c.islower() for c in password):
        return 'Password must contain at least one lowercase letter.'
    if not any(c.isupper() for c in password):
        return 'Password must contain at least one uppercase letter.'
    if not any(c.isdigit() for c in password):
        return 'Password must contain at least one digit.'
    if not any(c in "!@#$%^&*()-_=+[]{};:'\",.<>/?|`~" for c in password):
        return 'Password must contain at least one special character.'
    return None


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm = request.form.get('confirm', '').strip()
        if not username:
            flash('Username is required.', 'danger')
            return render_template('auth/signup.html')
        if not password:
            flash('Password is required.', 'danger')
            return render_template('auth/signup.html')
        if password != confirm:
            flash('Password and confirmation do not match.', 'danger')
            return render_template('auth/signup.html')
        pw_err = validate_password(password)
        if pw_err:
            flash(pw_err, 'danger')
            return render_template('auth/signup.html')
        # Check if exists
        existing = find_user_by_username(username)
        if existing:
            flash('This username is already taken. Please choose another one.', 'warning')
            return render_template('auth/signup.html')
        try:
            pwd_hash = generate_password_hash(password)
            user_id = create_user(username, pwd_hash)
        except Exception:
            # Fallback if DB unique constraint triggers
            flash('This username is already taken. Please choose another one.', 'warning')
            return render_template('auth/signup.html')
        session['user_id'] = user_id
        flash('Account created! Welcome.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('auth/signup.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = find_user_by_username(username)
        if not user or not check_password_hash(user['password_hash'], password):
            flash('Invalid username or password.', 'danger')
            return render_template('auth/login.html')
        session['user_id'] = user['id']
        flash('Logged in successfully.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('auth/login.html')


@bp.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('auth.login'))


@bp.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if not username:
            flash('Please enter your username.', 'danger')
            return render_template('auth/forgot.html', reset_link=None)
        user = find_user_by_username(username)
        if not user:
            # Don't reveal whether user exists; still show generic success
            flash('If the account exists, a reset link has been generated.', 'info')
            return render_template('auth/forgot.html', reset_link=None)
        s = get_serializer()
        token = s.dumps({'uid': user['id']})
        reset_link = url_for('auth.reset_password', token=token, _external=True)
        flash('A password reset link has been generated below (demo mode).', 'info')
        return render_template('auth/forgot.html', reset_link=reset_link)
    return render_template('auth/forgot.html', reset_link=None)


@bp.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token: str):
    s = get_serializer()
    try:
        data = s.loads(token, max_age=3600)  # 1 hour validity
        uid = data.get('uid')
    except SignatureExpired:
        flash('Reset link has expired. Please request a new one.', 'warning')
        return redirect(url_for('auth.forgot'))
    except BadSignature:
        flash('Invalid reset link.', 'danger')
        return redirect(url_for('auth.forgot'))

    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        confirm = request.form.get('confirm', '').strip()
        if password != confirm:
            flash('Password and confirmation do not match.', 'danger')
            return render_template('auth/reset.html')
        pw_err = validate_password(password)
        if pw_err:
            flash(pw_err, 'danger')
            return render_template('auth/reset.html')
        pwd_hash = generate_password_hash(password)
        update_user_password(uid, pwd_hash)
        flash('Password has been reset. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset.html')
