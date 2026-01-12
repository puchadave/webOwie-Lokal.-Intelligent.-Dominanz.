<a href="https://puchalla.pro"><img width="1024" height="1024" alt="puchalla.pro | Systeme. Strategien. Kontrolle." src="https://github.com/user-attachments/assets/3da3e852-6b54-4688-8324-c6b5e12505ab" /></a>

# OSINT Marketing Tool

## Installation

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd osint_marketing_tool
   ```

2. **Create and activate a Python virtual environment (recommended):**
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Copy and configure environment variables:**
   ```sh
   cp config.example.env .env
   # Edit .env to set your API keys, database URL, and other secrets
   ```

5. **Set up the PostgreSQL database:**
   - Ensure PostgreSQL is running and create a database (e.g., `osint_db`).
   - Update `DATABASE_URL` in `.env` (e.g., `postgresql://user:password@localhost:5432/osint_db`).

6. **Initialize the database:**
   ```sh
   python app.py  # The app will create tables on first run
   ```

7. **Start the Flask server:**
   ```sh
   python app.py
   # Or use the VS Code task: Start Flask Debug Server
   ```



## Usage

- **Access the main dashboard:**
  - Open [http://localhost:5000/dashboard](http://localhost:5000/dashboard) in your browser.

- **Specialized dashboards:**
  - Social Media Manager: [http://localhost:5000/dashboard/social](http://localhost:5000/dashboard/social)
  - SEO/SEA: [http://localhost:5000/dashboard/sem](http://localhost:5000/dashboard/sem)
  - OSINT Market Analysis: [http://localhost:5000/dashboard/osint](http://localhost:5000/dashboard/osint)
  - System Architect: [http://localhost:5000/dashboard/arch](http://localhost:5000/dashboard/arch)
  - Cybersecurity: [http://localhost:5000/dashboard/cyber](http://localhost:5000/dashboard/cyber)

- **Manual backup:**
  - Run `python backup.py` for a manual backup
  - Run `python backup_ai.py` for AI-driven backup and monitoring

- **Tenant and business modules:**
  - Access CRM, accounting, ecommerce, and other modules via their respective routes or dashboards.

- **Configuration:**
  - Edit `.env` for API keys, database, and service credentials.

- **Extending:**
  - Add new connectors in `connectors/`, business logic in domain files, and templates in `templates/`.


## Notes
- Requires Python 3.8+
- Requires PostgreSQL for database storage
- For production, configure environment variables securely and use a production-ready WSGI server (e.g., gunicorn)
