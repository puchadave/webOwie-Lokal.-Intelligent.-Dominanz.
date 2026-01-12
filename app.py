# Cybersecurity Dashboard
@app.route('/dashboard/cyber')
def cyber_dashboard():
    return render_template('cyber_dashboard.html')

@app.route('/api/cyber_dashboard_metrics')
def cyber_dashboard_metrics():
    # Simulate live cybersecurity metrics (replace with real data sources as needed)
    import random
    threats = random.randint(0, 10)
    incidents = random.randint(0, 5)
    patches = random.randint(10, 50)
    vulns = random.randint(0, 8)
    data = {
        'threats': threats,
        'incidents': incidents,
        'patches': patches,
        'vulnerabilities': vulns,
        'chart_labels': ['Threats', 'Incidents', 'Patches', 'Vulnerabilities'],
        'chart_values': [threats, incidents, patches, vulns]
    }
    return jsonify(data)
# --- Specialized Dashboards ---
from flask import render_template

# Social Media Manager Dashboard
@app.route('/dashboard/social')
def social_dashboard():
    return render_template('social_dashboard.html')

@app.route('/api/social_dashboard_metrics')
def social_dashboard_metrics():
    # Example: Query post count from social_posts directory (legacy) and simulate followers/engagement
    import os, json
    SOCIAL_POSTS_DIR = os.environ.get('SOCIAL_POSTS_DIR', 'instance/social_posts')
    post_count = 0
    engagement_sum = 0
    engagement_count = 0
    for fname in os.listdir(SOCIAL_POSTS_DIR):
        if fname.endswith('.json'):
            post_count += 1
            with open(os.path.join(SOCIAL_POSTS_DIR, fname), 'r', encoding='utf-8') as f:
                post = json.load(f)
                engagement = post.get('engagement', 0)
                engagement_sum += engagement
                engagement_count += 1
    avg_engagement = (engagement_sum / engagement_count) if engagement_count else 0
    # Simulate follower count (replace with real API/db query if available)
    follower_count = 3500 + post_count * 2
    data = {
        'posts': post_count,
        'followers': follower_count,
        'engagement': round(avg_engagement, 3),
        'chart_labels': ['Posts', 'Followers', 'Engagement'],
        'chart_values': [post_count, follower_count, avg_engagement]
    }
    return jsonify(data)

# SEO/SEA Dashboard
@app.route('/dashboard/sem')
def sem_dashboard():
    return render_template('sem_dashboard.html')

@app.route('/api/sem_dashboard_metrics')
def sem_dashboard_metrics():
    # Example: Query SEOTask for completed actions as conversions, simulate impressions/clicks
    from models import db
    try:
        from sem import SEOTask
        conversions = SEOTask.query.filter_by(status='completed').count()
    except Exception:
        conversions = 0
    impressions = 50000 + conversions * 10
    clicks = 3200 + conversions * 2
    ctr = (clicks / impressions * 100) if impressions else 0
    data = {
        'impressions': impressions,
        'clicks': clicks,
        'ctr': round(ctr, 2),
        'conversions': conversions,
        'chart_labels': ['Impressions', 'Clicks', 'Conversions'],
        'chart_values': [impressions, clicks, conversions]
    }
    return jsonify(data)

# OSINT Market Analysis Dashboard
@app.route('/dashboard/osint')
def osint_dashboard():
    return render_template('osint_dashboard.html')

@app.route('/api/osint_dashboard_metrics')
def osint_dashboard_metrics():
    # Example: Aggregate trending topics and mentions from CRM and social posts
    import os, json
    SOCIAL_POSTS_DIR = os.environ.get('SOCIAL_POSTS_DIR', 'instance/social_posts')
    topics = {}
    mentions = 0
    sentiment_score = 0
    sentiment_count = 0
    for fname in os.listdir(SOCIAL_POSTS_DIR):
        if fname.endswith('.json'):
            with open(os.path.join(SOCIAL_POSTS_DIR, fname), 'r', encoding='utf-8') as f:
                post = json.load(f)
                topic = post.get('topic', 'General')
                topics[topic] = topics.get(topic, 0) + 1
                mentions += 1
                sentiment = post.get('sentiment', 1)
                sentiment_score += sentiment
                sentiment_count += 1
    trending = ', '.join(sorted(topics, key=topics.get, reverse=True)[:3])
    avg_sentiment = sentiment_score / sentiment_count if sentiment_count else 1
    sentiment_label = 'Positive' if avg_sentiment > 0.5 else 'Negative'
    data = {
        'trending': trending or 'N/A',
        'mentions': mentions,
        'sentiment': sentiment_label,
        'chart_labels': list(topics.keys()),
        'chart_values': list(topics.values())
    }
    return jsonify(data)

