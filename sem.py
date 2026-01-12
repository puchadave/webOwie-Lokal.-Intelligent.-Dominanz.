from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from datetime import datetime
from accounting import db
import threading

try:
    from users import login_required, current_user, user_has_permission
except Exception:
    def login_required(f):
        return f
    def current_user():
        return None
    def user_has_permission(u, name):
        return False

# Ad connector helper import
try:
    from connectors import get_ads_connector
except Exception:
    get_ads_connector = None

sem_bp = Blueprint('sem', __name__, template_folder='templates')


class SEOTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_url = db.Column(db.String(1024))
    action = db.Column(db.String(255))
    status = db.Column(db.String(50), default='pending')
    result = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@sem_bp.route('/')
def dashboard():
    # Overview landing
    return render_template('sem_dashboard.html')


@sem_bp.route('/kpis')
@login_required
def kpis():
    # For now return placeholder KPIs; real implementation aggregates analytics
    data = {
        'organic_sessions': 1234,
        'paid_sessions': 456,
        'conversions': 78,
        'avg_position': 3.4,
        'ctr': 4.5
    }
    return render_template('sem_kpis.html', kpis=data)


@sem_bp.route('/seo/optimize', methods=['POST'])
@login_required
def seo_optimize():
    # Requires permission to run automation
    u = current_user()
    if not user_has_permission(u, 'run_automation'):
        return jsonify({'error': 'Forbidden: missing permission run_automation'}), 403

    data = request.get_json() or {}
    url = data.get('url')
    actions = data.get('actions', ['meta', 'content', 'links'])

    # enqueue a simple SEO task
    t = SEOTask(target_url=url, action=','.join(actions))
    db.session.add(t)
    db.session.commit()

    def worker(task_id, url, actions):
        # placeholder: perform analyses (OSINT/SOCMINT/HUMINT) and apply changes
        # This would call external crawlers, LLMs, and CMS APIs in production
        import time
        time.sleep(1)
        t = SEOTask.query.get(task_id)
        t.status = 'done'
        t.result = f'Applied actions: {actions} on {url}'
        db.session.commit()

    threading.Thread(target=worker, args=(t.id, url, actions)).start()
    return jsonify({'task_id': t.id}), 202


@sem_bp.route('/sea', methods=['GET', 'POST'])
@login_required
def sea():
    # Manage SEA campaigns and connectors
    if request.method == 'POST':
        # simple action: trigger ad API call
        if not user_has_permission(current_user(), 'manage_sea'):
            return jsonify({'error': 'Forbidden: missing permission manage_sea'}), 403
        data = request.get_json() or {}
        provider = data.get('provider')
        action = data.get('action')
        payload = data.get('payload', {})
        # Use connectors.get_ads_connector if available
        try:
            from connectors import get_ads_connector
            conn = get_ads_connector(provider)
            res = conn.perform_action(action, payload)
            return jsonify({'result': res})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return render_template('sem_sea.html')


@sem_bp.route('/config')
@login_required
def config():
    # show config page and detect connected ad providers (per-tenant storage)
    import os
    import time
    tenant = os.environ.get('TENANT')
    if tenant:
        token_dir = os.path.join('storage', 'tenants', tenant, 'ads')
    else:
        token_dir = os.path.join('storage', 'ads')
    os.makedirs(token_dir, exist_ok=True)

    providers = ['google_ads', 'facebook_ads', 'instagram_ads', 'linkedin']
    connected = {}
    now = datetime.utcnow()
    def human_age(ts):
        try:
            delta = now - datetime.fromtimestamp(ts)
        except Exception:
            return None
        secs = int(delta.total_seconds())
        if secs < 60:
            return f"{secs}s ago"
        mins = secs // 60
        if mins < 60:
            return f"{mins}m ago"
        hrs = mins // 60
        if hrs < 24:
            return f"{hrs}h ago"
        days = hrs // 24
        if days < 7:
            return f"{days}d ago"
        weeks = days // 7
        return f"{weeks}w ago"

    for p in providers:
        token_path = os.path.join(token_dir, f'{p}_token.json')
        exists = os.path.exists(token_path)
        token_mtime = None
        token_age = None
        if exists:
            try:
                token_mtime = os.path.getmtime(token_path)
                token_age = human_age(token_mtime)
            except Exception:
                token_mtime = None
                token_age = None
        connected[p] = {
            'connected': exists,
            'token_path': token_path if exists else None,
            'token_mtime': datetime.fromtimestamp(token_mtime).isoformat() if token_mtime else None,
            'token_age': token_age
        }

    return render_template('sem_config.html', connected=connected)


@sem_bp.route('/ads/connect')
@login_required
def ads_connect():
    # Initiate OAuth flow for an ads provider (e.g., google_ads)
    provider = request.args.get('provider', 'google_ads')
    u = current_user()
    if not user_has_permission(u, 'manage_sea') and getattr(u, 'role', None) != 'admin':
        return "Forbidden", 403

    # determine storage path (per-tenant if available)
    import os
    tenant = os.environ.get('TENANT')
    if tenant:
        token_dir = os.path.join('storage', 'tenants', tenant, 'ads')
    else:
        token_dir = os.path.join('storage', 'ads')
    os.makedirs(token_dir, exist_ok=True)
    token_path = os.path.join(token_dir, f'{provider}_token.json')

    # create connector instance with storage path
    try:
        from connectors import get_ads_connector
        conn = get_ads_connector(provider, config=None)
        # if connector accepts storage_path via constructor, re-instantiate
        try:
            conn = conn.__class__(config=getattr(conn, 'config', None), storage_path=token_path)
        except TypeError:
            # connector does not support storage_path param; fallback
            pass
        # not all connectors implement get_auth_url
        if not hasattr(conn, 'get_auth_url'):
            return f'Provider {provider} does not support OAuth connect via this UI', 400
        auth_url = conn.get_auth_url(state=provider)
        flash(f'Redirecting to {provider} for connection...')
        return redirect(auth_url)
    except Exception as e:
        return f'Error initiating connect: {e}', 500


