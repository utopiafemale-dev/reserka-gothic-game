# Reserka Gothic — Godot campaign

Open `project.godot` in **Godot 4.3 or newer** (tested with 4.6.3), wait for asset imports, then press **F5** to play. No Python installation is needed.

## Controls

- A/D or arrows: move
- Space, W or Up: jump; press again for a double jump
- X or J: sword attack
- Escape: pause/resume
- Enter: continue after clearing a stage
- R: retry the current stage; after campaign victory, start a new journey
- M: mute/unmute all audio
- `[` / `]`: decrease/increase music volume

## Four-stage campaign

1. **The Castle Approach** — introduction to flying skulls, hounds, and heavy demons.
2. **The Drowned Swamp** — forest scenery, charging hounds, spike hazards, and elevated routes.
3. **The Hollow Caverns** — cave scenery, jumpable floor gaps, spikes, and mixed encounters.
4. **The Moonlit Graveyard** — tougher encounters and a 250-health warden boss that accelerates below half health.

Defeat every enemy to unlock each stage's golden gate, then walk to it. Press Enter on the cleared-stage screen to advance. Health resets to 100 on each new stage. Green cross pickups restore 30 health and remain available while you are at full health. Falling into a cavern gap kills the player; spikes deal damage with temporary invulnerability. Raised platforms allow jumping through from below.

Skulls fly toward you; hounds charge; demons stop and telegraph a heavier close-range strike. The warden has a larger strike radius. Watch for the orange attack warning and jump away. Enemy health bars appear after damage; the boss bar is always visible. Sword attacks deal 25 damage, at most once to each enemy per swing.

## Generated art and audio

The final stage uses an AI-generated moonlit graveyard background (`assets/graveyard.png`). It is new artwork, not an itch.io download.

Includes three looping music tracks and seven effects: jump, sword, hurt, healing pickup, enemy defeat, death, and stage clear. Effects use separate playback voices so they can overlap. Music starts at a reduced volume. Audio settings last for the current run, including level transitions and retries; they are not saved to disk. Music continues during pause.

All ten audio assets are original procedural synthesis with no third-party samples. Recreate them with `python3 tools/generate_audio.py`. They replace the earlier copied music/effects whose complete license provenance was not verified. See `assets/audio/SOURCES.md` for details. Existing Gothicvania art still follows the original collection license; the new graveyard image was created with the connected image-generation tool.

## Editing

- `scripts/levels.gd`: stage names, dimensions, platform layouts, backgrounds, enemies, hazards, healing pickups and music. Enemy coordinates are their feet; skulls float above their coordinates.
- `scripts/main.gd`: stage progression, UI, platform construction, pickups, hazards and scenery.
- `scripts/player.gd`: movement, double jump, combat and health.
- `scripts/enemy.gd`: enemy variants and boss behavior.
- `scripts/audio.gd`: track/effect routing, volume and mute controls.

The game uses a single `main.tscn` with stage data loaded at runtime. This is an expanded native GDScript port; it does not include the Python game's character selection, full world/progression system, visual level editor, save system or Ultimate post-processing.

## Validation

```sh
godot --headless --path . --editor --import
godot --headless --path . --script tests/smoke.gd
godot --headless --path . --script tests/campaign.gd
godot --headless --path . --script tests/enemies.gd
godot --headless --path . --script tests/traversal.gd
```

Smoke checks cover core controls and combat. Campaign checks exercise all four stage transitions, locked gates, healing, hazard damage, audio decoding/playback controls, boss health, victory and retries. Enemy checks cover charging, telegraphs, strikes and boss phase speed. Traversal checks use movement and double jump to reach every gate with combat and hazard damage isolated. Headless audio checks verify decoding and playback state, not audible mix quality.

In a sandbox where your normal user directories are read-only, set `XDG_DATA_HOME`, `XDG_CONFIG_HOME`, and `XDG_CACHE_HOME` to writable directories before running Godot.

For a browser build, install Godot export templates matching your editor version, add a Web export preset, and export to a static hosting service. This is an editable Godot project, not a hosted browser game.