# System Architect Dashboard
@app.route('/dashboard/arch')
def arch_dashboard():
    return render_template('arch_dashboard.html')

@app.route('/api/arch_dashboard_metrics')
def arch_dashboard_metrics():
    # Example: Query user count, simulate API calls, errors, uptime
    from models import User
    try:
        active_users = User.query.count()
    except Exception:
        active_users = 0
    # Simulate API calls and errors (replace with real monitoring if available)
    api_calls = 12000 + active_users * 10
    errors = 2
    uptime = '99.99%'
    data = {
        'active_users': active_users,
        'api_calls': api_calls,
        'errors': errors,
        'uptime': uptime,
        'chart_labels': ['Active Users', 'API Calls', 'Errors'],
        'chart_values': [active_users, api_calls, errors]
    }
    return jsonify(data)
# --- Dashboard Route & API ---
from models import Tenant, User, Invoice, Lead

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/dashboard_metrics')
def dashboard_metrics():
    tenants = Tenant.query.count()
    users = User.query.count()
    invoices = Invoice.query.count()
    leads = Lead.query.count()
    # Example chart: KPIs by type
    chart_labels = ['Tenants', 'Users', 'Invoices', 'Leads']
    chart_values = [tenants, users, invoices, leads]
    return jsonify({
        'tenants': tenants,
        'users': users,
        'invoices': invoices,
        'leads': leads,
        'chart_labels': chart_labels,
        'chart_values': chart_values
    })
# E-Mail-Marketing-Modul registrieren
try:
    from email_marketing import email_marketing_bp
except Exception:
    email_marketing_bp = None

# CRM-Modul registrieren
try:
    from crm import crm_bp
except Exception:
    crm_bp = None

# Social Media Management Modul registrieren
try:
    from social import social_bp
except Exception:
    social_bp = None

# Business-Website-Modul registrieren
try:
    from business_site import business_site_bp
except Exception:
    business_site_bp = None

# --- KI-Chat-API für das Chat-Widget ---
from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db

@app.route('/api/ai_chat', methods=['POST'])
def api_ai_chat():
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    if not message:
        return jsonify({'reply': 'Bitte gib eine Nachricht ein.'}), 400
    ai_engine = os.environ.get('AI_ENGINE', 'gemini').lower()

    # Datenzugriff: Rechnungen, Nutzer, Leads, Dokumente
    try:
        from accounting import Invoice
        invoices = Invoice.query.order_by(Invoice.created_at.desc()).limit(10).all()
        invoice_data = [
            {
                'id': inv.id,
                'seller': inv.seller,
                'buyer': inv.buyer,
                'issue_date': str(inv.issue_date),
                'due_date': str(inv.due_date),
                'currency': inv.currency,
                'status': inv.status,
                'total': inv.total
            } for inv in invoices
        ]
    except Exception:
        invoice_data = []
    try:
        import users
        user_list = getattr(users, 'User', None)
        if user_list:
            users_data = [u.to_dict() for u in user_list.query.limit(10).all()]
        else:
            users_data = []
    except Exception:
        users_data = []
    try:
        from main import load_leads
        leads_data = load_leads()
    except Exception:
        leads_data = {}
    try:
        import os
        doc_dir = os.environ.get('DOCUMENT_STORAGE', 'storage/documents')
        docs = os.listdir(doc_dir) if os.path.exists(doc_dir) else []
    except Exception:
        docs = []

    # Kontext für die KI
    context = (
        f"Letzte Rechnungen: {invoice_data}\n"
        f"Nutzer: {users_data}\n"
        f"Leads: {list(leads_data.keys())}\n"
        f"Dokumente: {docs}\n"
    )
    prompt = f"Systemkontext:\n{context}\n\nUser: {message}"

    try:
        if ai_engine == 'openai':
            from utils.openai_client import OpenAIClient
            client = OpenAIClient()
            reply = client.generate(prompt)
        elif ai_engine == 'ollama':
            from utils.ollama_client import OllamaClient
            client = OllamaClient()
            reply = client.generate(prompt)
        else:
            from utils.gemini_client import GeminiClient
            client = GeminiClient()
            reply = client.generate(prompt)
    except Exception as e:
        reply = f'[KI-Fehler: {e}]'
    return jsonify({'reply': reply})
