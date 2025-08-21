#!/bin/bash

# Reserka Gothic - Ultimate Enhanced Edition Installation Script
# For macOS systems

echo "🎮 Installing Reserka Gothic - Ultimate Enhanced Edition..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Game information
GAME_NAME="Reserka Gothic Ultimate"
GAME_VERSION="v2.1.0"
INSTALL_DIR="$HOME/Applications/ReserkaGothic"
DESKTOP_FILE="$HOME/Desktop/Reserka Gothic.command"

echo -e "${CYAN}Installing: ${GAME_NAME} ${GAME_VERSION}${NC}"
echo -e "${BLUE}Installation Directory: ${INSTALL_DIR}${NC}"
echo ""

# Check Python installation
echo -e "${YELLOW}🔍 Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Found: ${PYTHON_VERSION}${NC}"
else
    echo -e "${RED}❌ Python 3 not found!${NC}"
    echo -e "${YELLOW}Please install Python 3 from: https://www.python.org/downloads/${NC}"
    exit 1
fi

# Check pygame installation
echo -e "${YELLOW}🔍 Checking pygame installation...${NC}"
if python3 -c "import pygame" &> /dev/null; then
    PYGAME_VERSION=$(python3 -c "import pygame; print(f'pygame {pygame.version.ver}')")
    echo -e "${GREEN}✓ Found: ${PYGAME_VERSION}${NC}"
else
    echo -e "${YELLOW}⚠️  pygame not found. Installing...${NC}"
    pip3 install pygame numpy
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ pygame installed successfully${NC}"
    else
        echo -e "${RED}❌ Failed to install pygame${NC}"
        exit 1
    fi
fi

# Create installation directory
echo -e "${YELLOW}📁 Creating installation directory...${NC}"
mkdir -p "$INSTALL_DIR"
echo -e "${GREEN}✓ Created: ${INSTALL_DIR}${NC}"

# Copy game files
echo -e "${YELLOW}📦 Installing game files...${NC}"
cp -r * "$INSTALL_DIR/"
echo -e "${GREEN}✓ Game files installed${NC}"

