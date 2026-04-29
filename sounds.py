"""Procedurally generated sound effects — no external files needed."""
import array
import math
import random

_RATE = 22050   # must match pygame.mixer.pre_init frequency

def _make(samples: list) -> "pygame.mixer.Sound":
    import pygame
    buf = array.array('h')
    for s in samples:
        v = max(-32767, min(32767, int(s * 32767)))
        buf.append(v)   # left
        buf.append(v)   # right (stereo)
    return pygame.mixer.Sound(buffer=buf)


def _death() -> "pygame.mixer.Sound":
    n = int(_RATE * 0.75)
    out = []
    for i in range(n):
        t = i / _RATE
        freq = 520 * max(0.18, 1.0 - t * 1.6)
        amp  = max(0.0, 1.0 - t * 1.35) * 0.38
        out.append(amp * math.sin(2 * math.pi * freq * t))
    return _make(out)


def _hit() -> "pygame.mixer.Sound":
    n   = int(_RATE * 0.15)
    rng = random.Random(1)
    out = []
    prev = 0.0
    for i in range(n):
        t    = i / _RATE
        prev = 0.3 * prev + 0.7 * (rng.random() * 2 - 1)
        amp  = (1.0 - t / 0.15) ** 2 * 0.55
        out.append(amp * prev)
    return _make(out)


def _wind() -> "pygame.mixer.Sound":
    """Short whoosh played when the air-dash / scooter activates."""
    n   = int(_RATE * 0.45)
    rng = random.Random(7)
    out = []
    prev = 0.0
    for i in range(n):
        t    = i / _RATE
        prev = 0.83 * prev + 0.17 * (rng.random() * 2 - 1)
        env  = math.sin(math.pi * t / 0.45) * 0.42
        out.append(env * prev)
    return _make(out)


def load() -> dict:
    """Return {'death': Sound, 'hit': Sound, 'wind': Sound}.
    Returns {} silently if mixer is not ready."""
    try:
        return {'death': _death(), 'hit': _hit(), 'wind': _wind()}
    except Exception:
        return {}
