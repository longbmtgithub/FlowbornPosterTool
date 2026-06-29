#!/bin/bash
pip install requests Pillow -q 2>/dev/null
python3 flowborn_poster.py "$@"
