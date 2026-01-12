# OpenBanking connector

This project includes a generic `OpenBankingConnector` scaffold in `connectors/openbanking.py`.

Features:
- OAuth2 authorization code flow support (`get_auth_url`, `fetch_token`, `refresh_token`).
- Token storage with optional Fernet encryption (use `ADS_ENCRYPTION_KEY` environment variable).
- Convenience methods: `get_accounts()` and `create_payment()` which map to typical OpenBanking endpoints. These are scaffolds — adapt payloads to your bank's API.

Configuration (environment variables in `config.example.env`):
- `OPENBANKING_CLIENT_ID`
- `OPENBANKING_CLIENT_SECRET`
- `OPENBANKING_AUTH_URL` (provider auth endpoint)
- `OPENBANKING_TOKEN_URL` (provider token endpoint)
- `OPENBANKING_API_BASE` (base URL for accounts/payments endpoints)
- `OPENBANKING_REDIRECT_URI` (must match registered redirect URI)
- `OPENBANKING_SCOPE`

Usage:
- Select the connector by setting `PAYMENT_PROVIDER=openbanking` in your `.env` or `config.example.env`.
- The app will instantiate `OpenBankingConnector.configure_from_env()` when needed.
- To initiate user authorization, your app should provide a route that calls `get_auth_url()` and redirects the user to the bank's consent page; upon return the bank will call your callback where you exchange the `code` for a token via `fetch_token(code)`.

Security and compliance notes:
- OpenBanking integrations often require strict security and consent handling; verify requirements of the target bank and local regulations (e.g., PSD2 in EU).
- Tokens and client secrets should be stored securely (use a secrets manager in production). The repo includes optional Fernet-based encryption for token files when `ADS_ENCRYPTION_KEY` is set.

Example quick test (local):
1. Set env vars in `.env` or environment.
2. Start the app and implement a small route to call `get_payment_connector('openbanking').get_auth_url()` and redirect the user.
3. Complete the OAuth consent and let the callback call `fetch_token(code)`.

If you want, I can add a ready-to-use `/bank/connect`, `/bank/callback`, `/bank/status` routes mirroring the SEM ads flow. Want me to add those now?