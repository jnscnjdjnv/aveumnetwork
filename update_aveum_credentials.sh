#!/bin/bash

echo "Aveum Credentials Update Tool"
echo "==========================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed or not in PATH."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found."
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Run the update script
echo
echo "Running Aveum Credentials Update Tool..."
python update_aveum_credentials.py

# Deactivate virtual environment
deactivate

echo
read -p "Press Enter to continue..." 