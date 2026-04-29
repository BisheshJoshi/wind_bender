import math
import pygame
from constants import *

# ── Level geometry ─────────────────────────────────────────────────────────────

_PLATFORM_DATA = [
    # (x, y, w, h)
    (  0, 5100, 480, 40),   # ground
    ( 50, 4920, 200, 18),
    (230, 4800, 180, 18),
    ( 80, 4680, 160, 18),
    (260, 4560, 200, 18),
    ( 40, 4400, 140, 18),
    (240, 4280, 160, 18),
    (100, 4160, 120, 18),
    (300, 4040, 140, 18),
    ( 60, 3880, 130, 18),
    (250, 3760, 120, 18),
    ( 80, 3640, 110, 18),
    (280, 3520, 130, 18),
    (120, 3400, 140, 18),
    ( 60, 3200, 100, 18),
    (270, 3100, 110, 18),
    (150, 2980, 120, 18),
    (320, 2860, 100, 18),
    ( 80, 2740, 100, 18),
    (200, 2560,  90, 18),
    ( 60, 2420,  80, 18),
    (300, 2300,  80, 18),
    (140, 2180,  90, 18),
    (320, 2060,  80, 18),
    ( 80, 1940,  80, 18),
    (200, 1760,  80, 18),
    ( 80, 1640,  70, 18),
    (280, 1520,  70, 18),
    (150, 1400,  80, 18),
    (320, 1280,  70, 18),
    (100, 1160,  70, 18),
    (260, 1040,  70, 18),
    (160,  920,  70, 18),
    ( 80,  760,  80, 18),
    (280,  640,  80, 18),
    (160,  520,  80, 18),
    (260,  400,  80, 18),
    (120,  280,  80, 18),
    (150,  160, 180, 18),   # finish platform
]

_WIND_DATA = [
    # (x, y, w, h)
    (190, 4640, 50, 200),
    (110, 4020, 50, 200),
    (270, 3500, 50, 200),
    (155, 2640, 50, 200),
    (295, 1860, 50, 200),
    (175,  860, 50, 200),
]

_COLLECT_POS = [
    (160, 4880), (300, 4760), (140, 4640),
    (120, 4370), (320, 4250),
    (150, 3850), (310, 3710), (160, 3560),
    (220, 2530), (120, 2390), (350, 2270),
    (220, 1730), (140, 1610), (310, 1490),
    (230,  740), (300,  610), (190,  490),
]

PLAYER_START       = (240, 5100)
FINISH_WORLD_RECT  = (150, 110, 180, 50)


# ── Platform ───────────────────────────────────────────────────────────────────

class Platform:
    DEPTH   = 7     # px of 3-D face shown below the top surface
    PILLAR_W = 9

    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, surface, cam_y: float):
        r = self.rect.move(0, -round(cam_y))
        if r.bottom < 0 or r.top > HEIGHT:
            return

        # ── 3-D depth face (below platform) ──────────────────────────────────
        depth_rect = pygame.Rect(r.left + 2, r.bottom, r.width - 2, self.DEPTH)
        pygame.draw.rect(surface, C_PLAT_DARK, depth_rect)

        # ── Main surface ──────────────────────────────────────────────────────
        pygame.draw.rect(surface, C_PLATFORM, r)

        # Stone-crack detail lines on wider platforms
        if r.width >= 90:
            mid_x = r.left + r.width // 2
            pygame.draw.line(surface, C_PLAT_EDGE,
                             (mid_x, r.top + 4), (mid_x, r.bottom - 2), 1)

        # ── Highlight trim along top edge ─────────────────────────────────────
        pygame.draw.line(surface, C_PLAT_TRIM,
                         (r.left + 2, r.top + 1), (r.right - 2, r.top + 1), 2)

        # ── Border ────────────────────────────────────────────────────────────
        pygame.draw.rect(surface, C_PLAT_EDGE, r, 1)

        # ── Corner pillars on wide platforms ─────────────────────────────────
        if r.width >= 120:
            for px in (r.left, r.right - self.PILLAR_W):
                pillar = pygame.Rect(px, r.top - 5, self.PILLAR_W,
                                     r.height + self.DEPTH + 5)
                pygame.draw.rect(surface, C_PILLAR, pillar)
                # Cap
                pygame.draw.rect(surface, C_PLAT_TRIM,
                                 (px, r.top - 5, self.PILLAR_W, 3))
                pygame.draw.rect(surface, C_PLAT_EDGE, pillar, 1)


# ── Wind current ───────────────────────────────────────────────────────────────

