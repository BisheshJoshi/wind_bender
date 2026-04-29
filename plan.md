# Project Plan: Airbender Spires (working title)

## Project Brief

A single-level 3D platformer built in Godot, inspired by **Sonic Robo Blast 2** (fan-made 3D Sonic game) but reimagined in the world of *Avatar: The Last Airbender*. The player controls Aang and uses airbending as movement primitives — not combat — to traverse a vertical level set in an Air Temple spire complex.

This is a **hackathon project** (retro-remixed game theme) being built by a developer with no prior Godot experience. Scope discipline is the single most important constraint. The target is a polished vertical slice, not a feature-complete game.

## Core Design Pillars

1. **Movement is the verb.** Like classic Sonic, the joy is in flowing through the level, not fighting enemies. Every mechanic serves traversal.
2. **One character, one bending style.** Aang, airbending only. No fire/water/earth. No combat NPCs in the MVP.
3. **One level, done well.** Air Temple spires — vertical, glide-heavy, with wind currents as boost pads. A short tutorial section precedes it.
4. **Retro feel, modern controls.** Genesis-era spirit (speed, momentum, secrets) with smooth 3D platforming controls.

## Scope (Hard Boundaries)

### In Scope
- Single playable character: Aang
- One main level: Air Temple Spires (vertical platformer)
- One tutorial area: teaches each movement mechanic in isolation before the main level
- Four movement mechanics (see below)
- Wind current boost pads as level elements
- Basic collectibles (something simple — air scrolls, sky bison statues, etc.) to reward exploration
- Start screen, pause menu, level-complete screen
- Placeholder/free-asset art and audio — visual polish is bonus, not core

### Explicitly Out of Scope (do not implement unless core scope is finished)
- Combat or enemies
- Other bending styles (firebending, waterbending, earthbending)
- Other characters (Korra, Katara, etc.)
- Multiple levels or hub world
- Story cutscenes or dialogue beyond minimal tutorial text
- Multiplayer, save systems beyond a simple "level complete" flag
- Custom 3D modeling — use free assets (Kenney, Quaternius, Mixamo, etc.) or simple primitives
- Voice acting, original music composition

**If a feature is not on the In Scope list, the default answer is no.**

## Movement Mechanics (the four verbs)

These are the only abilities Aang has. Everything else in the level is built around them.

### 1. Air Scooter (Spin Dash equivalent)
- Hold a button to charge a ball of air under Aang
- Release to rocket forward at high speed along the ground
- Speed decays over time unless on a downhill slope or boost pad
- Steerable but with momentum — turning is sluggish at high speed
- Sonic-style: should feel *fast* and *fun* before it feels balanced

### 2. Air Jump / Glide
- Standard jump, plus a double jump in mid-air
- Holding the jump button while falling deploys Aang's staff-glider
- Glider gives slow descent and forward momentum, used to cross long gaps
- Cannot gain altitude from glider alone — only updrafts (see boost pads)

### 3. Air Blast (contextual, not combat)
- Short directional burst of air
- Uses: push moveable objects (boulders, doors, platforms), deflect environmental hazards (falling rocks, rolling objects), trigger switches
- Does NOT damage anything. There is nothing to damage.

### 4. Wall Run (on updrafts only)
- Short timed wall-run when running into a wall marked with an updraft (visual: vertical wind streaks)
- Limited duration — a few seconds
- Used for vertical traversal, not horizontal Prince-of-Persia traversal

## Level Design: Air Temple Spires

A vertical level. The player ascends from the base of the temple complex to the peak. Key principles:

- **Verticality first.** The level reads top-to-bottom on a map. Players are mostly looking up.
- **Multiple paths.** Like classic Sonic, there should be a fast "skilled" route higher up and a safer slower route lower down.
- **Wind currents as boost pads.** Visual: swirling wind columns. Function: launch the player upward or in a directed arc. Replaces Sonic's spring pads.
- **Glide segments.** Long gaps between spires forced by missing bridges or destroyed walkways. Use the glider.
- **Updraft walls.** Vertical surfaces with visible wind streaks — these are the only walls Aang can wall-run on.
- **Air scooter sections.** Long curved ramps and connected walkways that reward charging the scooter and committing to speed.

### Tutorial Area
A small enclosed garden/courtyard at the temple's base with four discrete zones, one per mechanic:
1. A small ramp to teach jumping and double-jumping
2. A long flat path with a target zone to teach the air scooter
3. A boulder blocking a door to teach air blast
4. A small wall with visible updrafts to teach wall run

