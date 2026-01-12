# OAuth setup for SEM / Ads connectors

This document explains how to register OAuth clients for Google Ads, Meta (Facebook/Instagram), and LinkedIn, how to configure the example env, and how to run a local end-to-end test.

## 1) Register an OAuth client

Google Ads (recommended testing):

- Open Google Cloud Console > APIs & Services > Credentials.
- Create an OAuth 2.0 Client ID (Application type: Web application).
- Add an authorized redirect URI:
  - For local testing: `http://localhost:5000/sem/ads/callback`
  - For deployed instances: `https://your-domain/sem/ads/callback`
- Note the `Client ID` and `Client secret`.

Facebook / Meta:

- Use Meta for Developers > My Apps > Add App.
- Configure OAuth redirect URIs similar to above and obtain App ID/Secret.

LinkedIn:

- Create an app at LinkedIn Developer Portal, set OAuth 2.0 redirect URL, and obtain client id/secret.

## 2) Configure `.env` (or per-tenant .env files)

Copy `config.example.env` to `.env` or use per-tenant `.env.<tenant>` files if you run in multi-tenant mode.
Fill the provider variables, e.g:

```env
GOOGLE_ADS_CLIENT_ID=xxx
GOOGLE_ADS_CLIENT_SECRET=yyy
GOOGLE_ADS_REDIRECT_URI=http://localhost:5000/sem/ads/callback
```

For per-tenant testing create `.env.<tenant>` containing the same keys. The app uses the `TENANT` env var to select tenant storage at `storage/tenants/<tenant>/`.

## 3) Local run and test flow

1. Install dependencies and start the Flask app (adjust if you use a virtualenv):

```bash
pip install -r requirements.txt
export FLASK_APP=app.py
export FLASK_ENV=development
# Optionally set TENANT=testclient
export TENANT=testclient
flask run
```

1. In your browser open `http://localhost:5000/sem/config` and click "Connect" for Google Ads.
2. Authenticate with Google and accept requested scopes.
3. On success the app will store the token at `storage/tenants/<tenant>/ads/google_ads_token.json` (or the global `ADS_TOKEN_DEFAULT_PATH` if you are single-tenant testing).

## 4) Verify connector actions

Once token is present you can exercise connector actions via the SEM UI or by calling the connector directly in a Python REPL, for example:

```python
from connectors.google_ads import GoogleAdsConnector
c = GoogleAdsConnector(token_path='storage/tenants/testclient/ads/google_ads_token.json')
print(c.perform_action('list_customers'))
```

## 7) Encrypting stored tokens (recommended)

The app supports optional symmetric encryption for token files using a Fernet key stored in the `ADS_ENCRYPTION_KEY` environment variable.

Generate a key locally with:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Then export it before running the app:

```bash
export ADS_ENCRYPTION_KEY=<the-key-from-above>
```

If the key is set, token files written to `storage/tenants/<tenant>/ads/` will be encrypted. If unset, files remain plaintext (useful for debugging but not for production).

## 5) Security notes

- Never commit client secrets to source control.
- Prefer a secrets manager in production.
- Tokens stored on disk should be encrypted or placed in restricted storage with careful access controls.

## 6) Troubleshooting

- If the provider rejects the redirect URI, confirm the redirect registered in the provider dashboard exactly matches the one in `.env` (including http/https and trailing slash).
- Check Flask logs for callback errors.
- Ensure `TENANT` matches the tenant folder where you expect tokens to be written.

---

If you want, I can now update the SEM config template to show token age and quick disconnect buttons. Proceed?
