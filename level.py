import math
import random
import pygame
from constants import *


# ── Platform ───────────────────────────────────────────────────────────────────

class Platform:
    DEPTH    = 7
    PILLAR_W = 9

    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, surface, cam_y: float):
        r = self.rect.move(0, -round(cam_y))
        if r.bottom < 0 or r.top > HEIGHT:
            return
        pygame.draw.rect(surface, C_PLAT_DARK,
                         (r.left + 2, r.bottom, r.width - 2, self.DEPTH))
        pygame.draw.rect(surface, C_PLATFORM, r)
        if r.width >= 90:
            mid_x = r.left + r.width // 2
            pygame.draw.line(surface, C_PLAT_EDGE,
                             (mid_x, r.top + 4), (mid_x, r.bottom - 2), 1)
        pygame.draw.line(surface, C_PLAT_TRIM,
                         (r.left + 2, r.top + 1), (r.right - 2, r.top + 1), 2)
        pygame.draw.rect(surface, C_PLAT_EDGE, r, 1)
        if r.width >= 120:
            for px in (r.left, r.right - self.PILLAR_W):
                pillar = pygame.Rect(px, r.top - 5, self.PILLAR_W,
                                     r.height + self.DEPTH + 5)
                pygame.draw.rect(surface, C_PILLAR, pillar)
                pygame.draw.rect(surface, C_PLAT_TRIM,
                                 (px, r.top - 5, self.PILLAR_W, 3))
                pygame.draw.rect(surface, C_PLAT_EDGE, pillar, 1)


# ── Wind current ───────────────────────────────────────────────────────────────

