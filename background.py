"""
Parallax background: Air Temple architecture silhouettes.

Layer depths (scroll factor relative to camera):
  far   0.12  — distant mountain-top pagodas
  mid   0.32  — closer temple towers + stone walls with lanterns
  cloud 0.20  — drifting clouds
"""

import random
import pygame
from constants import *


def _pagoda(surface, x: int, base_y: int, base_w: int, tiers: int, color):
    """Multi-tiered pagoda silhouette. Drawn top-down from base_y upward."""
    w   = base_w
    y   = base_y
    for _ in range(tiers):
        body_h  = 28
        roof_h  = 11
        ow      = 8            # roof overhang
        bx      = x + (base_w - w) // 2

        # Tier body
        pygame.draw.rect(surface, color, (bx, y - body_h, w, body_h))

        # Trapezoidal roof
        pygame.draw.polygon(surface, color, [
            (bx - ow,         y - body_h),
            (bx + w + ow,     y - body_h),
            (bx + w + ow - 4, y - body_h - roof_h),
            (bx + 4,          y - body_h - roof_h),
        ])

        y  -= body_h + roof_h
        w   = max(base_w // (tiers + 1), w - base_w // (tiers + 1))

    # Final needle spire
    cx = x + base_w // 2
    pygame.draw.polygon(surface, color, [
        (cx - 3, y),
        (cx + 3, y),
        (cx,     y - 18),
    ])


def _wall(surface, x: int, y: int, w: int, h: int, color):
    """Horizontal stone wall section with arched window cutouts."""
    pygame.draw.rect(surface, color, (x, y, w, h))
    darker = (max(0, color[0] - 22), max(0, color[1] - 22), max(0, color[2] - 22))
    num_w  = max(1, w // 55)
    for i in range(num_w):
        wx = x + int((i + 0.5) * w / num_w) - 7
        wy = y + h // 3
        pygame.draw.rect(surface, darker, (wx, wy + 7, 14, 15))
        pygame.draw.circle(surface, darker, (wx + 7, wy + 7), 7)


def _cloud(surface, x: int, y: int, w: int, h: int):
    r = h // 2 + 5
    pygame.draw.ellipse(surface, C_CLOUD, (x, y, w, h))
    for ox, extra in ((w // 5, 0), (w // 2, -4), (4 * w // 5, 2)):
        pygame.draw.circle(surface, C_CLOUD, (x + ox, y + r + extra), r + extra // 2)


class Background:
    def __init__(self, seed: int = 7):
        rng = random.Random(seed)

        # Far pagodas — small, 2-3 tiers, sparse
        self.far = [
            (rng.randint(-60, WIDTH + 40),
             rng.randint(200, 1400),
             rng.randint(22, 44),
             rng.randint(2, 3))
            for _ in range(22)
        ]

        # Mid pagodas — larger, 3-5 tiers
        self.mid_pagodas = [
            (rng.randint(-80, WIDTH + 60),
             rng.randint(100, 1600),
             rng.randint(38, 70),
             rng.randint(3, 5))
            for _ in range(16)
        ]

        # Mid walls — wide horizontal stone sections
        self.mid_walls = [
            (rng.randint(-80, WIDTH - 60),
             rng.randint(200, 1500),
             rng.randint(80, 200),
             rng.randint(35, 70))
            for _ in range(12)
        ]

        # Lanterns — warm dots near mid buildings
        self.lanterns = [
            (rng.randint(20, WIDTH - 20),
             rng.randint(100, 1600))
            for _ in range(35)
        ]

        # Clouds
        self.clouds = [
            (rng.randint(-120, WIDTH + 80),
             rng.randint(0, 1500),
             rng.randint(85, 200),
             rng.randint(18, 38))
            for _ in range(26)
        ]

    def draw(self, surface, cam_y: float):
        # ── Far layer ─────────────────────────────────────────────────────────
        for (x, wy, w, tiers) in self.far:
            dy = int(wy - cam_y * 0.12)
            if -200 <= dy <= HEIGHT + 200:
                _pagoda(surface, x, dy, w, tiers, C_FAR_TEMPLE)

        # ── Cloud layer ───────────────────────────────────────────────────────
        for (x, wy, w, h) in self.clouds:
            dy = int(wy - cam_y * 0.20)
            if -60 <= dy <= HEIGHT + 60:
                _cloud(surface, x, dy, w, h)

        # ── Mid walls ─────────────────────────────────────────────────────────
        for (x, wy, w, h) in self.mid_walls:
            dy = int(wy - cam_y * 0.32)
            if -h <= dy <= HEIGHT + 10:
                _wall(surface, x, dy, w, h, C_MID_TEMPLE)

        # ── Mid pagodas ───────────────────────────────────────────────────────
        for (x, wy, w, tiers) in self.mid_pagodas:
            dy = int(wy - cam_y * 0.32)
            if -300 <= dy <= HEIGHT + 50:
                _pagoda(surface, x, dy, w, tiers, C_MID_TEMPLE)

        # ── Lanterns ──────────────────────────────────────────────────────────
        for (x, wy) in self.lanterns:
            dy = int(wy - cam_y * 0.32)
            if -10 <= dy <= HEIGHT + 10:
                pygame.draw.circle(surface, C_LANTERN, (x, dy), 3)
                # Soft glow ring
                pygame.draw.circle(surface, (*C_LANTERN[:2], 80),
                                   (x, dy), 6, 1)
