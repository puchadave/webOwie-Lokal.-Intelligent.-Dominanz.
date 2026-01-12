# Copilot Instructions for AI Agents

## Project Overview
This is an OSINT marketing tool built with Python and Flask. The codebase is modular, with each business function (accounting, CRM, ecommerce, social, etc.) implemented in a separate file or submodule. The architecture is designed for extensibility and integration with external APIs and services.

## Major Components
- **Cybersecurity Dashboard**: Security KPIs and analytics at `/dashboard/cyber`.
- **Specialized Dashboards**: Role-specific dashboards for Social Media Manager (`/dashboard/social`), SEO/SEA (`/dashboard/sem`), OSINT Market Analysis (`/dashboard/osint`), and System Architect (`/dashboard/arch`).
- **Dashboard**: Real-time visualization of metrics, KPIs, and analytics from all modules at `/dashboard`.
- **Main Application**: `app.py` (Flask server entry point)
- **Business Modules**: Files like `accounting.py`, `crm.py`, `ecommerce.py`, `blog.py`, etc. Each handles a distinct business domain.
- **Connectors**: `connectors/` contains API integrations (e.g., bank, social media, ads). Each connector is a separate file following a similar pattern.
- **Templates**: `templates/` holds Jinja2 HTML templates for UI rendering.
- **Static Files**: `static/` for CSS and static assets.
- **Storage**: `storage/tenants/` organizes tenant-specific data (documents, ads, invoices) in a multi-tenant structure.
- **Utils**: `utils/` provides shared helpers for AI, crypto, and API clients.

## Developer Workflows
- **Cybersecurity Dashboard**: Access security metrics and analytics at `/dashboard/cyber`. Data is aggregated via `/api/cyber_dashboard_metrics` and visualized with Chart.js.
- **Specialized Dashboards**: Access role-specific analytics at the respective dashboard routes. Data is aggregated via `/api/*_dashboard_metrics` endpoints and visualized with Chart.js.
- **Dashboard**: Access system-wide metrics and analytics at `/dashboard`. Data is aggregated via `/api/dashboard_metrics` and visualized with Chart.js.
- **Run Server**: Use the VS Code task "Start Flask Debug Server" or run `python app.py` from the project root.
- **Configuration**: Copy `config.example.env` to `.env` and set environment variables for API keys and secrets.
- **Dependencies**: Install Python packages from `requirements.txt`.
- **Multi-Tenancy**: Tenant data is isolated in `storage/tenants/<tenant>/`. Update `tenants.json` and `manage_tenants.py` for tenant management.

## Project-Specific Patterns
- **Connector Pattern**: Each external service integration is a class/module in `connectors/`, with a consistent interface for authentication and data retrieval.
- **Modular Business Logic**: Business domains are separated by file, with minimal cross-file dependencies.
- **Template Usage**: Flask routes render templates from `templates/`, passing context from business modules.
- **AI Integration**: Utilities in `utils/` (e.g., `openai_client.py`, `gemini_client.py`) abstract AI service calls.

## Integration Points
- **External APIs**: Bank, social media, ads, and payment connectors in `connectors/`.
- **AI Services**: Accessed via utility clients in `utils/`.
- **Tenant Data**: Read/write from `storage/tenants/` using tenant-specific paths.

## Conventions
- **File Naming**: Business logic files are named after their domain (e.g., `accounting.py`, `crm.py`).
- **Connector Naming**: Each connector is named for its service (e.g., `google_ads.py`, `facebook_api.py`).
- **Minimal Global State**: Prefer passing context explicitly between modules.

## Key Files & Directories
 - `backup.py`: Backup solution for tenant and config data
- `models.py`: SQLAlchemy ORM models for all business data

## Example: Adding a New Connector
1. Create a new file in `connectors/` (e.g., `new_service_connector.py`).
2. Implement authentication and data retrieval methods following existing connector patterns.
3. Update relevant business modules to use the new connector.
4. Add configuration to `.env` if needed.

---
For questions or unclear patterns, review the structure above and reference existing connectors and business modules for implementation examples.


## Backup Solution
- The `backup.py` module provides manual backup functionality for tenant data and config files.
- The `backup_ai.py` module implements AI-driven backup:
	- Monitors file changes and triggers incremental backups automatically
	- Schedules regular full-system backups
	- Uses OpenAI (see `utils/openai_client.py`) to optimize backup frequency and retention
	- Integrates with Flask via `backup_bp` for status and manual triggers (`/backup/full`, `/backup/advice`)
	- Stores backups as zip files in `storage/backups/`
- Start the monitor via CLI: `python backup_ai.py` (runs in background)
- Extend or configure AI logic as needed for your deployment.
