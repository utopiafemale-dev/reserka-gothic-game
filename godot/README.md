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

## 2.5D and co-op edition

The default startup scene is `three_d/boot.tscn`: character selection, solo play,
co-op host/join and a loading screen. The scenery uses eight original procedural
GLB models; characters stay animated sprites in a real 3D world. Distant scenery
retains the existing illustrations. This is not a full conversion to rigged 3D
characters. Gothic Knight and Adventurer are distinct sprite designs; Spectral
and Crimson are knight color variants, with the same abilities.

Edit `three_d/gameplay.tres` in the Godot Inspector to tune movement, gravity,
jump counts, health, sword damage, enemy behavior and camera settings. Stage
layouts remain in `scripts/levels.gd`. Open `main.tscn` for the original 2D game.
Original 3D models can be rebuilt with Blender using `tools/build_3d_models.py`.

Desktop co-op supports eight players total using an authoritative ENet host.
Each device picks its own character. Join using the host's reachable address and
UDP port (default 24567). Across the internet the host needs suitable firewall
and router forwarding. The host controls pause, retry and stage progression.
Partners revive after six seconds if another player survives; everyone falling
ends the stage. Host disconnect ends the session; there is no host migration.

## Browser edition and hosting

The repository's `web/` contains the Godot 4.6.3 single-threaded WebGL2 export.
Browser co-op uses WebSockets and a separate authoritative server for each room.
Create a room, share its six-character code, and friends join from the same site.
The first player controls pause, retry and stage progression; leadership passes
to a remaining player when they leave. Rooms support two through eight players,
with at most eight simultaneous rooms per server. Empty rooms expire after
20 minutes. There are no accounts, passwords, matchmaking or saved progress.
Keep room codes private if you only want friends to join.

Run from the repository root with Python 3.12+, Godot 4.6.3 and dependencies:

```sh
pip install -r server/requirements.txt
godot --headless --path godot --editor --import
python server/app.py
```

Deploy the root Dockerfile on a container host supporting persistent WebSockets.
Set `PORT` if required by the host; default is 8080. Serve it through HTTPS so
browser clients use WSS. This same service serves both the game and room API.
A static-only Sites upload can run solo but cannot provide room multiplayer.
No public hosting has been configured in this repository.

To rebuild the browser export, install the matching official Godot export
templates, then run `godot --headless --path godot --export-release Web`.
Desktop network validation: `python godot/tools/run_network_tests.py`.

Validation in this cloud environment: 42 3D gameplay checks, four actual-physics
stage traversals, 11 startup/loading checks, 59 legacy campaign/audio checks,
68 desktop ENet checks, and eight WebSocket client checks passed. Two actual
Chromium sessions created/joined the same room without console errors after
WebSocket flow control was added. Public internet
latency and mobile touch controls are not tested; play uses a keyboard. The Docker
build could not download Debian packages through this environment’s container
network, so container deployment remains unverified.