class WindCurrent:
    def __init__(self, x, y, w, h):
        self.rect  = pygame.Rect(x, y, w, h)
        self._tick = 0
        self._core = pygame.Surface((w, h),      pygame.SRCALPHA)
        self._core.fill((*C_WIND, 55))
        self._glow = pygame.Surface((w + 24, h), pygame.SRCALPHA)
        self._glow.fill((*C_WIND_GLOW, 18))

    def update(self):
        self._tick += 1

    def draw(self, surface, cam_y: float):
        r = self.rect.move(0, -round(cam_y))
        if r.bottom < 0 or r.top > HEIGHT:
            return
        surface.blit(self._glow, (r.left - 12, r.top))
        surface.blit(self._core, r.topleft)
        for i in range(6):
            offset = (self._tick * 5 + i * (self.rect.h // 6)) % self.rect.h
            x  = r.left + (r.w * (i + 1)) // 7
            y1 = r.top  + offset
            y2 = r.top  + offset - 26
            pygame.draw.line(surface, C_WIND, (x, y1), (x, y2),
                             2 if i % 2 == 0 else 1)
        chev_y = r.bottom - (self._tick * 3) % self.rect.h
        if r.top <= chev_y <= r.bottom:
            mx = r.centerx
            pygame.draw.line(surface, C_WIND_GLOW,
                             (mx - 9, chev_y + 7), (mx, chev_y), 2)
            pygame.draw.line(surface, C_WIND_GLOW,
                             (mx + 9, chev_y + 7), (mx, chev_y), 2)


# ── Collectible ────────────────────────────────────────────────────────────────

class Collectible:
    SW, SH = 16, 10
    END_R  = 6

    def __init__(self, x, y):
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
        cx  = self.pos[0]
        bob = round(3 * math.sin(self._tick * 0.07))
        cy  = self.pos[1] - round(cam_y) + bob
        if not (-30 <= cy <= HEIGHT + 30):
            return
        glow_r = self.END_R + 6 + round(abs(math.sin(self._tick * 0.07)) * 3)
        pygame.draw.circle(surface, C_COLLECT2, (cx, cy), glow_r, 1)
        pygame.draw.circle(surface, C_COLLECT,  (cx, cy), glow_r + 2, 1)
        bl = cx - self.SW // 2
        pygame.draw.rect(surface, C_COLLECT,
                         (bl, cy - self.SH // 2, self.SW, self.SH))
        pygame.draw.circle(surface, C_COLLECT2, (bl,           cy), self.END_R)
        pygame.draw.circle(surface, C_COLLECT2, (bl + self.SW, cy), self.END_R)
        for li in range(3):
            pygame.draw.line(surface, C_COLLECT2,
                             (bl + 2, cy - 2 + li * 2),
                             (bl + self.SW - 2, cy - 2 + li * 2), 1)


# ── Bison ──────────────────────────────────────────────────────────────────────

class Bison:
    """A flying sky bison that serves as a moving platform."""
    BACK_W = 82     # rideable back width
    BODY_H = 30     # body height (below the back surface)
    HEAD_W = 38
    HEAD_H = 28
    BOB_AMP = 8     # vertical bobbing amplitude

    def __init__(self, x: float, world_y: float, direction: int = 1):
        self.world_x = float(x)
        self.world_y = float(world_y)   # Y of back surface in world coords
        self.vel_x   = 1.4 * direction
        self._tick   = random.randint(0, 200)
        self._update_rect()

    def _update_rect(self):
        bob = self.BOB_AMP * math.sin(self._tick * 0.025)
        self._screen_back_y = self.world_y + bob   # world Y of back this frame
        self.rect = pygame.Rect(
            int(self.world_x),
            int(self._screen_back_y),
            self.BACK_W, 6
        )

    def update(self):
        self.world_x += self.vel_x
        self._tick   += 1
        if self.world_x < -10 or self.world_x + self.BACK_W > WIDTH + 10:
            self.vel_x *= -1
        self._update_rect()

    def draw(self, surface, cam_y: float):
        dx  = round(self.world_x)
        dy  = round(self._screen_back_y) - round(cam_y)  # screen Y of back

        if dy - self.HEAD_H - 10 > HEIGHT or dy + self.BODY_H + 15 < 0:
            return

        fr = self.vel_x > 0   # facing right?

        # Legs (3 visible from the side, animated)
        for i in range(3):
            lx   = dx + 10 + i * (self.BACK_W // 3)
            swing = round(4 * math.sin(self._tick * 0.12 + i * 1.2))
            pygame.draw.line(surface, C_BISON_LEG,
                             (lx,          dy + self.BODY_H),
                             (lx + swing,  dy + self.BODY_H + 13), 3)

        # Body
        pygame.draw.rect(surface, C_BISON,
                         (dx, dy, self.BACK_W, self.BODY_H),
                         border_radius=10)
        pygame.draw.rect(surface, C_BISON_OUT,
                         (dx, dy, self.BACK_W, self.BODY_H),
                         1, border_radius=10)

        # Fur detail on back (saddle area)
        pygame.draw.line(surface, C_BISON_OUT,
                         (dx + 8, dy + 2), (dx + self.BACK_W - 8, dy + 2), 1)

        # Tail
        tx = dx if fr else dx + self.BACK_W
        pygame.draw.line(surface, C_BISON_OUT,
                         (tx, dy + self.BODY_H // 2),
                         (tx + (-18 if fr else 18), dy + self.BODY_H // 2 - 8), 3)
        pygame.draw.circle(surface, C_BISON,
                           (tx + (-18 if fr else 18), dy + self.BODY_H // 2 - 8), 5)
        pygame.draw.circle(surface, C_BISON_OUT,
                           (tx + (-18 if fr else 18), dy + self.BODY_H // 2 - 8), 5, 1)

        # Head
        hx = (dx + self.BACK_W - 10) if fr else (dx - self.HEAD_W + 10)
        hy = dy - 8
        pygame.draw.ellipse(surface, C_BISON,    (hx, hy, self.HEAD_W, self.HEAD_H))
        pygame.draw.ellipse(surface, C_BISON_OUT, (hx, hy, self.HEAD_W, self.HEAD_H), 1)

        # Arrow tattoo on forehead
        acx = hx + self.HEAD_W // 2
        acy = hy + 4
        pygame.draw.polygon(surface, C_ARROW, [
            (acx,     acy),
            (acx - 4, acy + 7),
            (acx + 4, acy + 7),
        ])

        # Eye
        ex = hx + (self.HEAD_W - 7 if fr else 7)
        ey = hy + self.HEAD_H // 2 + 2
        pygame.draw.circle(surface, C_EYE,   (ex, ey), 2)
        pygame.draw.circle(surface, C_WHITE, (ex + 1, ey - 1), 1)


# ── Procedural level ───────────────────────────────────────────────────────────

class ProceduralLevel:
    """Generates platforms, wind currents, bisons, and collectibles on the fly."""

    CHUNK_H = 1400   # world-Y units generated per chunk

    def __init__(self):
        self._rng   = random.Random()   # unseeded: different each run
        self.platforms     : list[Platform]    = []
        self.wind_currents : list[WindCurrent] = []
        self.bisons        : list[Bison]       = []
        self.collectibles  : list[Collectible] = []
        self._gen_y        = float(PLAYER_START_Y)
        self._last_cx      = float(PLAYER_START_X)  # center X of last platform

        # Wide starting ground so the player has somewhere to stand
        self.platforms.append(Platform(0, PLAYER_START_Y, WIDTH, 40))

        # Seed several chunks so there are platforms above the spawn point
        for _ in range(3):
            self._generate_chunk()

    # ----------------------------------------------------------------- internal

    def _generate_chunk(self):
        target_y = self._gen_y - self.CHUNK_H
        y = self._gen_y

        while y > target_y:
            gap_y  = self._rng.randint(115, 195)
            y     -= gap_y

            # Horizontal position — must be reachable from previous platform
            drift     = self._rng.randint(55, 195)
            direction = 1 if self._rng.random() > 0.5 else -1
            new_w     = self._rng.randint(60, 135)
            new_cx    = self._last_cx + direction * drift
            new_x     = new_cx - new_w // 2
            new_x     = max(8, min(WIDTH - new_w - 8, new_x))

            self.platforms.append(Platform(int(new_x), int(y), new_w, 18))
            self._last_cx = new_x + new_w // 2

            # Wind current above some platforms
            if self._rng.random() < 0.15:
                wx = int(new_x + new_w // 3)
                self.wind_currents.append(WindCurrent(wx, int(y) - 210, 50, 210))

            # Collectible hovering above platform
            if self._rng.random() < 0.45:
                self.collectibles.append(
                    Collectible(int(new_x + new_w // 2), int(y) - 28))

            # Bison — mid-air between this and next platform
            if self._rng.random() < 0.08:
                bx  = self._rng.randint(15, WIDTH - 100)
                bdir = 1 if self._rng.random() > 0.5 else -1
                self.bisons.append(Bison(bx, y - 75, bdir))

        self._gen_y = y

    # ------------------------------------------------------------------ public

    def update(self, cam_y: float):
        # Generate more when the frontier is close to the camera top
        if self._gen_y > cam_y - 500:
            self._generate_chunk()

        # Cull elements far below the visible area
        cutoff = cam_y + HEIGHT + 700
        self.platforms     = [p for p in self.platforms     if p.rect.top  < cutoff]
        self.wind_currents = [w for w in self.wind_currents if w.rect.top  < cutoff]
        self.collectibles  = [c for c in self.collectibles  if c.pos[1]    < cutoff]
        self.bisons        = [b for b in self.bisons        if b.world_y   < cutoff]

        for wc in self.wind_currents:
            wc.update()
        for c in self.collectibles:
            c.update()
        for b in self.bisons:
            b.update()

    def check_collect(self, player_rect) -> int:
        """Return number of new scrolls collected this frame."""
        n = 0
        for c in self.collectibles:
            if not c.collected and player_rect.colliderect(c.rect):
                c.collected = True
                n += 1
        return n

    def draw(self, surface, cam_y: float):
        for p in self.platforms:
            p.draw(surface, cam_y)
        for wc in self.wind_currents:
            wc.draw(surface, cam_y)
        for c in self.collectibles:
            c.draw(surface, cam_y)
        for b in self.bisons:
            b.draw(surface, cam_y)
