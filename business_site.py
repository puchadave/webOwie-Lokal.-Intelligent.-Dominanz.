from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import os

business_site_bp = Blueprint('business_site', __name__, template_folder='templates')

# Speicherort für generierte Seiten
BUSINESS_SITE_DIR = os.environ.get('BUSINESS_SITE_DIR', 'instance/business_site')
os.makedirs(BUSINESS_SITE_DIR, exist_ok=True)

# --- KI-Integration ---
def generate_website_content(prompt, engine='gemini'):
    try:
        if engine == 'openai':
            from utils.openai_client import OpenAIClient
            client = OpenAIClient()
            return client.generate(prompt, max_tokens=2048)
        elif engine == 'ollama':
            from utils.ollama_client import OllamaClient
            client = OllamaClient()
            return client.generate(prompt, max_tokens=2048)
        else:
            from utils.gemini_client import GeminiClient
            client = GeminiClient()
            return client.generate(prompt, max_tokens=2048)
    except Exception as e:
        return f'[KI-Fehler: {e}]'

@business_site_bp.route('/')
def business_site_index():
    # Zeige die Startseite der Business-Website
    index_path = os.path.join(BUSINESS_SITE_DIR, 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            html = f.read()
        return html
    return render_template('business_site_setup.html')

@business_site_bp.route('/cms', methods=['GET', 'POST'])
def business_site_cms():
    # Einfaches CMS-Formular für Seitenbearbeitung
    if request.method == 'POST':
        page = request.form.get('page', 'index')
        content = request.form.get('content', '')
        with open(os.path.join(BUSINESS_SITE_DIR, f'{page}.html'), 'w', encoding='utf-8') as f:
            f.write(content)
        flash('Seite gespeichert!', 'success')
        return redirect(url_for('business_site.business_site_cms'))
    # Seiten auflisten
    pages = [f for f in os.listdir(BUSINESS_SITE_DIR) if f.endswith('.html')]
    page_content = ''
    page = request.args.get('page', 'index')
    page_path = os.path.join(BUSINESS_SITE_DIR, f'{page}.html')
    if os.path.exists(page_path):
        with open(page_path, 'r', encoding='utf-8') as f:
            page_content = f.read()
    return render_template('business_site_cms.html', pages=pages, page=page, content=page_content)

@business_site_bp.route('/generate', methods=['POST'])
def business_site_generate():
    # KI-generierte Website auf Knopfdruck
    data = request.get_json() or {}
    prompt = data.get('prompt', 'Erstelle eine moderne Business-Website für ein Unternehmen.')
    engine = os.environ.get('AI_ENGINE', 'gemini')
    html = generate_website_content(prompt, engine)
    with open(os.path.join(BUSINESS_SITE_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    return jsonify({'success': True, 'html': html})
