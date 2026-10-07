#!/bin/bash
# MX26 Factory Setup — run on MX26
# Requires: GITHUB_TOKEN set in environment or .env file
set -e

echo "=== MX26 Factory Setup ==="

# 1. Install prerequisites
echo "[1/6] Installing prerequisites..."
sudo yum install -y python3 python3-pip git 2>/dev/null || sudo apt-get install -y python3 python3-pip git

# 2. Install Python deps
echo "[2/6] Installing Python dependencies..."
pip3 install requests python-dotenv 2>/dev/null || pip3 install --break-system-packages requests python-dotenv

# 3. Clone factory
echo "[3/6] Cloning factory..."
if [ -d ~/ai-factory ]; then
    cd ~/ai-factory && git pull
else
    git clone https://github.com/ALANDVO/ai-factory-alan-vo.git ~/ai-factory
fi
cd ~/ai-factory

# 4. Set up .env (requires GITHUB_TOKEN in environment)
echo "[4/6] Configuring environment..."
if [ -z "$GITHUB_TOKEN" ]; then
    echo "  ERROR: GITHUB_TOKEN not set. Run: export GITHUB_TOKEN=ghp_..."
    echo "  Then re-run this script."
    exit 1
fi
cat > .env << ENVEOF
GITHUB_TOKEN=$GITHUB_TOKEN
GITHUB_USER=ALANDVO
EMAIL=alanvo@gmail.com
ENVEOF

# 5. Set up cron (every 10 minutes)
echo "[5/6] Setting up cron..."
CRON_ENTRY="*/10 * * * * cd ~/ai-factory && source .env && export GITHUB_TOKEN && python3 factory.py >> ~/ai-factory/cron.log 2>&1"
(crontab -l 2>/dev/null | grep -v "ai-factory" ; echo "$CRON_ENTRY") | crontab -
echo "  Cron installed: every 10 minutes"

# 6. Test run
echo "[6/6] Test run..."
source .env && export GITHUB_TOKEN && python3 factory.py

echo ""
echo "=== Setup Complete ==="
echo "Factory is running on a 10-minute cron schedule."
echo "Check logs: tail -f ~/ai-factory/cron.log"
echo "Current repos: https://github.com/ALANDVO?tab=repositories&q=alan-vo&type=&language=&sort="