from flask import Flask, render_template, session
import os

# Create app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost:5432/osint_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
app.secret_key = os.environ.get('FLASK_SECRET') or os.urandom(24)

# --- Multi-tenant support ---
tenant = os.environ.get('TENANT')
if tenant:
    tenant_dir = os.path.join('storage', 'tenants', tenant)
    os.makedirs(tenant_dir, exist_ok=True)
    db_file = os.path.abspath(os.path.join(tenant_dir, 'app.db'))
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_file}"
    app.config['DOCUMENT_STORAGE'] = os.path.join(tenant_dir, 'documents')
    app.config['EINVOICE_PATH'] = os.path.join(tenant_dir, 'einvoices')
    os.makedirs(app.config['DOCUMENT_STORAGE'], exist_ok=True)
    os.makedirs(app.config['EINVOICE_PATH'], exist_ok=True)
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    app.config['DOCUMENT_STORAGE'] = os.environ.get('DOCUMENT_STORAGE', 'storage/documents')
    app.config['EINVOICE_PATH'] = os.environ.get('EINVOICE_PATH', 'storage/einvoices')

app.config['OPEN_REGISTRATION'] = os.environ.get('OPEN_REGISTRATION', 'false').lower() in ('1', 'true', 'yes')
app.config['PAYMENT_PROVIDER'] = os.environ.get('PAYMENT_PROVIDER', 'paypal')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import and register blueprints if present
try:
    from accounting import accounting_bp, db as db
except Exception:
    accounting_bp = None
    db = None

try:
    from dms import dms_bp
except Exception:
    dms_bp = None

try:
    from users import auth_bp
except Exception:
    auth_bp = None

try:
    from ecommerce import ecom as ecommerce_bp
except Exception:
    ecommerce_bp = None

try:
    from blog import blog_bp
except Exception:
    blog_bp = None

try:
    from sem import sem_bp
except Exception:
    sem_bp = None

# Initialize DB and register blueprints
if db:
    db.init_app(app)
    with app.app_context():
        db.create_all()
    if accounting_bp and 'accounting' not in app.blueprints:
        app.register_blueprint(accounting_bp, url_prefix='/accounting')
    if dms_bp and 'dms' not in app.blueprints:
        app.register_blueprint(dms_bp, url_prefix='/documents')
    if auth_bp and 'auth' not in app.blueprints:
        app.register_blueprint(auth_bp, url_prefix='/auth')
    if ecommerce_bp and 'ecommerce' not in app.blueprints:
        app.register_blueprint(ecommerce_bp, url_prefix='/ecommerce')
    if blog_bp and 'blog' not in app.blueprints:
        app.register_blueprint(blog_bp, url_prefix='/blog')
    if sem_bp and 'sem' not in app.blueprints:
        app.register_blueprint(sem_bp, url_prefix='/sem')
    if business_site_bp and 'business_site' not in app.blueprints:
        app.register_blueprint(business_site_bp, url_prefix='/business_site')
    if social_bp and 'social' not in app.blueprints:
        app.register_blueprint(social_bp, url_prefix='/social')
    if crm_bp and 'crm' not in app.blueprints:
        app.register_blueprint(crm_bp, url_prefix='/crm')
    if email_marketing_bp and 'email_marketing' not in app.blueprints:
        app.register_blueprint(email_marketing_bp, url_prefix='/email_marketing')


@app.route('/')
def index():
    # basic index to navigate to major features
    return render_template('index.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
from flask import Flask, render_template, session
import os

# Create app
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET') or os.urandom(24)

# --- Multi-tenant support ---
tenant = os.environ.get('TENANT')
if tenant:
    tenant_dir = os.path.join('storage', 'tenants', tenant)
    os.makedirs(tenant_dir, exist_ok=True)
    db_file = os.path.abspath(os.path.join(tenant_dir, 'app.db'))
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_file}"
    app.config['DOCUMENT_STORAGE'] = os.path.join(tenant_dir, 'documents')
    app.config['EINVOICE_PATH'] = os.path.join(tenant_dir, 'einvoices')
    os.makedirs(app.config['DOCUMENT_STORAGE'], exist_ok=True)
    os.makedirs(app.config['EINVOICE_PATH'], exist_ok=True)
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    app.config['DOCUMENT_STORAGE'] = os.environ.get('DOCUMENT_STORAGE', 'storage/documents')
    app.config['EINVOICE_PATH'] = os.environ.get('EINVOICE_PATH', 'storage/einvoices')

