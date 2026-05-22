# 🏰 Reserka - Gothic Edition

A dark fantasy action-platformer game inspired by classic Metroidvania titles, featuring stunning Gothicvania pixel art assets and atmospheric gothic horror gameplay.

![Reserka Gothic](https://img.shields.io/badge/Reserka-Gothic%20Edition-gold?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Pygame](https://img.shields.io/badge/Pygame-2.5+-green?style=for-the-badge)

## 🌟 Features

### 🎮 Core Gameplay
- **Metroidvania-style Exploration**: Navigate gothic castles and dark environments
- **Fluid Combat System**: Attack enemies with combo moves and special abilities
- **Double Jump Mechanics**: Enhanced platforming with double jump capability
- **Progressive Difficulty**: Enemies get stronger as you advance
- **Soul Collection System**: Defeat enemies to collect souls (in-game currency)

### 🎨 Visual Style
- **Authentic Gothicvania Assets**: High-quality pixel art sprites and animations
- **Atmospheric Environments**: Dark castles, horror towns, and mysterious backgrounds  
- **Animated Characters**: Smooth sprite animations for hero, enemies, and effects
- **Gothic Horror Theme**: Demons, fire skulls, hell hounds, and otherworldly creatures

### 🛠️ Technical Features
- **Level Editor**: Create custom levels with visual editor
- **Asset Management**: Efficient loading and management of game assets
- **Modular Architecture**: Easy to extend with new enemies and mechanics
- **Save/Load System**: Level persistence and game state management

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone/Download the game**:
   ```bash
   cd reserka-gothic-game
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the game launcher**:
   ```bash
   python reserka_launcher.py
   ```

### Alternative: Direct Game Launch
```bash
# Launch main game directly
python src/reserka_gothic.py

# Launch level editor directly  
python src/level_editor.py
```


## 🧢 New Prototype: Pokémon-Style 2D Pixel RPG

A new playable prototype is included at `src/pixel_mon_rpg.py`. It focuses on classic monster-RPG flow:

- Top-down tile exploration
- Tall-grass random encounters
- Turn-based battle menu (Attack / Skill / Item / Run)
- Healer NPC and simple town interaction

Run it with:

```bash
python src/pixel_mon_rpg.py
```

Controls:
- Move: WASD / Arrow Keys
- Interact: E
- Battle select: W/S or Up/Down
- Confirm action: Enter or Space
- Quit: ESC

## 🎮 How to Play

### Controls
- **Movement**: WASD or Arrow Keys
- **Jump**: SPACE or W (double jump available)
- **Attack**: X or J
- **Pause**: ESC

### Game Mechanics
1. **Exploration**: Navigate through gothic castle environments
2. **Combat**: Attack enemies to defeat them and collect souls
3. **Platforming**: Use double jump to reach higher platforms
4. **Health Management**: Avoid enemy attacks to preserve health
5. **Soul Collection**: Gather souls from defeated enemies

### Enemy Types
- **Fire Skulls**: Fast-moving floating enemies with moderate health
- **Demons**: Powerful ground-based enemies with high damage
- **Hell Hounds**: Quick melee attackers with medium health

## 🛠️ Level Editor

The included level editor allows you to create custom levels with a visual interface.

### Editor Controls
- **1**: Platform Mode - Create platforms by dragging
- **2**: Enemy Mode - Place enemies (TAB to cycle types)
- **3**: Spawn Mode - Set player spawn point
- **4**: Erase Mode - Remove objects
- **G**: Toggle grid visibility
- **S**: Toggle snap to grid
- **Ctrl+S**: Save level
- **Ctrl+L**: Load level
- **Ctrl+C**: Clear level
- **Arrow Keys**: Move camera

### Creating Custom Levels
1. Launch the level editor from the main launcher
2. Use different modes to place platforms, enemies, and spawn points
3. Save your level with Ctrl+S
4. Load saved levels with Ctrl+L

## 📁 Project Structure

```
reserka-gothic-game/
├── src/
│   ├── reserka_gothic.py      # Main game engine
│   └── level_editor.py        # Visual level editor
├── assets/                    # Gothicvania art assets
│   ├── Gothic-hero-Files/     # Player animations
│   ├── demon-Files/           # Demon enemy sprites
│   ├── Fire-Skull-Files/      # Fire skull sprites
│   ├── Hell-Hound-Files/      # Hell hound sprites
│   ├── Gothic-Castle-Files/   # Environment art
│   └── Gothic-Horror-Files/   # Background assets
├── levels/                    # Custom level files
├── config/                    # Game configuration
├── reserka_launcher.py        # Game launcher
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## 🎨 Assets

This game uses the **Gothicvania Patreon Collection** assets, featuring:

- **Hero Sprites**: Idle, run, jump, attack, crouch, and special moves
- **Enemy Sprites**: Various demons, skulls, hounds, and creatures
- **Environment Art**: Castle backgrounds, tiles, and atmospheric elements
- **Horror Themes**: Dark, gothic aesthetic with detailed pixel art

## 🔧 Customization

### Adding New Enemies
1. Add sprite assets to the `assets/` directory
2. Update `AssetManager.load_enemy_animations()` to load new sprites
3. Create enemy type in the `Enemy` class
4. Add to level editor enemy types

### Modifying Game Balance
Edit constants in `reserka_gothic.py`:
- `PLAYER_SPEED`: Character movement speed
- `JUMP_STRENGTH`: Jump height
- `GRAVITY`: Fall speed
- Enemy health, damage, and speed values

### Custom Levels
Use the level editor to create new levels, or manually edit JSON files in the `levels/` directory.

## 🐛 Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```bash
   pip install pygame Pillow
   ```

2. **Asset Loading Errors**
   - Ensure all assets are in the `assets/` directory
   - Check file paths and permissions

3. **Performance Issues**
   - Reduce screen resolution in game settings
   - Lower the number of enemies in custom levels

4. **Controls Not Working**
   - Make sure the game window has focus
   - Try alternative control schemes (WASD vs Arrow keys)

## 🎯 Game Design

### Core Loop
1. **Explore** gothic environments
2. **Fight** demonic enemies  
3. **Collect** souls and power-ups
4. **Progress** through increasingly difficult areas
5. **Master** platforming and combat skills

### Difficulty Progression
- **Early Game**: Basic platforming with simple enemies
- **Mid Game**: Complex level layouts with mixed enemy types
- **Late Game**: Challenging combat encounters and precision platforming


## 🤖 AI Virtual World Business Concept

If you want to build a "virtual world for AI" with a real-world profit bridge, see:

- `docs/ai_virtual_world_business_loop.md`

This concept proposes an agent economy, auditable profit ledger, and a controlled payout pipeline to send approved earnings to real-world accounts.

## 🚧 Future Enhancements

### Planned Features
- **Sound Effects**: Gothic audio atmosphere and combat sounds
- **Music**: Dark orchestral soundtrack
- **Power-ups**: Special abilities and equipment upgrades
- **Multiple Levels**: Expanded world with different environments
- **Boss Battles**: Epic encounters with powerful demons
- **Inventory System**: Collectible items and upgrades
- **Story Mode**: Narrative elements and character progression

### Technical Improvements
- **Performance Optimization**: Better asset caching and rendering
- **Mobile Support**: Touch controls and mobile-friendly UI
- **Online Features**: Level sharing and leaderboards
- **Mod Support**: Plugin system for community content

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- New enemy types and behaviors
- Additional level mechanics
- UI/UX enhancements
- Performance optimizations
- Bug fixes and testing

## 📄 License

This game code is open source. The Gothicvania assets are used under their respective licenses.

## 🎮 Credits

- **Game Engine**: Python + Pygame
- **Art Assets**: Gothicvania Patreon Collection
- **Game Design**: Classic Metroidvania inspiration
- **Development**: Built with passion for gothic horror gaming

---

**Experience the dark fantasy world of Reserka - Gothic Edition!** 🏰⚔️

Explore haunted castles, battle demonic creatures, and master the art of gothic platforming in this atmospheric action game.
