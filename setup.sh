#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON=$(which python3)

echo "=== greytHR Auto Punch Setup ==="
echo ""

# 1. Check Python
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found. Install Python 3.8+ first."
    exit 1
fi
echo "[OK] Python3 found: $PYTHON"

# 2. Check Google Chrome
if [ -d "/Applications/Google Chrome.app" ]; then
    echo "[OK] Google Chrome found"
elif command -v google-chrome &>/dev/null; then
    echo "[OK] Google Chrome found"
else
    echo "ERROR: Google Chrome not found. Install it from https://www.google.com/chrome/"
    exit 1
fi

# 3. Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install selenium webdriver-manager
echo "[OK] Dependencies installed"

# 4. Setup .env file
echo ""
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    echo "Created .env file from .env.example"
    echo "IMPORTANT: Edit .env and fill in your credentials:"
    echo "  $SCRIPT_DIR/.env"
    echo ""
    read -rp "Enter your greytHR Login ID: " login_id
    read -rsp "Enter your greytHR Password: " password
    echo ""
    read -rp "Enter your greytHR URL [https://webshar-india.greythr.com/]: " url
    url="${url:-https://webshar-india.greythr.com/}"

    cat > "$SCRIPT_DIR/.env" <<EOF
GREYTHR_URL=$url
GREYTHR_LOGIN_ID=$login_id
GREYTHR_PASSWORD=$password
EOF
    echo "[OK] Credentials saved to .env"
else
    echo "[OK] .env file already exists"
fi

# 5. Setup cron jobs
echo ""
read -rp "Set up cron jobs for auto sign-in (10:05 AM) and sign-out (9:50 PM) on weekdays? [y/N]: " setup_cron
if [[ "$setup_cron" =~ ^[Yy]$ ]]; then
    # Remove existing greythr cron entries
    crontab -l 2>/dev/null | grep -v "greythr_punch" > /tmp/crontab_clean || true

    echo "5 10 * * 1-5 cd $SCRIPT_DIR && $PYTHON $SCRIPT_DIR/greythr_punch.py signin >> $SCRIPT_DIR/greythr_punch.log 2>&1" >> /tmp/crontab_clean
    echo "50 21 * * 1-5 cd $SCRIPT_DIR && $PYTHON $SCRIPT_DIR/greythr_punch.py signout >> $SCRIPT_DIR/greythr_punch.log 2>&1" >> /tmp/crontab_clean

    crontab /tmp/crontab_clean
    rm /tmp/crontab_clean

    echo "[OK] Cron jobs installed:"
    crontab -l | grep greythr
else
    echo "Skipped cron setup. You can run manually:"
    echo "  python3 $SCRIPT_DIR/greythr_punch.py signin"
    echo "  python3 $SCRIPT_DIR/greythr_punch.py signout"
fi

# 6. Test run
echo ""
read -rp "Run a test sign-in now? [y/N]: " test_run
if [[ "$test_run" =~ ^[Yy]$ ]]; then
    echo "Running test sign-in..."
    $PYTHON "$SCRIPT_DIR/greythr_punch.py" signin
    echo "[OK] Test sign-in completed. Check greythr_punch.log for details."
else
    echo "Skipped test run."
fi

echo ""
echo "=== Setup Complete ==="
echo "Logs: $SCRIPT_DIR/greythr_punch.log"
echo "Errors: $SCRIPT_DIR/error_signin.png / error_signout.png (on failure)"
