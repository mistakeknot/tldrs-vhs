#!/usr/bin/env bash
#
# tldrs-vhs uninstaller
# One-liner: curl -fsSL https://raw.githubusercontent.com/mistakeknot/tldrs-vhs/main/scripts/uninstall.sh | bash
#
# Options:
#   --yes           Skip confirmation prompts
#   --dir PATH      Installation directory (default: ~/tldrs-vhs)
#   --purge-store   Also remove ~/.tldrs-vhs data
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

INSTALL_DIR="${HOME}/tldrs-vhs"
SKIP_CONFIRM=false
PURGE_STORE=false

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
        --purge-store)
            PURGE_STORE=true
            shift
            ;;
        --help|-h)
            echo "tldrs-vhs uninstaller"
            echo ""
            echo "Usage: uninstall.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --yes, -y       Skip confirmation prompts"
            echo "  --dir PATH      Installation directory (default: ~/tldrs-vhs)"
            echo "  --purge-store   Also remove ~/.tldrs-vhs data"
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
echo -e "${BLUE}║           tldrs-vhs Uninstaller                                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$SKIP_CONFIRM" = false ]; then
    echo -e "This will remove: ${GREEN}${INSTALL_DIR}${NC}"
    if [ "$PURGE_STORE" = true ]; then
        echo -e "Store data will also be removed: ${GREEN}~/.tldrs-vhs${NC}"
    else
        echo -e "Store data will be kept at: ${GREEN}~/.tldrs-vhs${NC}"
    fi
    echo ""
    read -p "Continue? [Y/n] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]] && [[ ! -z $REPLY ]]; then
        echo "Aborted."
        exit 0
    fi
fi

# Step 1: Remove shell alias
echo ""
echo -e "${BLUE}[1/3]${NC} Removing shell alias..."

SHELL_RC=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

if [ -n "$SHELL_RC" ]; then
    if grep -q "alias tldrs-vhs=" "$SHELL_RC" 2>/dev/null; then
        sed -i.bak '/# tldrs-vhs/d' "$SHELL_RC"
        sed -i.bak '/alias tldrs-vhs=/d' "$SHELL_RC"
        rm -f "${SHELL_RC}.bak"
        echo -e "  ${GREEN}✓${NC} Removed alias from ${SHELL_RC}"
    else
        echo -e "  ${YELLOW}→${NC} No alias found in ${SHELL_RC}"
    fi
else
    echo -e "  ${YELLOW}→${NC} No shell rc file found"
fi

# Step 2: Remove installation directory
echo ""
echo -e "${BLUE}[2/3]${NC} Removing installation directory..."

if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    echo -e "  ${GREEN}✓${NC} Removed ${INSTALL_DIR}"
else
    echo -e "  ${YELLOW}!${NC} ${INSTALL_DIR} not found"
fi

if [ "$PURGE_STORE" = true ]; then
    echo ""
    echo -e "${BLUE}[3/3]${NC} Removing store data..."
    rm -rf "${HOME}/.tldrs-vhs"
    echo -e "  ${GREEN}✓${NC} Removed ~/.tldrs-vhs"
fi

echo ""
echo -e "${GREEN}Done.${NC}"
if [ -n "$SHELL_RC" ]; then
    echo -e "Restart your shell or run: ${BLUE}source ${SHELL_RC}${NC}"
fi
