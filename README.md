# Airbender Spires

A vertical platformer built in Python and pygame, themed around Avatar: The Last Airbender. You play as Aang, climbing endlessly upward through four zones — Southern Air Temple, Eastern Air Temple, Northern Mountaintop, and the Spirit World — while a rising fire floor forces you to keep moving. Fight Fire Nation soldiers, ride flying bisons, dodge fireballs, and use airbending to survive as long as possible.

---

## What it does

- Infinite procedurally generated vertical level with a single zigzag path up
- Rising fire floor that accelerates over time — fall behind and you die
- Four altitude-based zones, each with unique visuals, sky, platform style, and enemy density
- GBA-accurate Aang sprite animations: walk, idle, glide, air blast, air dash
- Enemies drawn from the Fire Drake NES sprite sheet with animated fireballs
- Flying bisons (Appa) as moving platforms
- Tornado-style wind current columns that launch you upward
- Air Blast (Z/Q) kills enemies; stomp enemies by landing on their heads
- Air Dash (X/Shift) works both on the ground and mid-air
- Health system with invincibility frames and procedural hit/death/wind sounds
- Score based on height climbed + scrolls collected + enemies killed
- Local leaderboard saved to `scores.json`

---

## How to run

### a. Clone the repo

```bash
git clone https://github.com/BisheshJoshi/wind_bender.git
cd wind_bender
git checkout klens
```

### b. Install dependencies

Python 3.10+ is required.

```bash
pip install -r requirements.txt
```

### c. Run

```bash
python main.py
```

**Controls**

| Key | Action |
|-----|--------|
| Arrows / WASD | Move |
| SPACE | Jump (press again mid-air = double jump) |
| Hold SPACE (falling) | Glide |
| X / Shift | Air Dash (ground or mid-air) |
| Z / Q | Air Blast — kills enemies |
| ESC (during play) | Return to title |
| ESC (title screen) | Quit |

---

## Members

-Klenis Arapaj
-Shankar Jora
-Bishesh Joshi
