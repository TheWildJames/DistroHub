#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Function to install PyQt5 using apt
install_with_apt() {
  echo "Installing PyQt5 using apt..."
  sudo apt-get update
  sudo apt-get install -y python3-pyqt5
}

# Function to install PyQt5 using dnf
install_with_dnf() {
  echo "Installing PyQt5 using dnf..."
  sudo dnf install -y python3-qt5
}

# Function to install PyQt5 using pacman
install_with_pacman() {
  echo "Installing PyQt5 using pacman..."
  sudo pacman -S --noconfirm python-pyqt5
}

# Check if PyQt5 is installed and install it if necessary
if ! python3 -c "import PyQt5" > /dev/null 2>&1; then
  if command -v apt > /dev/null 2>&1; then
    install_with_apt
  elif command -v dnf > /dev/null 2>&1; then
    install_with_dnf
  elif command -v pacman > /dev/null 2>&1; then
    install_with_pacman
  else
    echo "Could not detect package manager. Please install PyQt5 manually."
    exit 1
  fi
fi

sudo chmod +x "$SCRIPT_DIR/Start-DistroHub.sh"
sudo chmod +x "$SCRIPT_DIR/DistroHub.py"

# Start the DistroHub application
python3 "$SCRIPT_DIR/DistroHub.py"
 