app.config['OPEN_REGISTRATION'] = os.environ.get('OPEN_REGISTRATION', 'false').lower() in ('1', 'true', 'yes')
app.config['PAYMENT_PROVIDER'] = os.environ.get('PAYMENT_PROVIDER', 'paypal')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import and register blueprints if present
try:
    from accounting import accounting_bp, db as db
except Exception:
    accounting_bp = None
    db = None

try:
    from dms import dms_bp
except Exception:
    dms_bp = None

try:
    from users import auth_bp
except Exception:
    auth_bp = None

try:
    from ecommerce import ecom as ecommerce_bp
except Exception:
    ecommerce_bp = None

try:
    from blog import blog_bp
except Exception:
    blog_bp = None

try:
    from sem import sem_bp
except Exception:
    sem_bp = None

# Initialize DB and register blueprints
if db:
    db.init_app(app)
    with app.app_context():
        db.create_all()
    if accounting_bp and 'accounting' not in app.blueprints:
        app.register_blueprint(accounting_bp, url_prefix='/accounting')
    if dms_bp and 'dms' not in app.blueprints:
        app.register_blueprint(dms_bp, url_prefix='/documents')
    if auth_bp and 'auth' not in app.blueprints:
        app.register_blueprint(auth_bp, url_prefix='/auth')
    if ecommerce_bp and 'ecommerce' not in app.blueprints:
        app.register_blueprint(ecommerce_bp, url_prefix='/ecommerce')
    if blog_bp and 'blog' not in app.blueprints:
        app.register_blueprint(blog_bp, url_prefix='/blog')
    if sem_bp and 'sem' not in app.blueprints:
        app.register_blueprint(sem_bp, url_prefix='/sem')


@app.route('/')
def index():
    # basic index to navigate to major features
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import json
from functools import wraps
import imaplib
import smtplib
from email.mime.text import MIMEText
from email.header import decode_header
import email



@app.route('/compose_email')
@login_required

def compose_email():
    leads_data = load_leads()
    company_names = sorted(list(leads_data.keys()))
    return render_template('compose_email.html', company_names=company_names)

@app.route('/send_new_email', methods=['POST'])
@login_required

def send_new_email():
    config = session['email_config']
    to_email = request.form['to_email']
    subject = request.form['subject']
    body = request.form['body']

    if send_email_smtp(config, to_email, subject, body):
        return redirect(url_for('index')) # Redirect to inbox after sending
    else:
        # TODO: Handle error case more gracefully
        return "Failed to send email", 500


@app.route('/generate_ai_email', methods=['POST'])
@login_required

def generate_ai_email():
    data = request.get_json() or {}
    company_name = data.get('company_name')
    prompt = data.get('prompt')

    if not company_name or not prompt:
        return jsonify({"error": "Company name and prompt are required"}), 400

    # permission check: only users with 'use_ai' may call this
    try:
        from users import current_user, user_has_permission
        u = current_user()
        if not user_has_permission(u, 'use_ai'):
            return jsonify({'error': 'Forbidden: missing permission use_ai'}), 403
    except Exception:
        return jsonify({'error': 'Permission system unavailable'}), 500

    leads = load_leads()
    lead_data = leads.get(company_name)

    if not lead_data:
        return jsonify({"error": f"Lead for {company_name} not found"}), 404

    generated_content = generate_email_content(lead_data, prompt)
    return jsonify(generated_content)


@app.route('/leads_dashboard')
@login_required

def leads_dashboard():
    leads = load_leads()
    return render_template('leads.html', leads=leads)



if __name__ == '__main__':
    app.run(debug=True)
    generated_content = generate_email_content(lead_data, prompt)



    return jsonify(generated_content)







@app.route('/leads_dashboard')



@login_required



def leads_dashboard():



    leads = load_leads()



    return render_template('leads.html', leads=leads)











if __name__ == '__main__':



    app.run(debug=True)






