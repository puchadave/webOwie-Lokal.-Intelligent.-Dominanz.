from flask import Blueprint, render_template, request, jsonify
import os, json, datetime

email_marketing_bp = Blueprint('email_marketing', __name__, template_folder='templates')

EMAIL_CAMPAIGNS_DIR = os.environ.get('EMAIL_CAMPAIGNS_DIR', 'instance/email_campaigns')
os.makedirs(EMAIL_CAMPAIGNS_DIR, exist_ok=True)

# --- KI-Integration und OSINT/SOCMINT/HUMINT ---
def analyze_and_generate_email(recipient, campaign, engine='gemini'):
    # Simuliere OSINT/SOCMINT/HUMINT-Analyse
    osint_data = f"Analyse für {recipient}: Interessen, Verhalten, aktuelle Themen, Social Media, News."
    prompt = f"Erstelle eine individuelle Marketing-E-Mail für {recipient} zur Kampagne '{campaign}' basierend auf diesen Daten: {osint_data}"
    try:
        if engine == 'openai':
            from utils.openai_client import OpenAIClient
            client = OpenAIClient()
            return client.generate(prompt, max_tokens=512)
        elif engine == 'ollama':
            from utils.ollama_client import OllamaClient
            client = OllamaClient()
            return client.generate(prompt, max_tokens=512)
        else:
            from utils.gemini_client import GeminiClient
            client = GeminiClient()
            return client.generate(prompt, max_tokens=512)
    except Exception as e:
        return f'[KI-Fehler: {e}]'

def send_email(recipient, subject, body):
    # Simulierter Versand (hier kann SMTP/ESP angebunden werden)
    print(f"Sende E-Mail an {recipient}: {subject}\n{body}")
    return True

@email_marketing_bp.route('/')
def email_marketing_index():
    campaigns = []
    for fname in os.listdir(EMAIL_CAMPAIGNS_DIR):
        if fname.endswith('.json'):
            with open(os.path.join(EMAIL_CAMPAIGNS_DIR, fname), 'r', encoding='utf-8') as f:
                campaigns.append(json.load(f))
    campaigns.sort(key=lambda c: c.get('sent_at', ''), reverse=True)
    return render_template('email_marketing_index.html', campaigns=campaigns)

@email_marketing_bp.route('/generate', methods=['POST'])
def email_marketing_generate():
    data = request.get_json() or {}
    recipient = data.get('recipient', 'kunde@example.com')
    campaign = data.get('campaign', 'Neue Produktkampagne')
    engine = os.environ.get('AI_ENGINE', 'gemini')
    email_text = analyze_and_generate_email(recipient, campaign, engine)
    subject = f"{campaign} für {recipient}"
    sent = send_email(recipient, subject, email_text)
    campaign_data = {
        'recipient': recipient,
        'campaign': campaign,
        'subject': subject,
        'body': email_text,
        'sent_at': str(datetime.datetime.now()),
        'osint_data': f"Analyse für {recipient}"
    }
    fname = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M')}_{recipient.replace('@','_')}.json"
    with open(os.path.join(EMAIL_CAMPAIGNS_DIR, fname), 'w', encoding='utf-8') as f:
        json.dump(campaign_data, f, ensure_ascii=False, indent=2)
    return jsonify({'success': sent, 'campaign': campaign_data})
