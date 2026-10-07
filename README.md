# KAGE — Shadows Remember

KAGE is a playable browser prototype for a real-time, 2–8 player psychological survival-horror RPG. Lost travelers wake outside a mythical feudal Japanese village. The countryside is beautiful, the shared campfire is warm, and each traveler has brought a different wrongness with them.

The original Python/Pygame experiments remain in `src/`; the production prototype is the new web application in `web/`.

## Play locally

```bash
npm install
npm run dev
```

Open the printed URL. Without backend configuration, rooms use `BroadcastChannel`, so Create/Join works across tabs on the same browser. Use **WASD / arrow keys** to move, **E / Enter / A** to interact, and **Escape / B** to cancel. Touch devices get a D-pad and A/B controls.

```bash
npm test        # system tests
npm run build   # type-check and production build
npm run preview # preview dist/
```

## Architecture

- **Canvas renderer:** fixed 32px logical tile grid, pixel-perfect scaling, separate connected region maps.
- **Authoritative realtime:** PartyKit validates joins, logical one-tile moves, damage, disconnects, and shared event promotion. Clients interpolate/display logical state rather than streaming frames.
- **Offline/local transport:** `BroadcastChannel` provides a no-setup multi-tab development fallback.
- **Systems:** data-driven identities, group trial choices, room clock, scheduled NPCs, private/shared horror events, death/corruption, campfire decisions, and local character persistence.
- **Persistence:** character progress stays on-device in `localStorage`; live rooms are intentionally ephemeral.

## Multiplayer backend

1. Sign in to PartyKit (`npx partykit login`) and run `npm run party:deploy`.
2. Set the frontend environment variable to the resulting host (no protocol):

```bash
VITE_PARTYKIT_HOST=kage-reality.your-name.partykit.dev
```

For local network testing, run `npm run party:dev` and set `VITE_PARTYKIT_HOST=localhost:1999`. No secrets are exposed: the host is public configuration and server authority lives in `party/server.ts`.

## Deploy

Vercel and Netlify configuration files are included. Connect the repository, add `VITE_PARTYKIT_HOST`, and deploy; both providers run `npm run build` and publish `dist`. The one external step is creating/deploying the PartyKit project under your own account.

## Current slice

- Title, four-letter Create/Join flow, responsive Canvas, desktop/touch controls
- Five connected regions: Hollow Village, Bamboo Path, River Valley, Mountain Shrine, Forbidden Woods
- Random persistent archetype/burden, virtue profile, memories, corruption and deaths
- Shared 20-minute day/dusk/night/dawn clock and changing NPC schedules
- NPC dialogue, private burden-based watcher, shared reality-bleed promotion
- Adaptive Wounded Guardian party trial and functional campfire truth/lie/silence choice
- Original programmatic pixel environment, subtle generated audio cue, mobile safe areas

## Known limitations / priorities

- Room existence is ephemeral; PartyKit currently permits joining a newly opened code and does not reserve codes globally.
- The vertical slice provides system depth but not the final 15–30 minutes of authored content.
- Improve movement interpolation, reconnect identity claims, server-side collision maps, accessibility options, procedural ambience, combat/ritual UI, and automated browser multiplayer tests next.
- Deploying PartyKit requires the project owner's external account; no credentials are committed.

All new artwork is drawn programmatically and is original. The web prototype does not use the legacy third-party Gothicvania assets.
