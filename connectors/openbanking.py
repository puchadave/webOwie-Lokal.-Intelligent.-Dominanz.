import os
import json
import requests
from urllib.parse import urlencode
from utils.crypto import encrypt_bytes, decrypt_bytes


class OpenBankingConnector:
    """Generic OpenBanking OAuth2 connector scaffold.

    This is a generic implementation for OAuth2-based OpenBanking APIs.
    Configure the following env vars or pass via `config`:
      - OPENBANKING_CLIENT_ID
      - OPENBANKING_CLIENT_SECRET
      - OPENBANKING_AUTH_URL
      - OPENBANKING_TOKEN_URL
      - OPENBANKING_API_BASE (e.g. https://api.example-bank.com)
      - OPENBANKING_REDIRECT_URI
      - OPENBANKING_SCOPE

    Token storage is written to `storage/<provider>_token.json` or a provided storage_path.
    If `ADS_ENCRYPTION_KEY` (or a generic `ADS_ENCRYPTION_KEY`) is set, token files are encrypted.
    """

    DEFAULT_SCOPE = 'accounts payments'

    def __init__(self, config=None, storage_path=None):
        self.config = config or {}
        self.client_id = self.config.get('client_id') or os.environ.get('OPENBANKING_CLIENT_ID')
        self.client_secret = self.config.get('client_secret') or os.environ.get('OPENBANKING_CLIENT_SECRET')
        self.auth_url = self.config.get('auth_url') or os.environ.get('OPENBANKING_AUTH_URL')
        self.token_url = self.config.get('token_url') or os.environ.get('OPENBANKING_TOKEN_URL')
        self.api_base = self.config.get('api_base') or os.environ.get('OPENBANKING_API_BASE')
        self.redirect_uri = self.config.get('redirect_uri') or os.environ.get('OPENBANKING_REDIRECT_URI')
        self.scope = self.config.get('scope') or os.environ.get('OPENBANKING_SCOPE') or self.DEFAULT_SCOPE
        self.storage_path = storage_path or os.environ.get('OPENBANKING_TOKEN_PATH') or os.path.join('storage', 'openbanking_token.json')

    @staticmethod
    def configure_from_env():
        return {
            'client_id': os.environ.get('OPENBANKING_CLIENT_ID'),
            'client_secret': os.environ.get('OPENBANKING_CLIENT_SECRET'),
            'auth_url': os.environ.get('OPENBANKING_AUTH_URL'),
            'token_url': os.environ.get('OPENBANKING_TOKEN_URL'),
            'api_base': os.environ.get('OPENBANKING_API_BASE'),
            'redirect_uri': os.environ.get('OPENBANKING_REDIRECT_URI'),
            'scope': os.environ.get('OPENBANKING_SCOPE'),
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
                pass
            return json.loads(data.decode('utf-8'))
        except Exception:
            return None

    def get_auth_url(self, state=None):
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
        }
        if state:
            params['state'] = state
        return f"{self.auth_url}?{urlencode(params)}"

    def fetch_token(self, code):
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        r = requests.post(self.token_url, data=data, timeout=10)
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
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        r = requests.post(self.token_url, data=data, timeout=10)
        r.raise_for_status()
        new_token = r.json()
        if 'refresh_token' not in new_token:
            new_token['refresh_token'] = refresh_token
        self._save_token(new_token)
        return new_token

    def _get_auth_headers(self):
        token = self._load_token()
        if not token:
            raise RuntimeError('Not authenticated')
        access_token = token.get('access_token')
        return {'Authorization': f'Bearer {access_token}'}

    # Example convenience methods
    def get_accounts(self):
        url = f"{self.api_base.rstrip('/')}/accounts"
        r = requests.get(url, headers=self._get_auth_headers(), timeout=10)
        r.raise_for_status()
        return r.json()

    def create_payment(self, payment_payload):
        # POST to payments endpoint; payload shape depends on bank API (this is scaffold)
        url = f"{self.api_base.rstrip('/')}/payments"
        r = requests.post(url, headers=self._get_auth_headers(), json=payment_payload, timeout=10)
        r.raise_for_status()
        return r.json()
