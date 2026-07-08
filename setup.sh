#!/data/data/com.termux/files/usr/bin/sh
# ============================================
#  Flowborn Poster Tool - Setup Script
#  by hienmods (Termux - Android)
# ============================================

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  Flowborn Poster Tool - Auto Setup       ║"
echo "║  by hienmods                             ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Check Termux
if [ ! -d "/data/data/com.termux" ]; then
    echo "[!] Khong phat hien Termux."
    echo "[!] Neu ban dung iSH (iOS), chay: sh setup_ish.sh"
    exit 1
fi

# Update packages
echo ">  Cap nhat package..."
pkg update -y > /dev/null 2>&1

# Install Python
echo ">  Cai dat Python..."
pkg install -y python > /dev/null 2>&1
if command -v python > /dev/null 2>&1; then
    echo "[OK] Python: $(python --version 2>&1)"
else
    echo "[FAIL] Cai dat Python that bai!"
    exit 1
fi

# Install Node.js (for sign bridge)
echo ">  Cai dat Node.js..."
pkg install -y nodejs > /dev/null 2>&1
if command -v node > /dev/null 2>&1; then
    echo "[OK] Node.js: $(node --version)"
else
    echo "[!] Node.js khong cai duoc (khong bat buoc)"
fi

# Install Python packages
echo ">  Cai dat requests..."
pip install requests > /dev/null 2>&1
if python -c "import requests" > /dev/null 2>&1; then
    echo "[OK] requests"
else
    echo "[FAIL] Khong cai duoc requests!"
    exit 1
fi

echo ">  Cai dat Pillow (can thu vien anh)..."
pkg install -y libjpeg-turbo libpng zlib freetype > /dev/null 2>&1
LDFLAGS="-L/data/data/com.termux/files/usr/lib" \
CFLAGS="-I/data/data/com.termux/files/usr/include" \
pip install Pillow > /dev/null 2>&1
if python -c "from PIL import Image" > /dev/null 2>&1; then
    echo "[OK] Pillow"
else
    # Retry with --no-cache-dir
    echo ">  Thu lai Pillow (no-cache)..."
    pip install --no-cache-dir Pillow > /dev/null 2>&1
    if python -c "from PIL import Image" > /dev/null 2>&1; then
        echo "[OK] Pillow"
    else
        echo "[FAIL] Pillow khong cai duoc!"
        echo "  Thu chay thu cong:"
        echo "    pkg install libjpeg-turbo libpng zlib freetype"
        echo "    pip install --no-cache-dir Pillow"
    fi
fi

# Check files
echo ""
echo ">  Kiem tra files..."
FILES_OK=true
for f in "flowborn_poster.py" "loadtran.py" "sign_bridge.js" "camp-security-oversea.0.1.0.js"; do
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

    # Tao lenh tat 'flb' va 'lt'
    TOOL_DIR="$(pwd)"
    
    FLB_PATH="$PREFIX/bin/flb"
    printf '#!/data/data/com.termux/files/usr/bin/sh\ncd "%s" && exec python flowborn_poster.py "$@"\n' "$TOOL_DIR" > "$FLB_PATH"
    chmod +x "$FLB_PATH"
    echo "[OK] Lenh tat 'flb' (Flowborn Poster)"

    LT_PATH="$PREFIX/bin/lt"
    printf '#!/data/data/com.termux/files/usr/bin/sh\ncd "%s" && exec python loadtran.py "$@"\n' "$TOOL_DIR" > "$LT_PATH"
    chmod +x "$LT_PATH"
    echo "[OK] Lenh tat 'lt' (Load Tran)"

    echo ""
    echo "  CACH SU DUNG:"
    echo "  1. Copy file .har vao thu muc nay"
    echo "  2. Copy anh/video vao thu muc nay"
    echo "  3. Chay: flb (Flowborn) hoac lt (Load Tran)"
    echo ""
    echo "  Cac lenh:"
    echo "    flb              — Chay Flowborn Poster"
    echo "    lt               — Chay Load Tran"
    echo "    flb --device-id  — Xem ma thiet bi"
    echo "    flb --test-sign  — Test sign bridge"
else
    echo "[FAIL] Thieu files! Vui long copy day du files."
fi
echo ""
