#!/bin/bash
# Flowborn Poster Tool - Auto Setup for Cloud Shell
cd ~
if [ ! -d "FlowbornPosterTool" ]; then
  git clone https://github.com/longbmtgithub/FlowbornPosterTool.git
fi
cd FlowbornPosterTool
pip install requests Pillow -q 2>/dev/null
echo ""
echo "=================================="
echo "  SAN SANG! Copy file .har vao day"
echo "  roi chay: python3 flowborn_poster.py"
echo "=================================="
echo ""
ls -la *.har 2>/dev/null || echo "(Chua co file .har - upload vao day)"
