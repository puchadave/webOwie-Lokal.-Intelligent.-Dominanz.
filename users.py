from flask import Blueprint, request, render_template, redirect, url_for, session, current_app, flash
from werkzeug.security import generate_password_hash, check_password_hash
from accounting import db
from datetime import datetime
import json

auth_bp = Blueprint('auth', __name__, template_folder='templates')


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(32), default='user')  # 'admin' or 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class MerchantAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    provider = db.Column(db.String(64))
    account_details = db.Column(db.Text)  # JSON encoded details
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))


class UserPermission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    permission_id = db.Column(db.Integer, db.ForeignKey('permission.id'))


def user_has_permission(user, perm_name):
    if not user:
        return False
    # admins have all permissions
    if getattr(user, 'role', None) == 'admin':
        return True
    perm = Permission.query.filter_by(name=perm_name).first()
    if not perm:
        return False
    up = UserPermission.query.filter_by(user_id=user.id, permission_id=perm.id).first()
    return bool(up)


def permission_required(perm_name):
    def decorator(f):
        from functools import wraps

        @wraps(f)
        def wrapped(*args, **kwargs):
            u = current_user()
            if not user_has_permission(u, perm_name):
                return "Forbidden: missing permission", 403
            return f(*args, **kwargs)

        return wrapped

    return decorator


def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    return User.query.get(uid)


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    open_reg = current_app.config.get('OPEN_REGISTRATION', False)
    # Allow registration if open OR an admin is creating accounts (session admin)
    allow = open_reg or session.get('user_role') == 'admin'

    if request.method == 'POST':
        if not allow:
            return "Registration is disabled", 403
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email')
        if User.query.filter_by(username=username).first():
            flash('Username already taken')
            return render_template('register.html', open_registration=open_reg)
        user = User(username=username, email=email, role='user')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Optional: setup a MerchantAccount ("Kasse") during registration
        setup_kasse = request.form.get('setup_kasse')
        if setup_kasse:
            provider = request.form.get('kasse_provider')
            account_id = request.form.get('kasse_account')
            details = {'account_id': account_id}
            m = MerchantAccount(user_id=user.id, provider=provider, account_details=json.dumps(details))
            db.session.add(m)
            db.session.commit()

        session['user_id'] = user.id
        session['user_role'] = user.role
        return redirect(url_for('index'))
    return render_template('register.html', open_registration=open_reg)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_role'] = user.role
            return redirect(url_for('index'))
        flash('Invalid credentials')
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_role', None)
    return redirect(url_for('login'))


@auth_bp.route('/users')
@login_required
def users_list():
    # admin-only view
    if session.get('user_role') != 'admin':
        return "Forbidden", 403
    users = User.query.order_by(User.created_at.desc()).all()
    # build permission mapping for template: user_id -> [perm_name,...]
    perm_map = {}
    for u in users:
        perms = Permission.query.join(UserPermission, Permission.id == UserPermission.permission_id).filter(UserPermission.user_id == u.id).all()
        perm_map[u.id] = [p.name for p in perms]

    all_perms = Permission.query.order_by(Permission.name).all()
    return render_template('users.html', users=users, perm_map=perm_map, all_perms=all_perms)


@auth_bp.route('/user/<int:user_id>/role', methods=['POST'])
@login_required
def change_role(user_id):
    # admin-only
    if session.get('user_role') != 'admin':
        return "Forbidden", 403
    new_role = request.form.get('role')
    if new_role not in ('user', 'admin'):
        return "Invalid role", 400
    user = User.query.get_or_404(user_id)
    user.role = new_role
    db.session.commit()
    return redirect(url_for('auth.users_list'))


@auth_bp.route('/user/<int:user_id>/permissions', methods=['POST'])
@login_required
def grant_permission(user_id):
    if session.get('user_role') != 'admin':
        return "Forbidden", 403
    perm_name = request.form.get('perm')
    if not perm_name:
        return redirect(url_for('auth.users_list'))
    perm = Permission.query.filter_by(name=perm_name).first()
    if not perm:
        perm = Permission(name=perm_name, description='')
        db.session.add(perm)
        db.session.commit()
    # avoid duplicates
    exists = UserPermission.query.filter_by(user_id=user_id, permission_id=perm.id).first()
    if not exists:
        up = UserPermission(user_id=user_id, permission_id=perm.id)
        db.session.add(up)
        db.session.commit()
    return redirect(url_for('auth.users_list'))


@auth_bp.route('/user/<int:user_id>/permissions/revoke', methods=['POST'])
@login_required
def revoke_permission(user_id):
    if session.get('user_role') != 'admin':
        return "Forbidden", 403
    perm_name = request.form.get('perm')
    if not perm_name:
        return redirect(url_for('auth.users_list'))
    perm = Permission.query.filter_by(name=perm_name).first()
    if not perm:
        return redirect(url_for('auth.users_list'))
    up = UserPermission.query.filter_by(user_id=user_id, permission_id=perm.id).first()
    if up:
        db.session.delete(up)
        db.session.commit()
    return redirect(url_for('auth.users_list'))
