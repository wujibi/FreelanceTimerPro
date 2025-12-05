#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}          Time Tracker App Launcher${NC}"
echo -e "${BLUE}================================================${NC}"
echo

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Python is available
if command_exists python3; then
    PYTHON_CMD="python3"
elif command_exists python; then
    PYTHON_CMD="python"
else
    echo -e "${RED}ERROR: Python is not installed or not in PATH${NC}"
    echo "Please install Python 3.x and try again"
    read -p "Press Enter to exit..."
    exit 1
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo -e "${RED}ERROR: main.py not found in current directory${NC}"
    echo "Current directory: $(pwd)"
    read -p "Press Enter to exit..."
    exit 1
fi

# Display Python version
echo -e "${GREEN}Using Python: $($PYTHON_CMD --version)${NC}"
echo -e "${YELLOW}Starting Time Tracker App...${NC}"
echo

# Launch the application
$PYTHON_CMD main.py

# Check exit status
if [ $? -ne 0 ]; then
    echo
    echo -e "${RED}Application exited with an error${NC}"
    read -p "Press Enter to exit..."
fi
