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

# Install Python3 + packages (pre-compiled, KHONG can build)
echo ">>> Cai dat Python3 + packages..."
apk add python3 py3-pip py3-pillow py3-requests 2>/dev/null

# Install js2py for Python sign bridge (khong can Node.js!)
echo ">>> Cai dat js2py (Python sign bridge)..."
pip3 install --break-system-packages js2py 2>/dev/null || pip3 install js2py 2>/dev/null

if command -v python3 >/dev/null 2>&1; then
    echo "[OK] Python3: $(python3 --version 2>&1)"
else
    echo "[FAIL] Cai dat Python3 that bai!"
    exit 1
fi

# Install Node.js
echo ">>> Cai dat Node.js..."
apk add nodejs 2>/dev/null
if command -v node >/dev/null 2>&1; then
    echo "[OK] Node.js: $(node --version)"
else
    echo "[FAIL] Cai dat Node.js that bai!"
    exit 1
fi

# Kiem tra requests co chua (neu apk khong co thi pip)
python3 -c "import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ">>> Cai requests qua pip..."
    pip3 install --break-system-packages requests 2>/dev/null || pip3 install requests 2>/dev/null
fi
echo "[OK] Python packages"

# Create symlink python -> python3
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

    # Tao lenh tat 'flb'
    TOOL_DIR="$(pwd)"
    echo "#!/bin/sh" > /usr/local/bin/flb
    echo "cd \"$TOOL_DIR\" && exec python3 flowborn_poster.py \"\$@\"" >> /usr/local/bin/flb
    chmod +x /usr/local/bin/flb
    echo "[OK] Lenh tat 'flb' da duoc tao!"

    echo ""
    echo "  CACH SU DUNG:"
    echo "  1. Copy file .har vao thu muc nay"
    echo "  2. Copy anh/video vao thu muc nay"
    echo "  3. Chay: flb"
    echo ""
    echo "  flb              — Chay tool"
    echo "  flb --device-id  — Xem ma thiet bi"
    echo "  flb --test-sign  — Test sign bridge"
else
    echo "[FAIL] Thieu files! Vui long copy day du files."
fi
echo ""
