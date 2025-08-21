#!/bin/bash

echo "🔧 Testing Reserka Gothic Ultimate Installation..."
echo "================================================="

# Test 1: Check desktop launcher exists
echo "📍 Checking Desktop Launcher..."
if [ -f ~/Desktop/Reserka\ Gothic.command ]; then
    echo "✅ Desktop launcher found: ~/Desktop/Reserka Gothic.command"
else
    echo "❌ Desktop launcher not found"
fi

# Test 2: Check installed version
echo ""
echo "📍 Checking Installed Version..."
if [ -d ~/Applications/ReserkaGothic ]; then
    echo "✅ Game installed at: ~/Applications/ReserkaGothic"
    if [ -f ~/Applications/ReserkaGothic/launch_game.sh ]; then
        echo "✅ Launcher script found"
    else
        echo "❌ Launcher script missing"
    fi
else
    echo "❌ Game installation not found"
fi

# Test 3: Check current directory version
echo ""
echo "📍 Checking Current Directory Version..."
if [ -f src/reserka_gothic_ultimate.py ]; then
    echo "✅ Game source found in current directory"
    if [ -f play_game.sh ]; then
        echo "✅ Quick launcher found"
    fi
else
    echo "❌ Game source not found in current directory"
fi

# Test 4: Check Python and pygame
echo ""
echo "📍 Checking Dependencies..."
if command -v python3 &> /dev/null; then
    echo "✅ Python 3 found: $(python3 --version)"
else
    echo "❌ Python 3 not found"
fi

if python3 -c "import pygame" &> /dev/null; then
    echo "✅ pygame library available"
else
    echo "❌ pygame library missing"
fi

echo ""
echo "🎮 HOW TO PLAY:"
echo "================================================="
echo "✨ Option 1 (Easiest): Double-click 'Reserka Gothic.command' on Desktop"
echo "✨ Option 2: Run: ~/Applications/ReserkaGothic/launch_game.sh"
echo "✨ Option 3: Run: ./play_game.sh (from this directory)"
echo "✨ Option 4: Run: python3 src/reserka_gothic_ultimate.py"
echo ""
echo "🎮 Game Controls:"
echo "   WASD/Arrows = Move"
echo "   SPACE = Jump (multi-jump!)"
echo "   X = Attack" 
echo "   Z = Dash (Female Adventurer)"
echo "   E = Interact with doors"
echo "   ESC = Pause menu"
echo ""
echo "Ready to play! 🔥"
