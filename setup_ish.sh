#!/bin/sh
# ============================================
#  Flowborn Poster Tool - Setup for iSH (iOS)
#  by hienmods
# ============================================

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  Flowborn Poster Tool - iSH Setup        ║"
echo "║  by hienmods                              ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# iSH dung Alpine Linux (apk)
echo ">>> Cap nhat package..."
apk update 2>/dev/null

# Install Python3
echo ">>> Cai dat Python3..."
apk add python3 py3-pip 2>/dev/null
if command -v python3 >/dev/null 2>&1; then
    echo "[OK] Python3: $(python3 --version 2>&1)"
else
    echo "[FAIL] Cai dat Python3 that bai!"
    exit 1
fi

# Install Node.js
echo ">>> Cai dat Node.js..."
apk add nodejs npm 2>/dev/null
if command -v node >/dev/null 2>&1; then
    echo "[OK] Node.js: $(node --version)"
else
    echo "[FAIL] Cai dat Node.js that bai!"
    echo "  Thu: apk add nodejs"
    exit 1
fi

# Install build deps for Pillow
echo ">>> Cai dat build dependencies..."
apk add gcc musl-dev python3-dev jpeg-dev zlib-dev 2>/dev/null

# Install Python packages
echo ">>> Cai dat requests + Pillow..."
pip3 install --break-system-packages requests Pillow 2>/dev/null || pip3 install requests Pillow 2>/dev/null
echo "[OK] Python packages"

# Create symlink python -> python3 if needed
if ! command -v python >/dev/null 2>&1; then
    ln -sf "$(which python3)" /usr/local/bin/python 2>/dev/null
    echo "[OK] Tao symlink python -> python3"
fi

# Check files
echo ""
echo ">>> Kiem tra files..."
FILES_OK=true
for f in "flowborn_poster.py" "sign_bridge.js" "camp-security-oversea.0.1.0.js"; do
    if [ -f "$f" ]; then
        echo "[OK] $f"
    else
        echo "[FAIL] THIEU: $f"
        FILES_OK=false
    fi
done

echo ""
echo "═══════════════════════════════════════════"

if [ "$FILES_OK" = true ]; then
    echo "[OK] Setup hoan tat!"
    echo ""
    echo "  CACH SU DUNG:"
    echo "  1. Copy file .har vao thu muc nay"
    echo "  2. Copy anh/video vao thu muc nay"
    echo "  3. Chay: python3 flowborn_poster.py"
    echo ""
    echo "  Lay ma thiet bi: python3 flowborn_poster.py --device-id"
    echo "  Test sign bridge: python3 flowborn_poster.py --test-sign"
else
    echo "[FAIL] Thieu files! Vui long copy day du files."
fi
echo ""
