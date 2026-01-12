
from flask import Blueprint, render_template, request, jsonify
import os, datetime, json

social_bp = Blueprint('social', __name__, template_folder='templates')

# Speicherort für geplante und generierte Posts
SOCIAL_POSTS_DIR = os.environ.get('SOCIAL_POSTS_DIR', 'instance/social_posts')
os.makedirs(SOCIAL_POSTS_DIR, exist_ok=True)

# --- KI-Integration und OSINT/SOCMINT/HUMINT ---
def analyze_and_generate_post(topic, engine='gemini'):
    # Simuliere OSINT/SOCMINT/HUMINT-Analyse
    osint_data = f"Echtzeit-Analyse für {topic}: Trends, Zielgruppe, Stimmungen, relevante Ereignisse."
    prompt = f"Erstelle einen Social-Media-Post für {topic} basierend auf diesen Daten: {osint_data}"
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

def optimal_post_time(osint_data):
    # Simuliere KI-basierte Zeitoptimierung
    now = datetime.datetime.now()
    # Beispiel: poste zur nächsten vollen Stunde
    return (now + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

@social_bp.route('/')
def social_index():
    # Zeige geplante und vergangene Posts
    posts = []
    for fname in os.listdir(SOCIAL_POSTS_DIR):
        if fname.endswith('.json'):
            with open(os.path.join(SOCIAL_POSTS_DIR, fname), 'r', encoding='utf-8') as f:
                posts.append(json.load(f))
    posts.sort(key=lambda p: p.get('scheduled', ''), reverse=True)
    return render_template('social_index.html', posts=posts)

@social_bp.route('/generate', methods=['POST'])
def social_generate():
    data = request.get_json() or {}
    topic = data.get('topic', 'Allgemeines Thema')
    engine = os.environ.get('AI_ENGINE', 'gemini')
    post_text = analyze_and_generate_post(topic, engine)
    osint_data = f"Echtzeit-Analyse für {topic}"
    scheduled = optimal_post_time(osint_data)
    post = {
        'topic': topic,
        'text': post_text,
        'osint_data': osint_data,
        'scheduled': str(scheduled)
    }
    fname = f"{scheduled.strftime('%Y%m%d_%H%M')}_{topic.replace(' ','_')}.json"
    with open(os.path.join(SOCIAL_POSTS_DIR, fname), 'w', encoding='utf-8') as f:
        import json; json.dump(post, f, ensure_ascii=False, indent=2)
    return jsonify({'success': True, 'post': post})
