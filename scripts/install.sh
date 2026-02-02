#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}[*] Installing AI Kali Agent...${NC}"

# Define paths
INSTALL_DIR="/usr/local/bin"
CONFIG_DIR="$HOME/.config/kali-ai-agent"
TOOLS_DIR="$HOME/.agent-tools"
AGENT_DIR="$(pwd)"

# Create directories
echo -e "${BLUE}[*] Creating directories...${NC}"
mkdir -p "$CONFIG_DIR"
mkdir -p "$TOOLS_DIR"

# Install dependencies
echo -e "${BLUE}[*] Installing Python dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    python3 -m pip install -r requirements.txt
else
    python3 -m pip install requests toml
fi

# Link configuration if not exists
if [ ! -f "$CONFIG_DIR/config.toml" ]; then
    echo -e "${BLUE}[*] copying default config...${NC}"
    cp config/default.toml "$CONFIG_DIR/config.toml"
fi

# Create executable wrapper
echo -e "${BLUE}[*] Creating 'agent' command...${NC}"
cat << EOF > agent_wrapper
#!/bin/bash
export PYTHONPATH="$AGENT_DIR:\$PYTHONPATH"
python3 "$AGENT_DIR/agent/main.py" "\$@"
EOF

chmod +x agent_wrapper
sudo mv agent_wrapper "$INSTALL_DIR/KD"

echo -e "${GREEN}[+] Installation complete!${NC}"
echo -e "Run 'KD \"scan localhost\"' to test."
