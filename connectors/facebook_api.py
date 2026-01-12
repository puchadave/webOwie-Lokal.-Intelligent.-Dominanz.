import os, json, requests
from urllib.parse import urlencode
from utils.crypto import encrypt_bytes, decrypt_bytes

class FacebookAPIConnector:
    DEFAULT_SCOPE = 'email,pages_manage_posts,pages_read_engagement'

    def __init__(self, config=None, storage_path=None):
        self.config = config or {}
        self.client_id = self.config.get('client_id') or os.environ.get('FACEBOOK_CLIENT_ID')
        self.client_secret = self.config.get('client_secret') or os.environ.get('FACEBOOK_CLIENT_SECRET')
        self.auth_url = self.config.get('auth_url') or os.environ.get('FACEBOOK_AUTH_URL')
        self.token_url = self.config.get('token_url') or os.environ.get('FACEBOOK_TOKEN_URL')
        self.redirect_uri = self.config.get('redirect_uri') or os.environ.get('FACEBOOK_REDIRECT_URI')
        self.scope = self.config.get('scope') or os.environ.get('FACEBOOK_SCOPE') or self.DEFAULT_SCOPE
        self.storage_path = storage_path or os.environ.get('FACEBOOK_TOKEN_PATH') or os.path.join('storage','facebook_token.json')

    def _save_token(self, token_data):
        os.makedirs(os.path.dirname(self.storage_path) or '.', exist_ok=True)
        data = json.dumps(token_data).encode('utf-8')
        try:
            data = encrypt_bytes(data)
        except Exception:
            pass
        with open(self.storage_path, 'wb') as f:
            f.write(data)

    def _load_token(self):
        if not os.path.exists(self.storage_path):
            return None
        try:
            with open(self.storage_path, 'rb') as f:
                data = f.read()
            try:
                data = decrypt_bytes(data)
            except Exception:
                pass
            return json.loads(data.decode('utf-8'))
        except Exception:
            return None

    def get_auth_url(self, state=None):
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
            'response_type': 'code'
        }
        if state:
            params['state'] = state
        return f"{self.auth_url}?{urlencode(params)}"

    def fetch_token(self, code):
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'code': code
        }
        r = requests.get(self.token_url, params=data, timeout=10)
        r.raise_for_status()
        token = r.json()
        self._save_token(token)
        return token

    def refresh_token(self, refresh_token=None):
        # Facebook exchanges long-lived tokens differently; stubbed here
        raise NotImplementedError('Refresh not implemented in generic stub')

    def api_get(self, path, params=None):
        token = self._load_token()
        if not token:
            raise RuntimeError('Not authenticated')
        access = token.get('access_token')
        url = path if path.startswith('http') else f"https://graph.facebook.com/{path.lstrip('/') }"
        r = requests.get(url, params={**(params or {}), 'access_token': access}, timeout=10)
        r.raise_for_status()
        return r.json()
