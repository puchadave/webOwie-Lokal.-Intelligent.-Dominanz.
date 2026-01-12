# Agenturmodus (Multi-tenant)

This project supports two options for running multiple customers (tenants):

1. Shared single-app mode (multi-tenant): run the app once and extend routes/templates to handle `tenant_id` in requests. This requires code changes to partition data by `tenant_id` in DB models.

2. Isolated per-tenant instances (recommended for agency mode): run one app process per customer using a separate SQLite DB and storage directory. This scaffold supports option 2 via the `TENANT` environment variable.

How to create and run a tenant (isolated instance):

1. Create a tenant:

```bash
python manage_tenants.py create "Kunde GmbH" kunde1
```

This will create `storage/tenants/kunde1/` and copy `config.example.env` to `.env.kunde1`.

1. Edit `.env.kunde1` if you need per-tenant credentials.

2. Run the tenant instance:

```bash
TENANT=kunde1 python app.py
```

The app will use `storage/tenants/kunde1/app.db`, `storage/tenants/kunde1/documents` and `storage/tenants/kunde1/einvoices` for data and files.

Notes

- This scaffold uses SQLite for per-tenant DB in development. For production, use a managed DB per tenant or a robust multi-tenant strategy.
- For true data isolation, run each tenant behind its own process or container and use separate credentials.
- Be careful with secrets and use secret managers for production.
