#!/bin/zsh

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Use the Python executable from the virtual environment in the same directory
PYTHON_PATH="$SCRIPT_DIR/.venv/bin/python"
MAIN_SCRIPT="$SCRIPT_DIR/main.py"

# Check if the Python executable exists
if [ ! -f "$PYTHON_PATH" ]; then
  echo "Python virtual environment not found at $PYTHON_PATH"
  exit 1
fi

# Check if the main script exists
if [ ! -f "$MAIN_SCRIPT" ]; then
  echo "Main script not found at $MAIN_SCRIPT"
  exit 1
fi

# Run the Python script
"$PYTHON_PATH" "$MAIN_SCRIPT" "$@"
