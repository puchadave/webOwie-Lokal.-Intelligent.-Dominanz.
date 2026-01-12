#!/bin/bash
# OSINT Marketing Tool - Minimal Bash Installer (No git clone, no Alpine, no logo)

set -e

function info() {
  echo "[INFO] $1"
}

function input() {
  read -p "$1 [$2]: " value
  echo "${value:-$2}"
}

function error() {
  echo "[ERROR] $1" >&2
  exit 1
}

# Check dependencies (assume all are pre-installed)
for dep in whiptail python3 pip psql git; do
  if ! command -v $dep >/dev/null; then
    echo "$dep is required. Please install it."
    exit 1
  fi
done

info "Welcome to the OSINT Marketing Tool Installer!"

# Python venv
read -p "Create Python virtual environment? [Y/n]: " venv_choice
venv_choice=${venv_choice:-Y}
if [[ "$venv_choice" =~ ^[Yy]$ ]]; then
  python3 -m venv venv || error "Failed to create venv."
  source venv/bin/activate || error "Failed to activate venv."
fi

# Install requirements
info "Installing Python dependencies..."
pip install -r requirements.txt || error "pip install failed."

# Database setup
DB_USER=$(input "Enter PostgreSQL username" "osintuser")
DB_PASS=$(input "Enter PostgreSQL password" "osintpass")
DB_NAME=$(input "Enter PostgreSQL database name" "osint_db")

info "Creating PostgreSQL database..."
export PGPASSWORD="$DB_PASS"
psql -U "$DB_USER" -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || true

# .env setup
if [ ! -f .env ]; then
  cp config.example.env .env
fi
sed -i "s|^DATABASE_URL=.*|DATABASE_URL=postgresql://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME|" .env

info "Database and environment configured."

# Initialize DB tables
info "Initializing database tables..."
python3 app.py || error "Database initialization failed."

info "Installation complete! Start the server with: python3 app.py"