After completing all four, a gate opens to the main level.

## Technical Stack

- **Engine:** Godot 4 (latest stable). Free, open-source, integrated 3D, GDScript is beginner-friendly.
- **Language:** GDScript (Python-like, lowest learning curve for Godot beginners).
- **Version control:** Git, with frequent commits.
- **Assets:** Free 3D assets from Kenney.nl, Quaternius, or similar CC0 sources. Aang himself can be a stylized humanoid placeholder until/unless time permits a custom model.
- **Audio:** Free sound effects from freesound.org or similar; royalty-free background music.

## Development Plan (in priority order)

The plan is intentionally sequential. **Do not move to step N+1 until step N is working.**

### Phase 1: Godot Foundations (learning + setup)
1. Install Godot 4. Run through the official "Your First 3D Game" tutorial end-to-end.
2. Create a new project. Set up Git.
3. Build a flat test plane with a simple capsule character that can walk and jump. Get the camera working (third-person, behind-the-shoulder).

### Phase 2: Core Movement (the four verbs)
Implement in this order, one at a time, each on the flat test plane:
1. Walk + jump + double jump (refine until it feels good)
2. Glide (double-jump-then-hold)
3. Air scooter (hold-to-charge, release-to-dash)
4. Air blast (button press, push a test cube)
5. Wall run on a designated wall

Each mechanic should feel good *in isolation* before moving on. Tune values (jump height, scooter speed, glide fall speed) until they feel responsive.

### Phase 3: Level Building Blocks
1. Build the wind current boost pad as a reusable scene (an Area3D that applies upward force).
2. Build the updraft wall as a reusable scene (a wall with metadata flagging it as wall-runnable).
3. Build a simple collectible (Area3D, increments a counter on touch).
4. Build a level-end trigger (Area3D, fires the level-complete screen).

### Phase 4: Tutorial Area
Build the four-zone tutorial courtyard. Use simple primitive geometry. Add minimal floating text labels ("Press SPACE to jump", etc.). Confirm a player can complete it cold.

### Phase 5: Main Level
Build the Air Temple Spires level. Start with grey-box geometry only — no decoration. Focus on the path and pacing. Iterate the layout until it plays well, then decorate.

### Phase 6: Menus & Polish
Start screen, pause menu, level-complete screen. Add audio. Add visual polish (particles for air blast, trail for air scooter, wind effects on updrafts).

### Phase 7: Buffer (assume this gets eaten)
Bug fixes, playtesting feedback, anything that slipped.

## Risk Register

- **Scope creep** — the #1 risk. Anything not on the in-scope list gets rejected by default.
- **Godot learning curve** — mitigated by Phase 1. Don't skip the tutorial.
- **Movement feel** — Sonic-style movement is notoriously hard to tune. Allocate real time to Phase 2 and accept that it might take longer than expected. Better to ship one great mechanic than four mediocre ones.
- **Asset pipeline rabbit hole** — placeholder primitives are fine for the demo. Do not spend hackathon time fighting Blender.
- **Legal** — Avatar is Nickelodeon/Paramount IP. For a hackathon this is fine (non-commercial, educational). If considering public release later, plan to either file off serial numbers (generic "airbender-inspired" framing) or accept takedown risk.

## Working Preferences (for Claude Code)

- Prefer **minimal, targeted changes** over broad refactors. When fixing a problem, scope the fix to the relevant file unless cross-file changes are unavoidable.
- For code reproduction or copying, output **exactly** what was asked for — no unsolicited renaming, type additions, or style changes.
- For new concepts, prefer **beginner-friendly explanations** with concrete examples and well-commented code. I have no prior Godot experience — assume I'm learning the engine as we go.
- When suggesting Godot patterns, prefer the **idiomatic Godot way** (signals, scenes, nodes) over generic OOP patterns ported from other engines.
- If a request would push the project out of scope (per the boundaries above), flag it and ask before proceeding.

## Definition of Done (for the hackathon submission)

- Player can launch the game, see a start screen, and begin playing.
- Tutorial teaches all four movement mechanics.
- Main level (Air Temple Spires) is completable from start to finish.
- All four movement mechanics function and feel reasonable.
- At least one collectible type works.
- Game has audio (footsteps, jump, air scooter, ambient).
- Game can be exported as a runnable build (Windows at minimum).
- README explains the project, controls, and credits.

If all of the above is true, the project is shippable. Anything beyond is bonus.