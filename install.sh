#!/bin/bash
# OSINT Marketing Tool - Graphical Bash Installer

set -e

function info() {
  whiptail --title "OSINT Installer" --msgbox "$1" 10 60
}

function input() {
  whiptail --title "OSINT Installer" --inputbox "$1" 10 60 "$2" 3>&1 1>&2 2>&3
}

function error() {
  whiptail --title "Error" --msgbox "$1" 10 60
  exit 1
}



# Alpine Linux: Install dependencies if missing

if grep -qi alpine /etc/os-release; then
  echo "Detected Alpine Linux. Installing dependencies with apk..."
  apk update
  apk add --no-cache whiptail python3 py3-pip postgresql-client postgresql-dev gcc musl-dev git bash libffi-dev openssl-dev
  # Ensure pip is available as pip3
  ln -sf /usr/bin/pip3 /usr/bin/pip
fi

# Check dependencies
for dep in whiptail python3 pip psql git; do
  if ! command -v $dep >/dev/null; then
    echo "$dep is required. Please install it."
    exit 1
  fi
done


# Show brand logo and slogan
whiptail --title "puchalla.pro | Systeme. Strategien. Kontrolle." --msgbox "//                       _           _ _                                         \n//                      | |         | | |                                        \n//      _ __  _   _  ___| |__   __ _| | | __ _   _ __  _ __ ___                  \n//     | '_ \\| | | |/ __| '_ \\ / _` | | |/ _` | | '_ \\| '__/ _ \\                 \n//     | |_) | |_| | (__| | | | (_| | | | (_| |_| |_) | | | (_) |                \n//     | .__/ \\__,_|\\___|_| |_|\\__,_|_|_|\\__,_(_) .__/|_|  \\___/                 \n//     | |                                      | |                              \n//     |_|____           _                      |_|  _____ _             _             _                _  __           _             _ _        \n//      / ____|         | |                         / ____| |           | |           (_)              | |/ /          | |           | | |       \n//     | (___  _   _ ___| |_ ___ _ __ ___   ___    | (___ | |_ _ __ __ _| |_ ___  __ _ _  ___ _ __     | ' / ___  _ __ | |_ _ __ ___ | | | ___   \n//      \\___ \\| | | / __| __/ _ \\ '_ ` _ \\ / _ \\    \\___ \\| __| '__/ _` | __/ _ \\/ _` | |/ _ \\ '_ \\    |  < / _ \\| '_ \\| __| '__/ _ \\| | |/ _ \\  \n//      ____) | |_| \\__ \\ ||  __/ | | | | |  __/_   ____) | |_| | | (_| | ||  __/ (_| | |  __/ | | |_  | . \\ (_) | | | | |_| | | (_) | | |  __/_ \n//     |_____/ \\__, |___/\\__\\___|_| |_| |_|\\___|_| |_____/ \\__,_|\\__,_|_|\\___|\\__,_|_|\\___|_| |___| |_|\\___/|_| |_|\\__|_|  \\___/|_| |_____/ \n//              __/ |                                                             __/ |                                                           \n//             |___/                                                             |___/                                                            \n//\n// puchalla.pro | Systeme. Strategien. Kontrolle." 25 120
info "Welcome to the OSINT Marketing Tool Installer!"

# Git clone
REPO_URL=$(input "Enter the git repository URL to clone:" "https://github.com/example/osint_marketing_tool.git")
CLONE_DIR=$(input "Enter the directory to clone into:" "osint_marketing_tool")
if [ ! -d "$CLONE_DIR" ]; then
  git clone "$REPO_URL" "$CLONE_DIR" || error "git clone failed."
fi
cd "$CLONE_DIR"

# Python venv
if whiptail --yesno "Create Python virtual environment?" 10 60; then
  python3 -m venv venv || error "Failed to create venv."
  source venv/bin/activate || error "Failed to activate venv."
fi

# Install requirements
info "Installing Python dependencies..."
pip install -r requirements.txt || error "pip install failed."

# Database setup
DB_USER=$(input "Enter PostgreSQL username:" "osintuser")
DB_PASS=$(input "Enter PostgreSQL password:" "osintpass")
DB_NAME=$(input "Enter PostgreSQL database name:" "osint_db")

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
