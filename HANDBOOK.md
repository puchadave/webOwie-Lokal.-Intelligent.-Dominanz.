# OSINT Marketing Tool – System Handbook

## 1. System Overview

This project is a modular, AI-driven business platform built with Flask. It integrates accounting, document management, CRM, social media automation, business website generator, webmail, email marketing, and a floating AI chat widget. The system supports multi-tenant operation and full data access for AI modules.

## 2. Architecture & Modules

- **Flask App**: Central application, modular blueprints for each business function.
- **AI Clients**: Gemini (default), OpenAI, Ollama (switchable via environment/config).
- **Floating Chat Widget**: Modern UI, file upload, speech-to-text (STT), text-to-speech (TTS), backend API integration.
- **Multi-Tenant Support**: Per-tenant storage, configuration, and data isolation.

### Main Modules

- **Accounting & DMS**: Invoicing, reminders, eInvoice generation, document upload, payment connector stubs.
- **CRM**: Automated lead generation, OSINT-based analysis, psychoprofile, strategy suggestions.
- **Social Media Management**: KI-based post generation, OSINT/SOCMINT/HUMINT analysis, scheduling, auto-posting.
- **Business Website**: KI-powered website generator, simple CMS, multi-page support.
- **Email Marketing**: KI-generated, individualized campaigns, scheduling, analytics.
- **Webmail**: IMAP/SMTP integration, basic email client features.

## 3. Quick Start

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables (see config.example.env).

3. Run the app:

   ```bash
   python app.py
   ```

4. Access modules via browser:
5. Access modules via browser:
   - Accounting: <http://127.0.0.1:5000/accounting/>
   - Documents: <http://127.0.0.1:5000/documents/>
   - CRM: <http://127.0.0.1:5000/crm/>
   - Social: <http://127.0.0.1:5000/social/>
   - Business Site: <http://127.0.0.1:5000/business_site/>
   - Email Marketing: <http://127.0.0.1:5000/email_marketing/>
   - Webmail: <http://127.0.0.1:5000/webmail/>

## 4. AI Integration

- **Default Engine**: Gemini (Google, GPT-4.1)
- **Switchable**: OpenAI, Ollama (via environment/config)
- **Full Data Access**: AI modules can access invoices, leads, documents, users, posts, etc.
- **Usage**: Each module uses AI for generation, analysis, and automation (see respective blueprint).

## 5. Floating Chat Widget

- **Features**: File upload, speech-to-text, text-to-speech, persistent chat, backend API (/api/ai_chat)
- **UI**: Modern, floating, cross-window
- **Extensibility**: Add custom actions, connect to other modules

## 6. Security & Compliance

- **Secrets**: Use environment variables or secret managers
- **Uploads**: Validate, limit size, scan for viruses
- **HTTPS**: Required in production
- **eInvoice**: UBL-like XML, country-specific compliance required

## 7. Extending & Customizing

- **Connectors**: Add real API calls in connectors/
- **Templates**: Customize HTML in templates/
- **Storage**: Per-tenant folders in storage/tenants/
- **AI**: Swap or extend AI clients in utils/

## 8. API Endpoints & Blueprints

- Each module registers a Flask blueprint (see app.py)
- Example endpoints:
  - /accounting/run_dunning (POST): Run dunning cycle
  - /social/generate (POST): Generate social post
  - /business_site/generate (POST): Generate website
  - /email_marketing/send (POST): Send campaign
  - /api/ai_chat (POST): Chat with AI

## 9. Example Workflow

- Create tenant, configure .env
- Upload documents, create invoices
- Generate leads via CRM
- Schedule and auto-post on social media
- Generate and publish business website
- Run email marketing campaigns
- Use floating chat for support, automation, or data queries

## 10. Legal Notes

- eInvoice formats and signing/validation requirements vary by country
- Consult local legal frameworks for compliance
- Use certified libraries for production

## 11. Troubleshooting

- Check logs for errors
- Validate environment variables
- Ensure correct file/folder permissions
- For OAuth, match redirect URIs exactly

## 12. Further Reading

- See README_ACCOUNTING.md, README_OAUTH.md, README_OPENBANKING.md, README_TENANTS.md for module-specific details.

---

For questions or further customization, contact the project maintainer or use the floating chat widget for instant AI support.
