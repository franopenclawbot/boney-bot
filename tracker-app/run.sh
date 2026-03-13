#!/bin/bash
# Run the product tracker
cd "$(dirname "$0")"
source venv/bin/activate
python3 tracker.py
