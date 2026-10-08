# Reserka Gothic — Godot starter port

Open `project.godot` in **Godot 4.3 or newer** (tested with 4.6.3), wait for asset imports, then press **F6** with `main.tscn` open or **F5** to play.

- A/D or arrows: move
- Space, W or Up: jump; press again for a double jump
- X or J: sword attack
- Escape: pause/resume
- R: restart

Defeat the five fire skulls and reach the golden gate on the right. Two sword hits defeat a skull. Contact costs health; you briefly become invulnerable after damage.

This standalone starter port includes a scrolling castle level, animated hero and enemies, physics platforms, double jump, sword combat, health, souls, pause, win/loss and restart. It does not include the Python game's complete world, character selection, progression, level editor, save files, audio, or Ultimate graphics effects. It uses native GDScript and requires no Python dependencies.

The level's platform and enemy layouts are in `scripts/main.gd`; player behavior is in `scripts/player.gd`; enemies are in `scripts/enemy.gd`. The main scene is `main.tscn`.

Validation:

```sh
godot --headless --path . --editor --import
godot --headless --path . --script tests/smoke.gd
```

Art is copied from the original Reserka repository's Gothicvania assets. Original asset licenses still apply; confirm redistribution rights before publishing. The project contains only the art needed for this starter level.

For a browser build, install the Godot export templates matching your editor version, add a Web export preset, and export to a static hosting service. This archive is an editable Godot project, not a hosted browser game.