@sem_bp.route('/ads/callback')
def ads_callback():
    # OAuth callback endpoint for ads connectors
    code = request.args.get('code')
    state = request.args.get('state')
    provider = request.args.get('provider') or state or 'google_ads'
    if not code:
        return 'Missing code', 400

    import os
    tenant = os.environ.get('TENANT')
    if tenant:
        token_dir = os.path.join('storage', 'tenants', tenant, 'ads')
    else:
        token_dir = os.path.join('storage', 'ads')
    os.makedirs(token_dir, exist_ok=True)
    token_path = os.path.join(token_dir, f'{provider}_token.json')

    try:
        from connectors import get_ads_connector
        conn = get_ads_connector(provider, config=None)
        # re-create connector with storage path if supported
        try:
            conn = conn.__class__(config=getattr(conn, 'config', None), storage_path=token_path)
        except TypeError:
            pass
        token = conn.fetch_token(code)
        # redirect to sem config with status
        flash(f'Connected to {provider}')
        return redirect(url_for('sem.config') + f'?connected={provider}')
    except Exception as e:
        flash(f'Error during token exchange: {e}')
        return redirect(url_for('sem.config'))


@sem_bp.route('/ads/disconnect', methods=['POST'])
@login_required
def ads_disconnect():
    provider = request.form.get('provider')
    if not provider:
        return redirect(url_for('sem.config'))
    u = current_user()
    if not user_has_permission(u, 'manage_sea') and getattr(u, 'role', None) != 'admin':
        return "Forbidden", 403

    import os
    tenant = os.environ.get('TENANT')
    if tenant:
        token_dir = os.path.join('storage', 'tenants', tenant, 'ads')
    else:
        token_dir = os.path.join('storage', 'ads')
    token_path = os.path.join(token_dir, f'{provider}_token.json')
    try:
        if os.path.exists(token_path):
            os.remove(token_path)
        flash(f'Disconnected {provider}')
        return redirect(url_for('sem.config'))
    except Exception as e:
        flash(f'Error disconnecting: {e}')
        return redirect(url_for('sem.config'))


@sem_bp.route('/ads/status/<provider>')
@login_required
def ads_status(provider):
    import os, json
    tenant = os.environ.get('TENANT')
    if tenant:
        token_dir = os.path.join('storage', 'tenants', tenant, 'ads')
    else:
        token_dir = os.path.join('storage', 'ads')
    token_path = os.path.join(token_dir, f'{provider}_token.json')
    if not os.path.exists(token_path):
        flash(f'No token found for {provider}')
        return redirect(url_for('sem.config'))
    try:
        with open(token_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        flash(f'Failed to read token file: {e}')
        return redirect(url_for('sem.config'))

    # mask sensitive fields for display
    def mask(s):
        if not s: return s
        s = str(s)
        if len(s) <= 8:
            return '****'
        return s[:4] + '...' + s[-4:]

    masked = {k: (mask(v) if k.lower() in ('access_token', 'refresh_token', 'id_token', 'client_secret') else v) for k, v in data.items()}
    return render_template('sem_ads_status.html', provider=provider, token=masked)


@sem_bp.route('/ads/refresh', methods=['POST'])
@login_required
def ads_refresh():
    provider = request.form.get('provider')
    if not provider:
        return redirect(url_for('sem.config'))
    u = current_user()
    if not user_has_permission(u, 'manage_sea') and getattr(u, 'role', None) != 'admin':
        return "Forbidden", 403

    import os
    tenant = os.environ.get('TENANT')
    if tenant:
        token_dir = os.path.join('storage', 'tenants', tenant, 'ads')
    else:
        token_dir = os.path.join('storage', 'ads')
    token_path = os.path.join(token_dir, f'{provider}_token.json')

    try:
        from connectors import get_ads_connector
        conn = get_ads_connector(provider, config=None)
        try:
            conn = conn.__class__(config=getattr(conn, 'config', None), storage_path=token_path)
        except TypeError:
            pass
        # attempt refresh
        new_token = conn.refresh_token()
        flash(f'Refreshed token for {provider}')
        return redirect(url_for('sem.ads_status', provider=provider))
    except Exception as e:
        flash(f'Error refreshing token: {e}')
        return redirect(url_for('sem.config'))


def seed_sem_permissions():
    try:
        from users import Permission
        defaults = [
            ('manage_sem', 'Manage SEM configuration'),
            ('run_automation', 'Allow running automated SEO tasks'),
            ('manage_sea', 'Manage paid ad campaigns via connectors')
        ]
        for name, desc in defaults:
            if not Permission.query.filter_by(name=name).first():
                p = Permission(name=name, description=desc)
                db.session.add(p)
        db.session.commit()
    except Exception:
        pass
