# Accounting & DMS Module (Scaffold)

This module provides a lightweight scaffold for accounting/invoicing, dunning, document management and payment connector stubs.

Quick start

- Install dependencies:

```bash
pip install -r requirements.txt
```

- Create a local SQLite DB and run the app (app.py will call create_all on startup):

```bash
python app.py
```

- Open <http://127.0.0.1:5000/accounting/> to view invoices and <http://127.0.0.1:5000/documents/> to upload documents.

Connectors

- Connector stubs are in `connectors/` with placeholder methods. Configure credentials via environment variables (see `config.example.env`). Replace TODOs with real API calls.

eInvoice & legal notes

- The provided eInvoice generator creates a simple UBL-like XML at `storage/einvoices/` with basic fields. Real eInvoice formats and signing/validation requirements vary by country — consult your local legal framework and use certified libraries for production.

Security

- Do not store plaintext secrets in repo. Use environment variables or secret managers.
- Use HTTPS in production, validate and limit uploads, and run virus scanning on uploaded files.

Dunning

- `run_dunning_cycle()` finds overdue invoices and creates `Reminder` entries. Run it via cron or a management script, e.g. `curl -X POST http://localhost:5000/accounting/run_dunning`.

AI stubs

- `ai_categorize_transaction()` and `ai_generate_dunning_text()` are deterministic placeholders — replace with calls to your preferred AI provider.