# Make scripts executable
chmod +x "$INSTALL_DIR"/*.sh
chmod +x "$INSTALL_DIR"/src/*.py

# Create desktop launcher
echo -e "${YELLOW}🖥️  Creating desktop launcher...${NC}"
cat > "$DESKTOP_FILE" << EOF
#!/bin/bash
# Reserka Gothic Ultimate - Desktop Launcher

cd "$INSTALL_DIR"
echo "🎮 Starting Reserka Gothic Ultimate..."
echo "🔥 Enhanced with pixel art and advanced graphics!"
echo ""
python3 src/reserka_gothic_ultimate.py
echo ""
echo "👋 Thanks for playing!"
read -p "Press Enter to close..."
EOF

chmod +x "$DESKTOP_FILE"
echo -e "${GREEN}✓ Desktop launcher created${NC}"

# Create Applications folder launcher (for Finder)
APPS_DIR="$HOME/Applications"
mkdir -p "$APPS_DIR"
ln -sf "$INSTALL_DIR" "$APPS_DIR/Reserka Gothic Ultimate"

# Create game launcher script
echo -e "${YELLOW}🚀 Creating game launcher...${NC}"
cat > "$INSTALL_DIR/launch_game.sh" << 'EOF'
#!/bin/bash

# Reserka Gothic Ultimate - Game Launcher
# Enhanced Edition with Pixel Art Integration

echo "🎮✨ Reserka Gothic - Ultimate Enhanced Edition ✨🎮"
echo "=================================================="
echo "🔥 Features:"
echo "   • Advanced Graphics Enhancement System"
echo "   • Dynamic Lighting & Atmospheric Effects" 
echo "   • Multi-character Support (2 playable characters)"
echo "   • Enhanced Menu System with Settings"
echo "   • Pixel Art Integration & Parallax Backgrounds"
echo "   • Professional Audio & Visual Effects"
echo "   • Level System & Character Progression"
echo "=================================================="
echo ""

# Change to game directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Check dependencies
echo "🔍 Checking game requirements..."
if ! python3 -c "import pygame, numpy" &> /dev/null; then
    echo "❌ Missing dependencies! Please run install_game.sh first."
    exit 1
fi
echo "✅ All requirements satisfied"
echo ""

# Launch game
echo "🚀 Launching game..."
echo "🎮 Controls: WASD/Arrows=Move, SPACE=Jump, X=Attack, Z=Dash, E=Door, ESC=Pause"
echo "🔧 Press F1 for FPS display, F11 for fullscreen"
echo ""

python3 src/reserka_gothic_ultimate.py

echo ""
echo "👋 Game session ended. Thanks for playing Reserka Gothic Ultimate!"
EOF

chmod +x "$INSTALL_DIR/launch_game.sh"
echo -e "${GREEN}✓ Game launcher created${NC}"

# Create uninstaller
echo -e "${YELLOW}🗑️  Creating uninstaller...${NC}"
cat > "$INSTALL_DIR/uninstall.sh" << EOF
#!/bin/bash
echo "🗑️ Uninstalling Reserka Gothic Ultimate..."
echo "This will remove the game from your system."
read -p "Are you sure? (y/N): " confirm
if [[ \$confirm == [yY] || \$confirm == [yY][eE][sS] ]]; then
    rm -rf "$INSTALL_DIR"
    rm -f "$DESKTOP_FILE"
    rm -f "$HOME/Applications/Reserka Gothic Ultimate"
    echo "✅ Reserka Gothic Ultimate has been uninstalled."
else
    echo "❌ Uninstall cancelled."
fi
EOF

chmod +x "$INSTALL_DIR/uninstall.sh"
echo -e "${GREEN}✓ Uninstaller created${NC}"

# Create README for installation
cat > "$INSTALL_DIR/README_INSTALLATION.md" << EOF
# Reserka Gothic - Ultimate Enhanced Edition
## Installation Complete! 🎮✨

### Game Features:
- **Advanced Graphics Enhancement System** with dynamic lighting
- **2 Playable Characters**: Gothicvania Hero & Female Adventurer
- **Enhanced Menu System** with pause menu and settings
- **Pixel Art Integration** with multi-layer parallax backgrounds
- **Professional Audio & Visual Effects**
- **Level Progression System** with experience and souls
- **Enhanced Combat System** with particle effects

### How to Play:
1. **Double-click** the "Reserka Gothic.command" file on your Desktop
2. **Or** run: \`$INSTALL_DIR/launch_game.sh\`
3. **Or** navigate to Applications folder and open "Reserka Gothic Ultimate"

### Controls:
- **Movement**: WASD or Arrow Keys
- **Jump**: SPACE (double/triple jump available)
- **Attack**: X key
- **Dash**: Z key (Female Adventurer only)
- **Interact**: E key (doors)
- **Pause**: ESC key
- **Settings**: Access through pause menu
- **FPS Display**: F1 key
- **Fullscreen**: F11 key

### System Requirements:
- macOS (any modern version)
- Python 3.6+
- pygame library
- 4GB RAM recommended
- OpenGL support for graphics enhancement

### Troubleshooting:
If you encounter issues:
1. Make sure Python 3 is installed
2. Ensure pygame is installed: \`pip3 install pygame numpy\`
3. Check file permissions: \`chmod +x launch_game.sh\`
4. Run from Terminal for error messages

### Uninstalling:
Run the uninstall script: \`$INSTALL_DIR/uninstall.sh\`

Enjoy the ultimate gothic gaming experience! 🔥
EOF

# Final installation summary
echo ""
echo -e "${PURPLE}=================================================="
echo -e "🎉 INSTALLATION COMPLETE! 🎉"
echo -e "==================================================${NC}"
echo -e "${GREEN}✅ Reserka Gothic Ultimate has been installed successfully!${NC}"
echo ""
echo -e "${CYAN}📍 Installation Location:${NC}"
echo -e "   ${INSTALL_DIR}"
echo ""
echo -e "${CYAN}🚀 How to Start Playing:${NC}"
echo -e "${YELLOW}   Option 1:${NC} Double-click 'Reserka Gothic.command' on your Desktop"
echo -e "${YELLOW}   Option 2:${NC} Run: $INSTALL_DIR/launch_game.sh"
echo -e "${YELLOW}   Option 3:${NC} Open 'Reserka Gothic Ultimate' from Applications folder"
echo ""
echo -e "${CYAN}🎮 Game Features:${NC}"
echo -e "   • Advanced Graphics Enhancement System"
echo -e "   • Dynamic Lighting & Atmospheric Effects"
echo -e "   • 2 Playable Characters with unique abilities"
echo -e "   • Enhanced Menu System with Settings"
echo -e "   • Pixel Art Integration & Parallax Backgrounds"
echo -e "   • Professional Audio & Visual Effects"
echo ""
echo -e "${GREEN}Ready to play! Have fun! 🔥${NC}"
echo ""
