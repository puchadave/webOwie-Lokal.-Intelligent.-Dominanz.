from flask import Blueprint, render_template, request, jsonify
import os
import datetime
import json

crm_bp = Blueprint('crm', __name__, template_folder='templates')

CRM_LEADS_FILE = os.environ.get('CRM_LEADS_FILE', 'instance/crm_leads.json')
os.makedirs(os.path.dirname(CRM_LEADS_FILE), exist_ok=True)

def osint_lead_analysis(company):
    # Simuliere OSINT-Analyse und Psychoprofil
    osint = f"OSINT für {company}: Markt, Web, Social, News, Verhalten."
    psycho = f"Psychoprofil: Innovationsfreudig, risikobereit, digital-affin."
    strategie = f"Strategie: Social Selling, Thought Leadership, gezielte Ansprache."
    return {
        'company_name': company,
        'osint_data': osint,
        'psychoprofile': psycho,
        'strategie': strategie,
        'created_at': str(datetime.datetime.now())
    }

def load_crm_leads():
    if os.path.exists(CRM_LEADS_FILE):
        with open(CRM_LEADS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_crm_leads(leads):
    with open(CRM_LEADS_FILE, 'w', encoding='utf-8') as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)

@crm_bp.route('/')
def crm_index():
    leads = load_crm_leads()
    return render_template('crm_index.html', leads=leads)

@crm_bp.route('/generate', methods=['POST'])
def crm_generate():
    data = request.get_json() or {}
    company = data.get('company', 'Beispiel GmbH')
    lead = osint_lead_analysis(company)
    leads = load_crm_leads()
    leads[company] = lead
    save_crm_leads(leads)
    return jsonify({'success': True, 'lead': lead})
