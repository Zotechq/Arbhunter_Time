# ArbHunter Time - Complete Setup & Run Guide

## One-Time Setup

```bash
# 1. Navigate to project folder
cd /home/edwin/PycharmProjects/Arbhunter_Time

# 2. Remove old virtual environment (if exists)
rm -rf .venv

# 3. Create new virtual environment
python3 -m venv .venv

# 4. Activate it
source .venv/bin/activate

# 5. Install all required packages
pip install requests beautifulsoup4 selenium webdriver-manager tabulate schedule lxml stem

# 6. Verify installation
python -c "import schedule; print('✅ Setup complete!')"