#!/bin/bash
# ============================================
#  Flowborn Poster Tool - Setup Script
#  by hienmods
# ============================================

RED='\033[91m'
GREEN='\033[92m'
CYAN='\033[96m'
YELLOW='\033[93m'
BOLD='\033[1m'
RESET='\033[0m'

echo ""
echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════╗${RESET}"
echo -e "${CYAN}${BOLD}║  Flowborn Poster Tool - Auto Setup       ║${RESET}"
echo -e "${CYAN}${BOLD}║  by hienmods                             ║${RESET}"
echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════╝${RESET}"
echo ""

# Check Termux
if [ ! -d "/data/data/com.termux" ]; then
    echo -e "${YELLOW}⚠  Khong phat hien Termux. Script nay danh cho Termux.${RESET}"
fi

# Update packages
echo -e "${CYAN}›  Cap nhat package...${RESET}"
pkg update -y > /dev/null 2>&1

# Install Python
echo -e "${CYAN}›  Cai dat Python...${RESET}"
pkg install -y python > /dev/null 2>&1
if command -v python &> /dev/null; then
    echo -e "${GREEN}✓  Python: $(python --version 2>&1)${RESET}"
else
    echo -e "${RED}✗  Cai dat Python that bai!${RESET}"
    exit 1
fi

# Install Node.js
echo -e "${CYAN}›  Cai dat Node.js...${RESET}"
pkg install -y nodejs > /dev/null 2>&1
if command -v node &> /dev/null; then
    echo -e "${GREEN}✓  Node.js: $(node --version)${RESET}"
else
    echo -e "${RED}✗  Cai dat Node.js that bai!${RESET}"
    exit 1
fi

# Install Python packages
echo -e "${CYAN}›  Cai dat requests + Pillow...${RESET}"
pip install requests Pillow > /dev/null 2>&1
echo -e "${GREEN}✓  Python packages OK${RESET}"

# Check files
echo ""
echo -e "${CYAN}›  Kiem tra files...${RESET}"
FILES_OK=true
for f in "flowborn_poster.py" "sign_bridge.js" "camp-security-oversea.0.1.0.js"; do
    if [ -f "$f" ]; then
        echo -e "${GREEN}✓  $f${RESET}"
    else
        echo -e "${RED}✗  THIEU: $f${RESET}"
        FILES_OK=false
    fi
done

echo ""
echo -e "${CYAN}${BOLD}═══════════════════════════════════════════${RESET}"

if [ "$FILES_OK" = true ]; then
    echo -e "${GREEN}${BOLD}✓  Setup hoan tat!${RESET}"

    # Tao lenh tat 'flb'
    FLB_PATH="$PREFIX/bin/flb"
    TOOL_DIR="$(pwd)"
    echo "#!/data/data/com.termux/files/usr/bin/bash" > "$FLB_PATH"
    echo "cd \"$TOOL_DIR\" && exec python flowborn_poster.py \"\$@\"" >> "$FLB_PATH"
    chmod +x "$FLB_PATH"
    echo -e "${GREEN}✓  Lenh tat 'flb' da duoc tao!${RESET}"

    echo ""
    echo -e "${CYAN}  CACH SU DUNG:${RESET}"
    echo -e "  1. Copy file ${YELLOW}.har${RESET} vao thu muc nay"
    echo -e "  2. Copy ${YELLOW}anh/video${RESET} vao thu muc nay"
    echo -e "  3. Chay: ${GREEN}flb${RESET}"
    echo ""
    echo -e "  ${CYAN}Cac lenh khac:${RESET}"
    echo -e "    ${GREEN}flb${RESET}              — Chay tool"
    echo -e "    ${GREEN}flb --device-id${RESET}  — Xem ma thiet bi"
    echo -e "    ${GREEN}flb --test-sign${RESET}  — Test sign bridge"
else
    echo -e "${RED}${BOLD}✗  Thieu files! Vui long copy day du files.${RESET}"
fi
echo ""