class WindCurrent:
    def __init__(self, x, y, w, h):
        self.rect  = pygame.Rect(x, y, w, h)
        self._tick = 0
        # Pre-built surfaces (avoid allocations in draw loop)
        self._core = pygame.Surface((w, h),      pygame.SRCALPHA)
        self._core.fill((*C_WIND, 55))
        self._glow = pygame.Surface((w + 24, h), pygame.SRCALPHA)
        self._glow.fill((*C_WIND_GLOW, 20))

    def update(self):
        self._tick += 1

    def draw(self, surface, cam_y: float):
        r = self.rect.move(0, -round(cam_y))
        if r.bottom < 0 or r.top > HEIGHT:
            return

        # Outer glow
        surface.blit(self._glow, (r.left - 12, r.top))
        # Core fill
        surface.blit(self._core, r.topleft)

        # Animated upward streaks (6 lanes)
        lanes = 6
        for i in range(lanes):
            offset = (self._tick * 5 + i * (self.rect.h // lanes)) % self.rect.h
            x  = r.left + (r.w * (i + 1)) // (lanes + 1)
            y1 = r.top  + offset
            y2 = r.top  + offset - 26
            thickness = 2 if i % 2 == 0 else 1
            pygame.draw.line(surface, C_WIND, (x, y1), (x, y2), thickness)

        # Upward chevron marker that floats up from the base
        chev_offset = (self._tick * 3) % self.rect.h
        chev_y = r.bottom - chev_offset
        if r.top <= chev_y <= r.bottom:
            mid_x = r.centerx
            pygame.draw.line(surface, C_WIND_GLOW,
                             (mid_x - 9, chev_y + 7), (mid_x, chev_y), 2)
            pygame.draw.line(surface, C_WIND_GLOW,
                             (mid_x + 9, chev_y + 7), (mid_x, chev_y), 2)


# ── Collectible ────────────────────────────────────────────────────────────────

class Collectible:
    """An air scroll — drawn as a small parchment roll."""
    SW, SH = 16, 10  # scroll body dimensions
    END_R  = 6        # end-cap radius

    def __init__(self, x, y):
        # Collision area a bit larger than the visual for forgiving pickups
        self.pos  = (x, y)
        self.rect = pygame.Rect(x - 12, y - 12, 24, 24)
        self.collected = False
        self._tick = 0

    def update(self):
        if not self.collected:
            self._tick += 1

    def draw(self, surface, cam_y: float):
        if self.collected:
            return
        cx = self.pos[0]
        bob = round(3 * math.sin(self._tick * 0.07))
        cy  = self.pos[1] - round(cam_y) + bob
        if not (-30 <= cy <= HEIGHT + 30):
            return

        # Outer glow ring (two thin concentric circles)
        glow_r = self.END_R + 6 + round(abs(math.sin(self._tick * 0.07)) * 3)
        pygame.draw.circle(surface, C_COLLECT2, (cx, cy), glow_r, 1)
        pygame.draw.circle(surface, C_COLLECT,  (cx, cy), glow_r + 2, 1)

        # Scroll body
        body_left = cx - self.SW // 2
        pygame.draw.rect(surface, C_COLLECT,
                         (body_left, cy - self.SH // 2, self.SW, self.SH))

        # End caps (darker circles)
        pygame.draw.circle(surface, C_COLLECT2,
                           (body_left,               cy), self.END_R)
        pygame.draw.circle(surface, C_COLLECT2,
                           (body_left + self.SW,     cy), self.END_R)

        # Text lines on the scroll face
        for li in range(3):
            lx1 = body_left + 2
            lx2 = body_left + self.SW - 2
            ly  = cy - 2 + li * 2
            pygame.draw.line(surface, C_COLLECT2, (lx1, ly), (lx2, ly), 1)


# ── Level ──────────────────────────────────────────────────────────────────────

class Level:
    def __init__(self):
        self.platforms     = [Platform(*d)    for d in _PLATFORM_DATA]
        self.wind_currents = [WindCurrent(*d) for d in _WIND_DATA]
        self.collectibles  = [Collectible(*p) for p in _COLLECT_POS]
        self.finish_rect   = pygame.Rect(*FINISH_WORLD_RECT)
        self.score         = 0
        self.total         = len(self.collectibles)

    def update(self):
        for wc in self.wind_currents:
            wc.update()
        for c in self.collectibles:
            c.update()

    def check_collect(self, player_rect):
        for c in self.collectibles:
            if not c.collected and player_rect.colliderect(c.rect):
                c.collected = True
                self.score += 1

    def check_finish(self, player_rect):
        return player_rect.colliderect(self.finish_rect)

    def draw(self, surface, cam_y: float):
        for plat in self.platforms:
            plat.draw(surface, cam_y)
        for wc in self.wind_currents:
            wc.draw(surface, cam_y)
        for c in self.collectibles:
            c.draw(surface, cam_y)
        # Finish trigger — glowing golden border
        fr = self.finish_rect.move(0, -round(cam_y))
        if -60 <= fr.y <= HEIGHT + 60:
            pygame.draw.rect(surface, C_COLLECT,  fr, 3)
            pygame.draw.rect(surface, C_COLLECT2, fr.inflate(4, 4), 1)
