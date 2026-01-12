import os
import json
import requests
from urllib.parse import urlencode


class GoogleAdsConnector:
    TOKEN_URL = 'https://oauth2.googleapis.com/token'
    AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
    DEFAULT_SCOPE = 'https://www.googleapis.com/auth/adwords openid email profile'

    def __init__(self, config=None, storage_path=None):
        self.config = config or {}
        self.client_id = self.config.get('client_id') or os.environ.get('GOOGLE_ADS_CLIENT_ID')
        self.client_secret = self.config.get('client_secret') or os.environ.get('GOOGLE_ADS_CLIENT_SECRET')
        self.redirect_uri = self.config.get('redirect_uri') or os.environ.get('GOOGLE_ADS_REDIRECT_URI')
        # storage path for tokens (per-tenant recommended)
        self.storage_path = storage_path or os.environ.get('GOOGLE_ADS_TOKEN_PATH') or 'storage/google_ads_token.json'

    @staticmethod
    def configure_from_env():
        return {
            'client_id': os.environ.get('GOOGLE_ADS_CLIENT_ID'),
            'client_secret': os.environ.get('GOOGLE_ADS_CLIENT_SECRET'),
            'redirect_uri': os.environ.get('GOOGLE_ADS_REDIRECT_URI')
        }

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
                # if decryption fails, assume file is plaintext JSON
                pass
            return json.loads(data.decode('utf-8'))
        except Exception:
            return None

    def get_auth_url(self, state=None):
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': self.DEFAULT_SCOPE,
            'access_type': 'offline',
            'include_granted_scopes': 'true'
        }
        if state:
            params['state'] = state
        return f"{self.AUTH_URL}?{urlencode(params)}"

    def fetch_token(self, code):
        data = {
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }
        r = requests.post(self.TOKEN_URL, data=data, timeout=10)
        r.raise_for_status()
        token = r.json()
        self._save_token(token)
        return token

    def refresh_token(self, refresh_token=None):
        token = self._load_token() or {}
        refresh_token = refresh_token or token.get('refresh_token')
        if not refresh_token:
            raise RuntimeError('No refresh token available')
        data = {
            'refresh_token': refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token'
        }
        r = requests.post(self.TOKEN_URL, data=data, timeout=10)
        r.raise_for_status()
        new_token = r.json()
        # preserve refresh_token
        if 'refresh_token' not in new_token:
            new_token['refresh_token'] = refresh_token
        self._save_token(new_token)
        return new_token

    def _get_auth_headers(self):
        token = self._load_token()
        if not token:
            raise RuntimeError('Not authenticated; call get_auth_url and fetch_token first')
        access_token = token.get('access_token')
        return {'Authorization': f'Bearer {access_token}'}

    def perform_action(self, action, payload):
        """Demonstration actions.

        Supported actions (demo):
        - list_customers: calls Google Ads listAccessibleCustomers endpoint
        - raw_get: expects payload['url'] to GET (with auth)
        """
        headers = self._get_auth_headers()
        if action == 'list_customers':
            url = 'https://googleads.googleapis.com/v14/customers:listAccessibleCustomers'
            r = requests.get(url, headers=headers, timeout=10)
            r.raise_for_status()
            return r.json()
        if action == 'raw_get':
            url = payload.get('url')
            if not url:
                raise ValueError('payload.url required for raw_get')
            r = requests.get(url, headers=headers, timeout=10)
            r.raise_for_status()
            return r.text
        raise NotImplementedError('Action not implemented in demo connector')
