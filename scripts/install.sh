#!/usr/bin/env bash
#
# tldrs-vhs installer
# One-liner: curl -fsSL https://raw.githubusercontent.com/mistakeknot/tldrs-vhs/main/scripts/install.sh | bash
#
# Options:
#   --yes           Skip confirmation prompts
#   --dir PATH      Installation directory (default: ~/tldrs-vhs)
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default options
INSTALL_DIR="${HOME}/tldrs-vhs"
SKIP_CONFIRM=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --yes|-y)
            SKIP_CONFIRM=true
            shift
            ;;
        --dir)
            INSTALL_DIR="$2"
            shift 2
            ;;
        --help|-h)
            echo "tldrs-vhs installer"
            echo ""
            echo "Usage: install.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --yes, -y       Skip confirmation prompts"
            echo "  --dir PATH      Installation directory (default: ~/tldrs-vhs)"
            echo "  --help, -h      Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           tldrs-vhs Installer                                 ║${NC}"
echo -e "${BLUE}║   Local content-addressed store (vhs:// refs)                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Confirmation
if [ "$SKIP_CONFIRM" = false ]; then
    echo -e "This will install tldrs-vhs to: ${GREEN}${INSTALL_DIR}${NC}"
    echo ""
    read -p "Continue? [Y/n] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]] && [[ ! -z $REPLY ]]; then
        echo "Aborted."
        exit 0
    fi
fi

# Step 1: Install uv if not present
echo ""
echo -e "${BLUE}[1/3]${NC} Checking for uv package manager..."

if command -v uv &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} uv is already installed: $(uv --version)"
else
    echo -e "  ${YELLOW}→${NC} Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    if command -v uv &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} uv installed successfully"
    else
        echo -e "  ${RED}✗${NC} Failed to install uv"
        exit 1
    fi
fi

# Step 2: Clone or update repository
echo ""
echo -e "${BLUE}[2/3]${NC} Setting up repository..."

if [ -d "$INSTALL_DIR" ]; then
    echo -e "  ${YELLOW}→${NC} Directory exists, updating..."
    cd "$INSTALL_DIR"
    git pull --ff-only 2>/dev/null || echo -e "  ${YELLOW}!${NC} Could not update (local changes?)"
else
    echo -e "  ${YELLOW}→${NC} Cloning repository..."
    git clone https://github.com/mistakeknot/tldrs-vhs "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi
echo -e "  ${GREEN}✓${NC} Repository ready at ${INSTALL_DIR}"

# Step 3: Set up Python environment with uv
echo ""
echo -e "${BLUE}[3/3]${NC} Setting up Python environment..."

if ! uv python find ">=3.10" &>/dev/null; then
    echo -e "  ${YELLOW}→${NC} Installing Python 3.11..."
    uv python install 3.11
else
    echo -e "  ${GREEN}✓${NC} Python 3.10+ available"
fi

echo -e "  ${YELLOW}→${NC} Installing dependencies..."
if [ -f "uv.lock" ]; then
    uv sync 2>&1 | grep -v "^  " || true
else
    uv venv -p 3.11 2>/dev/null || true
    uv pip install -e . 2>&1 | tail -5
fi
echo -e "  ${GREEN}✓${NC} Python environment ready"

echo ""
echo -e "${BLUE}Verifying installation...${NC}"
if uv run tldrs-vhs --help > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} CLI is working"
else
    source .venv/bin/activate 2>/dev/null || true
    if tldrs-vhs --help > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} CLI is working"
    else
        echo -e "  ${RED}✗${NC} CLI verification failed"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}Done.${NC}"
echo -e "Run: ${BLUE}tldrs-vhs --help${NC}"
echo -e "Store data lives at: ${BLUE}~/.tldrs-vhs/${NC}"
