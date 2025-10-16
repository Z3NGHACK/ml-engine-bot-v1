#!/bin/bash
# ============================================
# migrate.sh - Quick migration script
# Run: bash migrate.sh
# ============================================

echo "🚀 Trading Bot Migration Script"
echo "================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ requirements.txt not found${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Backing up original files${NC}"
mkdir -p backup
cp -r analysis/ backup/analysis_old 2>/dev/null || true
cp api/app.py backup/app_old.py 2>/dev/null || true
echo -e "${GREEN}✅ Backup created in ./backup/${NC}"

echo -e "${YELLOW}Step 2: Creating new enhanced modules${NC}"

# Create technical_enhanced.py (copy content from artifact)
cat > analysis/technical_enhanced.py << 'EOF'
# This file should be copied from the artifact: "Enhanced Technical Analysis Module"
# See the artifact for complete code
print("Please copy technical_enhanced.py from the artifact")
EOF

# Create pattern_detection_enhanced.py
cat > analysis/pattern_detection_enhanced.py << 'EOF'
# This file should be copied from the artifact: "Enhanced Pattern Detection Module"
# See the artifact for complete code
print("Please copy pattern_detection_enhanced.py from the artifact")
EOF

# Create improved API
cat > api/app_improved.py << 'EOF'
# This file should be copied from the artifact: "Improved ML Engine API"
# See the artifact for complete code
print("Please copy app_improved.py from the artifact")
EOF

echo -e "${YELLOW}Step 3: Creating worker.py${NC}"

cat > worker.py << 'EOF'
# This file should be copied from the artifact: "Background Worker Script"
# See the artifact for complete code
print("Please copy worker.py from the artifact")
EOF

echo -e "${YELLOW}Step 4: Updating requirements.txt${NC}"

# Add new requirements
cat >> requirements.txt << 'EOF'

# Background processing
schedule==1.2.0
python-telegram-bot==21.8
requests==2.31.0
EOF

echo -e "${GREEN}✅ requirements.txt updated${NC}"

echo -e "${YELLOW}Step 5: Creating GitHub Actions workflow${NC}"

mkdir -p .github/workflows
cat > .github/workflows/trading-bot-worker.yml << 'EOF'
name: Trading Bot Worker

on:
  schedule:
    - cron: '*/5 * * * *'
  workflow_dispatch:

jobs:
  collect-analyze:
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run Worker
        env:
          MONGODB_URI: ${{ secrets.MONGODB_URI }}
          BINANCE_API_KEY: ${{ secrets.BINANCE_API_KEY }}
          BINANCE_API_SECRET: ${{ secrets.BINANCE_API_SECRET }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: python worker.py --run-once
EOF

echo -e "${GREEN}✅ GitHub Actions workflow created${NC}"

echo -e "${YELLOW}Step 6: Creating Procfile for Railway/Render${NC}"

cat > Procfile << 'EOF'
api: uvicorn api.app_improved:app --host 0.0.0.0 --port $PORT
worker: python worker.py
EOF

echo -e "${GREEN}✅ Procfile created${NC}"

echo -e "${YELLOW}Step 7: Creating render.yaml${NC}"

cat > render.yaml << 'EOF'
services:
  - type: web
    name: ml-engine-api
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn api.app_improved:app --host 0.0.0.0 --port $PORT

  - type: background_worker
    name: trading-bot-worker
    env: python
    plan: standard
    buildCommand: pip install -r requirements.txt
    startCommand: python worker.py
EOF

echo -e "${GREEN}✅ render.yaml created${NC}"

echo ""
echo "================================"
echo -e "${GREEN}✅ Migration Script Complete!${NC}"
echo "================================"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo ""
echo "1. Copy content from artifacts to new files:"
echo "   - technical_enhanced.py"
echo "   - pattern_detection_enhanced.py"
echo "   - app_improved.py"
echo "   - worker.py"
echo ""
echo "2. Test locally:"
echo "   pip install -r requirements.txt"
echo "   python -c 'from analysis.technical_enhanced import EnhancedTechnicalAnalyzer'"
echo ""
echo "3. Push to GitHub:"
echo "   git add ."
echo "   git commit -m 'Add enhanced ML engine v2'"
echo "   git push origin main"
echo ""
echo "4. Choose deployment:"
echo "   Option A: GitHub Actions (FREE) - just add secrets"
echo "   Option B: Render/Railway - connect GitHub repo"
echo ""
echo -e "${YELLOW}Important:${NC}"
echo "- Don't forget to replace placeholder files with actual artifact content"
echo "- Add GitHub secrets before pushing"
echo "- Backup created in ./backup/ directory"
echo ""
echo -e "${GREEN}Happy trading! 🚀${NC}"