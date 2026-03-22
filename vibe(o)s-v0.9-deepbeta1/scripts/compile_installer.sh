#!/usr/bin/env bash
# ==============================================================================
# ArchForge - Python Installer Compiler Script
# Description: Compiles the CustomTkinter Python GUI into a standalone binary.
# ==============================================================================

set -euo pipefail

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}[INFO]${NC} Preparing to compile ArchForge GUI Installer..."

# Ensure we are in the project root
cd "$(dirname "$0")/.."

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} PyInstaller is not installed. Run: pip install pyinstaller"
    exit 1
fi

# Create dummy main.py if it doesn't exist yet (for initial CI/CD run)
mkdir -p installer
if [ ! -f installer/main.py ]; then
    echo -e "${BLUE}[INFO]${NC} Creating placeholder installer/main.py for initial compilation..."
    cat << 'EOF' > installer/main.py
import customtkinter as ctk
def main():
    app = ctk.CTk()
    app.title("ArchForge Installer")
    app.geometry("800x600")
    ctk.CTkLabel(app, text="ArchForge Installer Bootstrapped!").pack(expand=True)
    app.mainloop()
if __name__ == "__main__":
    main()
EOF
fi

echo -e "${BLUE}[INFO]${NC} Running PyInstaller..."

# Compile the installer
# --noconfirm: Overwrite existing build/dist
# --onedir: Create a directory containing the executable and libraries (faster startup than onefile)
# --windowed: Don't open a console window (GUI only)
# --add-data: Include CustomTkinter assets
pyinstaller --noconfirm \
            --onedir \
            --windowed \
            --name "archforge-installer" \
            --add-data "$(python3 -c 'import customtkinter; import os; print(os.path.dirname(customtkinter.__file__))'):customtkinter/" \
            installer/main.py

echo -e "${GREEN}[SUCCESS]${NC} Compilation complete! Binary is located in ./dist/archforge-installer/"
