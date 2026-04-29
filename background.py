"""
Four-zone parallax background reflecting Avatar locations.

Zone 0  Southern Air Temple  — warm stone pagodas, lanterns
Zone 1  Eastern Air Temple   — taller darker spires, prayer banners
Zone 2  Northern Mountaintop — icy peaks, dense cloud cover
Zone 3  Spirit World         — glowing spirit trees, floating wisps
"""

import random
import math
import pygame
from constants import *


# ── Drawing helpers ────────────────────────────────────────────────────────────

def _pagoda(surface, x, base_y, base_w, tiers, color):
    w, y = base_w, base_y
    for _ in range(tiers):
        bx = x + (base_w - w) // 2
        pygame.draw.rect(surface, color, (bx, y - 28, w, 28))
        ow = 8
        pygame.draw.polygon(surface, color, [
            (bx - ow,         y - 28),
            (bx + w + ow,     y - 28),
            (bx + w + ow - 4, y - 28 - 11),
            (bx + 4,          y - 28 - 11),
        ])
        y  -= 39
        w   = max(base_w // (tiers + 1), w - base_w // (tiers + 1))
    cx = x + base_w // 2
    pygame.draw.polygon(surface, color, [(cx - 3, y), (cx + 3, y), (cx, y - 18)])


def _wall(surface, x, y, w, h, color):
    pygame.draw.rect(surface, color, (x, y, w, h))
    dk = tuple(max(0, c - 22) for c in color)
    for i in range(max(1, w // 55)):
        wx = x + int((i + 0.5) * w / max(1, w // 55)) - 7
        wy = y + h // 3
        pygame.draw.rect(surface, dk, (wx, wy + 7, 14, 15))
        pygame.draw.circle(surface, dk, (wx + 7, wy + 7), 7)


def _banner(surface, x, y, color):
    """Hanging triangular prayer banner."""
    pygame.draw.polygon(surface, color, [(x, y), (x + 12, y), (x + 6, y + 22)])
    pygame.draw.line(surface, tuple(max(0, c - 30) for c in color),
                     (x, y), (x + 12, y), 2)


def _ice_peak(surface, x, y, w, h, color):
    """Triangular icy mountain silhouette."""
    pygame.draw.polygon(surface, color, [
        (x,          y + h),
        (x + w,      y + h),
        (x + w // 2, y),
    ])
    # Snow cap highlight
    cap = tuple(min(255, c + 40) for c in color)
    pygame.draw.polygon(surface, cap, [
        (x + w // 2 - 6, y + h // 5),
        (x + w // 2 + 6, y + h // 5),
        (x + w // 2,     y),
    ])


def _spirit_tree(surface, x, y, h, color):
    """Glowing organic spirit-world tree."""
    # Trunk
    trunk_w = max(6, h // 10)
    pygame.draw.rect(surface, color, (x - trunk_w // 2, y - h, trunk_w, h))
    # Branches / canopy blobs
    for i, (ox, oy, r) in enumerate([
        (0, -h, h // 3),
        (-h // 4, -h * 3 // 4, h // 4),
        ( h // 4, -h * 3 // 4, h // 4),
        (0,       -h * 5 // 6, h // 5),
    ]):
        pygame.draw.circle(surface, color, (x + ox, y + oy), r)


def _cloud(surface, x, y, w, h):
    r = h // 2 + 5
    pygame.draw.ellipse(surface, C_CLOUD, (x, y, w, h))
    for ox, extra in ((w // 5, 0), (w // 2, -4), (4 * w // 5, 2)):
        pygame.draw.circle(surface, C_CLOUD, (x + ox, y + r + extra), r + extra // 2)


# ── Background class ───────────────────────────────────────────────────────────

class Background:
    def __init__(self, seed: int = 7):
        rng = random.Random(seed)

        # Zone 0 & 1 — far pagodas
        self.far_pagodas = [
            (rng.randint(-70, WIDTH + 50),
             rng.randint(100, 1500),
             rng.randint(22, 46),
             rng.randint(2, 3))
            for _ in range(28)
        ]
        # Zone 0 & 1 — mid pagodas + walls
        self.mid_pagodas = [
            (rng.randint(-90, WIDTH + 60),
             rng.randint(80, 1600),
             rng.randint(38, 72),
             rng.randint(3, 5))
            for _ in range(18)
        ]
        self.mid_walls = [
            (rng.randint(-80, WIDTH - 60),
             rng.randint(180, 1500),
             rng.randint(90, 220),
             rng.randint(32, 70))
            for _ in range(14)
        ]
        self.banners = [
            (rng.randint(20, WIDTH - 20),
             rng.randint(80, 1600),
             (rng.randint(180, 255), rng.randint(80, 160), 0))
            for _ in range(30)
        ]
        self.lanterns = [
            (rng.randint(20, WIDTH - 20),
             rng.randint(80, 1600))
            for _ in range(40)
        ]

        # Zone 2 — icy peaks
        self.ice_peaks = [
            (rng.randint(-80, WIDTH + 80),
             rng.randint(80, 1500),
             rng.randint(60, 160),
             rng.randint(80, 220))
            for _ in range(22)
        ]

        # Zone 3 — spirit trees
        self.spirit_trees = [
            (rng.randint(10, WIDTH - 10),
             rng.randint(80, 1500),
             rng.randint(80, 200))
            for _ in range(20)
        ]
        self.wisps = [
            (rng.randint(20, WIDTH - 20),
             rng.randint(80, 1500),
             rng.random() * math.pi * 2)
            for _ in range(35)
        ]

        # Clouds always present
        self.clouds = [
            (rng.randint(-120, WIDTH + 80),
             rng.randint(0, 1500),
             rng.randint(85, 210),
             rng.randint(18, 40))
            for _ in range(28)
        ]

        self._tick = 0

    # ------------------------------------------------------------------ draw

    def draw(self, surface, cam_y: float, zone: int):
        self._tick += 1
        t = self._tick

        if zone <= 1:
            self._draw_temple(surface, cam_y, zone)
        elif zone == 2:
            self._draw_mountain(surface, cam_y)
        else:
            self._draw_spirit(surface, cam_y, t)

        # Clouds always
        for (x, wy, w, h) in self.clouds:
            dy = int(wy - cam_y * 0.20)
            if -60 <= dy <= HEIGHT + 60:
                _cloud(surface, x, dy, w, h)

    def _draw_temple(self, surface, cam_y: float, zone: int):
        far_col = (38, 68, 118) if zone == 0 else (28, 52, 100)
        mid_col = (55, 92, 148) if zone == 0 else (42, 72, 130)

        for (x, wy, w, tiers) in self.far_pagodas:
            dy = int(wy - cam_y * 0.12)
            if -300 <= dy <= HEIGHT + 50:
                _pagoda(surface, x, dy, w, tiers, far_col)

        for (x, wy, w, h) in self.mid_walls:
            dy = int(wy - cam_y * 0.32)
            if -h <= dy <= HEIGHT + 10:
                _wall(surface, x, dy, w, h, mid_col)

        for (x, wy, w, tiers) in self.mid_pagodas:
            dy = int(wy - cam_y * 0.32)
            if -300 <= dy <= HEIGHT + 50:
                _pagoda(surface, x, dy, w, tiers, mid_col)

        for (x, wy, color) in self.banners:
            dy = int(wy - cam_y * 0.32)
            if -30 <= dy <= HEIGHT + 30:
                _banner(surface, x, dy, color)

        for (x, wy) in self.lanterns:
            dy = int(wy - cam_y * 0.32)
            if -10 <= dy <= HEIGHT + 10:
                pygame.draw.circle(surface, C_LANTERN, (x, dy), 3)
                pygame.draw.circle(surface, (255, 200, 80), (x, dy), 6, 1)

    def _draw_mountain(self, surface, cam_y: float):
        far_col = (115, 130, 150)
        mid_col = (145, 162, 180)
        for (x, wy, w, h) in self.ice_peaks:
            dy = int(wy - cam_y * 0.15)
            if dy - h <= HEIGHT and dy >= -10:
                _ice_peak(surface, x, dy, w, h, far_col)
        for (x, wy, w, h) in self.ice_peaks[::2]:
            dy = int(wy - cam_y * 0.35) - 50
            if dy - h <= HEIGHT and dy >= -10:
                _ice_peak(surface, x + 30, dy, int(w * 0.7), int(h * 0.8), mid_col)

    def _draw_spirit(self, surface, cam_y: float, t: int):
        tree_col  = ( 50, 190, 160)
        wisp_col1 = (120, 255, 200)
        wisp_col2 = (200, 120, 255)

        for (x, wy, h) in self.spirit_trees:
            dy = int(wy - cam_y * 0.25)
            if dy - h <= HEIGHT + 20 and dy >= -20:
                _spirit_tree(surface, x, dy, h, tree_col)
                # Glow ring
                pygame.draw.circle(surface, (40, 160, 130),
                                   (x, dy - h), h // 3 + 3, 2)

        for i, (x, wy, phase) in enumerate(self.wisps):
            dy_base = int(wy - cam_y * 0.30)
            if not (-20 <= dy_base <= HEIGHT + 20):
                continue
            # Floating wander
            wx = x + round(20 * math.sin(t * 0.018 + phase))
            wy2 = dy_base + round(12 * math.cos(t * 0.022 + phase))
            col = wisp_col1 if i % 2 == 0 else wisp_col2
            pygame.draw.circle(surface, col, (wx, wy2), 4)
            pygame.draw.circle(surface, col, (wx, wy2), 7, 1)
