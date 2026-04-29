import math
import random
import pygame
from constants import *


def _zone_from_alt(altitude: float) -> int:
    for i, t in enumerate(reversed(ZONE_ALTS[1:])):
        if altitude >= t:
            return len(ZONE_ALTS) - 1 - i
    return 0


# ── Platform ───────────────────────────────────────────────────────────────────

class Platform:
    DEPTH    = 7
    PILLAR_W = 9

    def __init__(self, x, y, w, h, zone: int = 0):
        self.rect = pygame.Rect(x, y, w, h)
        self.zone = zone

    def _colors(self):
        mc, tr, dk, ed, pl = ZONE_PLAT[self.zone]
        return mc, tr, dk, ed, pl

    def draw(self, surface, cam_y: float):
        r = self.rect.move(0, -round(cam_y))
        if r.bottom < 0 or r.top > HEIGHT:
            return
        mc, tr, dk, ed, pl = self._colors()
        pygame.draw.rect(surface, dk, (r.left + 2, r.bottom, r.width - 2, self.DEPTH))
        pygame.draw.rect(surface, mc, r)
        if r.width >= 90:
            mid_x = r.left + r.width // 2
            pygame.draw.line(surface, ed, (mid_x, r.top + 4), (mid_x, r.bottom - 2), 1)
        pygame.draw.line(surface, tr, (r.left + 2, r.top + 1), (r.right - 2, r.top + 1), 2)
        pygame.draw.rect(surface, ed, r, 1)
        if r.width >= 120:
            for px in (r.left, r.right - self.PILLAR_W):
                pillar = pygame.Rect(px, r.top - 5, self.PILLAR_W, r.height + self.DEPTH + 5)
                pygame.draw.rect(surface, pl, pillar)
                pygame.draw.rect(surface, tr, (px, r.top - 5, self.PILLAR_W, 3))
                pygame.draw.rect(surface, ed, pillar, 1)


class CrumblingPlatform(Platform):
    """Breaks after the player stands on it for too long."""
    SHAKE_AT  = 55   # frames before shaking starts
    FALL_AT   = 80   # frames before it falls
    FALL_SPEED = 2.5

    def __init__(self, x, y, w, zone: int = 0):
        super().__init__(x, y, w, 14, zone)
        self._stand_timer = 0
        self._falling = False
        self.gone = False

    def step_stand(self):
        """Call each frame the player is on this platform."""
        self._stand_timer += 1

    def update(self):
        if self._stand_timer >= self.FALL_AT:
            self._falling = True
        if self._falling:
            self.rect.y += round(self.FALL_SPEED)
            if self.rect.top > PLAYER_START_Y + 200:
                self.gone = True

    @property
    def collideable(self):
        return not self._falling

    def draw(self, surface, cam_y: float):
        if self._falling:
            return
        r = self.rect.move(0, -round(cam_y))
        if r.bottom < 0 or r.top > HEIGHT:
            return
        mc, tr, dk, ed, pl = self._colors()
        # Crack tint — darker than normal
        crack_col = tuple(max(0, c - 30) for c in mc)
        pygame.draw.rect(surface, dk, (r.left + 2, r.bottom, r.width - 2, self.DEPTH))
        pygame.draw.rect(surface, crack_col, r)
        # Shake visual
        if self._stand_timer >= self.SHAKE_AT:
            shake = random.randint(-2, 2)
            r = r.move(shake, 0)
        pygame.draw.line(surface, tr, (r.left + 2, r.top + 1), (r.right - 2, r.top + 1), 2)
        # Crack lines
        for cx in (r.left + r.width // 3, r.left + 2 * r.width // 3):
            pygame.draw.line(surface, ed, (cx, r.top), (cx + 3, r.bottom), 1)
        pygame.draw.rect(surface, ed, r, 1)


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
            pygame.draw.line(surface, C_WIND_GLOW, (mx - 9, chev_y + 7), (mx, chev_y), 2)
            pygame.draw.line(surface, C_WIND_GLOW, (mx + 9, chev_y + 7), (mx, chev_y), 2)


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
        pygame.draw.rect(surface, C_COLLECT, (bl, cy - self.SH // 2, self.SW, self.SH))
        pygame.draw.circle(surface, C_COLLECT2, (bl,           cy), self.END_R)
        pygame.draw.circle(surface, C_COLLECT2, (bl + self.SW, cy), self.END_R)
        for li in range(3):
            pygame.draw.line(surface, C_COLLECT2,
                             (bl + 2, cy - 2 + li * 2),
                             (bl + self.SW - 2, cy - 2 + li * 2), 1)


# ── Bison ──────────────────────────────────────────────────────────────────────

class Bison:
    BACK_W  = 90   # collision platform width
    BOB_AMP = 8

    # Sprite loaded once on first instantiation
    _sprite_r: pygame.Surface = None
    _sprite_l: pygame.Surface = None
    _sprite_loaded = False

    @classmethod
    def _load_sprite(cls):
        if cls._sprite_loaded:
            return
        cls._sprite_loaded = True
        try:
            import sprite_loader
            frames = sprite_loader.load().get("appa", [])
            if frames:
                raw = frames[0]
                # Scale so the sprite is BACK_W wide; height scales proportionally
                sw, sh = raw.get_size()
                new_h  = round(sh * cls.BACK_W / sw)
                cls._sprite_r = pygame.transform.scale(raw, (cls.BACK_W, new_h))
                cls._sprite_r.set_colorkey((255, 255, 255))
                cls._sprite_l = pygame.transform.flip(cls._sprite_r, True, False)
        except Exception:
            pass

    def __init__(self, x: float, world_y: float, direction: int = 1):
        self._load_sprite()
        self.world_x = float(x)
        self.world_y = float(world_y)
        self.vel_x   = 1.4 * direction
        self._tick   = random.randint(0, 200)
        self._update_rect()

    def _update_rect(self):
        bob = self.BOB_AMP * math.sin(self._tick * 0.025)
        self._back_y = self.world_y + bob
        self.rect = pygame.Rect(int(self.world_x), int(self._back_y), self.BACK_W, 6)

    def update(self):
        self.world_x += self.vel_x
        self._tick   += 1
        if self.world_x < -10 or self.world_x + self.BACK_W > WIDTH + 10:
            self.vel_x *= -1
        self._update_rect()

    def draw(self, surface, cam_y: float):
        dx = round(self.world_x)
        dy = round(self._back_y) - round(cam_y)

        spr = self._sprite_r if self.vel_x > 0 else self._sprite_l
        if spr:
            sh = spr.get_height()
            if -sh <= dy <= HEIGHT + sh:
                surface.blit(spr, (dx, dy))
            return

        # Fallback: primitive drawing if sprite unavailable
        BODY_H, HEAD_W, HEAD_H = 30, 38, 28
        if dy - HEAD_H - 10 > HEIGHT or dy + BODY_H + 15 < 0:
            return
        fr = self.vel_x > 0
        for i in range(3):
            lx    = dx + 10 + i * (self.BACK_W // 3)
            swing = round(4 * math.sin(self._tick * 0.12 + i * 1.2))
            pygame.draw.line(surface, C_BISON_LEG, (lx, dy + BODY_H),
                             (lx + swing, dy + BODY_H + 13), 3)
        pygame.draw.rect(surface, C_BISON, (dx, dy, self.BACK_W, BODY_H), border_radius=10)
        pygame.draw.rect(surface, C_BISON_OUT, (dx, dy, self.BACK_W, BODY_H), 1, border_radius=10)


# ── Enemy (Fire Nation soldier) ────────────────────────────────────────────────

class Enemy:
    W, H = 18, 28

    _sprites: list = []
    _sprites_loaded = False

    @classmethod
    def _load_sprites(cls):
        if cls._sprites_loaded:
            return
        cls._sprites_loaded = True
        try:
            import sprite_loader
            cls._sprites = sprite_loader.load_drake().get("enemy", [])
        except Exception:
            cls._sprites = []

    def __init__(self, x: float, y: float, plat_left: int, plat_right: int, zone: int = 0):
        self._load_sprites()
        self.rect       = pygame.Rect(int(x) - self.W // 2, int(y) - self.H, self.W, self.H)
        self.vel_x      = ENEMY_SPEED
        self.plat_left  = plat_left
        self.plat_right = plat_right
        self.zone       = zone
        self.alive      = True
        self._fire_timer = random.randint(ENEMY_FIRE_MIN, ENEMY_FIRE_MAX)
        self._tick       = 0

    def update(self) -> bool:
        """Returns True when a fireball should be spawned."""
        self.rect.x += round(self.vel_x)
        self._tick  += 1
        if self.rect.left <= self.plat_left or self.rect.right >= self.plat_right:
            self.vel_x *= -1

        self._fire_timer -= 1
        if self._fire_timer <= 0:
            self._fire_timer = random.randint(ENEMY_FIRE_MIN, ENEMY_FIRE_MAX)
            return True
        return False

    def draw(self, surface, cam_y: float):
        r = self.rect.move(0, -round(cam_y))
        if r.bottom < 0 or r.top > HEIGHT:
            return

        if self._sprites:
            frame = self._sprites[(self._tick // 8) % len(self._sprites)]
            fw, fh = frame.get_size()
            sx = r.centerx - fw // 2
            sy = r.bottom  - fh
            surface.blit(frame, (sx, sy))
            return

        # Fallback: primitive soldier drawing
        armor = C_SPIRIT_ARMOR if self.zone == 3 else C_ENEMY_ARMOR
        helm  = C_SPIRIT_HELM  if self.zone == 3 else C_ENEMY_HELM
        pygame.draw.rect(surface, armor, r, border_radius=3)
        pygame.draw.rect(surface, helm,
                         (r.left + 1, r.top, r.width - 2, r.height // 3),
                         border_radius=3)
        pygame.draw.rect(surface, C_ENEMY_EYE,
                         (r.left + 3, r.top + r.height // 4, r.width - 6, 4))
        pygame.draw.rect(surface, (0, 0, 0), r, 1, border_radius=3)


# ── Fireball ───────────────────────────────────────────────────────────────────

class Fireball:
    R = 7

    _sprites: list = []
    _sprites_loaded = False

    @classmethod
    def _load_sprites(cls):
        if cls._sprites_loaded:
            return
        cls._sprites_loaded = True
        try:
            import sprite_loader
            cls._sprites = sprite_loader.load_drake().get("fireball", [])
        except Exception:
            cls._sprites = []

    def __init__(self, x: float, y: float, direction: int):
        self._load_sprites()
        self.x     = float(x)
        self.y     = float(y)
        self.vel_x = FIREBALL_SPEED * direction
        self.dir   = direction
        self.alive = True
        self._tick = 0
        self._update_rect()

    def _update_rect(self):
        self.rect = pygame.Rect(int(self.x) - self.R, int(self.y) - self.R,
                                self.R * 2, self.R * 2)

    def update(self):
        self.x    += self.vel_x
        self._tick += 1
        self._update_rect()
        if self.x < -20 or self.x > WIDTH + 20:
            self.alive = False

    def draw(self, surface, cam_y: float):
        cx = int(self.x)
        cy = int(self.y) - round(cam_y)
        if not (-20 <= cy <= HEIGHT + 20):
            return

        if self._sprites:
            frame = self._sprites[self._tick % len(self._sprites)]
            if self.dir < 0:
                frame = pygame.transform.flip(frame, True, False)
            fw, fh = frame.get_size()
            surface.blit(frame, (cx - fw // 2, cy - fh // 2))
            return

        # Fallback: primitive fireball
        pygame.draw.circle(surface, C_FIREBALL,  (cx, cy), self.R + 3)
        pygame.draw.circle(surface, C_FIREBALL2, (cx, cy), self.R)
        flicker = round(2 * math.sin(self._tick * 0.4))
        pygame.draw.circle(surface, (255, 255, 200), (cx, cy),
                           max(2, self.R - 3 + flicker))


# ── Procedural level ───────────────────────────────────────────────────────────

class ProceduralLevel:
    CHUNK_H = 1400

    # Enemy density per zone: 0=sparse … 3=dense
    _ENEMY_CHANCE = [0.25, 0.45, 0.60, 0.80]
    # Crumbling platform chance per zone
    _CRUMBLE_CHANCE = [0.12, 0.22, 0.35, 0.50]

    def __init__(self):
        self._rng   = random.Random()
        self.platforms     : list = []
        self.wind_currents : list[WindCurrent] = []
        self.bisons        : list[Bison]       = []
        self.collectibles  : list[Collectible] = []
        self.enemies       : list[Enemy]       = []
        self.fireballs     : list[Fireball]    = []
        self._gen_y   = float(PLAYER_START_Y)
        self._last_cx = float(PLAYER_START_X)
        self._direction = 1

        # Wide ground
        self.platforms.append(Platform(0, PLAYER_START_Y, WIDTH, 40, zone=0))
        for _ in range(3):
            self._generate_chunk()

    # ----------------------------------------------------------------- private

    def _altitude(self, world_y: float) -> float:
        return max(0.0, PLAYER_START_Y - world_y)

    def _generate_chunk(self):
        target_y = self._gen_y - self.CHUNK_H
        y = self._gen_y

        while y > target_y:
            gap_y = self._rng.randint(115, 165)
            y    -= gap_y

            altitude = self._altitude(y)
            zone     = _zone_from_alt(altitude)

            drift    = self._rng.randint(90, 160)
            new_w    = self._rng.randint(70, 130)
            new_cx   = self._last_cx + self._direction * drift
            new_x    = int(new_cx - new_w // 2)
            new_x    = max(8, min(WIDTH - new_w - 8, new_x))
            # Flip direction; if clamped to wall, force flip back so we don't hug the edge
            self._direction *= -1
            if new_x <= 8 or new_x + new_w >= WIDTH - 8:
                self._direction *= -1

            # Crumbling or solid platform
            if self._rng.random() < self._CRUMBLE_CHANCE[zone]:
                plat: Platform = CrumblingPlatform(new_x, int(y), new_w, zone)
            else:
                plat = Platform(new_x, int(y), new_w, 18, zone)
            self.platforms.append(plat)
            self._last_cx = new_x + new_w // 2

            # Wind current
            if self._rng.random() < 0.14:
                wx = new_x + new_w // 3
                self.wind_currents.append(WindCurrent(wx, int(y) - 210, 50, 210))

            # Collectible
            if self._rng.random() < 0.42:
                self.collectibles.append(Collectible(new_x + new_w // 2, int(y) - 28))

            # Enemy on solid platform wide enough to patrol
            if (not isinstance(plat, CrumblingPlatform)
                    and new_w >= 70
                    and self._rng.random() < self._ENEMY_CHANCE[zone]):
                ex = new_x + new_w // 4
                self.enemies.append(Enemy(ex, int(y), new_x, new_x + new_w, zone))

            # Bison (mid-air)
            if self._rng.random() < 0.07:
                bx   = self._rng.randint(20, WIDTH - 110)
                bdir = 1 if self._rng.random() > 0.5 else -1
                self.bisons.append(Bison(bx, y - 75, bdir))

        self._gen_y = y

    # ------------------------------------------------------------------ update

    def update(self, cam_y: float, player_rect, blast_rect) -> tuple[int, int]:
        """
        Returns (kill_count, damage_count) for this frame.
        blast_rect may be None.
        """
        if self._gen_y > cam_y - 500:
            self._generate_chunk()

        cutoff = cam_y + HEIGHT + 700

        # Platforms (inc. crumbling)
        self.platforms = [p for p in self.platforms
                          if p.rect.top < cutoff
                          and not (isinstance(p, CrumblingPlatform) and p.gone)]
        for p in self.platforms:
            if isinstance(p, CrumblingPlatform):
                if p.rect.colliderect(player_rect) and not p._falling:
                    p.step_stand()
                p.update()

        self.wind_currents = [w for w in self.wind_currents if w.rect.top < cutoff]
        self.collectibles  = [c for c in self.collectibles  if c.pos[1] < cutoff]
        self.bisons        = [b for b in self.bisons        if b.world_y < cutoff]

        for wc in self.wind_currents:
            wc.update()
        for c in self.collectibles:
            c.update()
        for b in self.bisons:
            b.update()

        # ── Enemy logic ───────────────────────────────────────────────────────
        kills   = 0
        new_fbs = []
        stomp_bounce = None

        for enemy in self.enemies:
            if not enemy.alive:
                continue

            fires = enemy.update()

            # Blast kill
            if blast_rect and blast_rect.colliderect(enemy.rect):
                enemy.alive = False
                kills += 1
                continue

            # Stomp kill (player falls onto enemy head)
            if (player_rect.colliderect(enemy.rect)
                    and player_rect.bottom <= enemy.rect.top + 14):
                enemy.alive = False
                kills += 1
                stomp_bounce = True
                continue

            # Fireball spawn
            if fires:
                fdir = 1 if enemy.vel_x > 0 else -1
                new_fbs.append(
                    Fireball(enemy.rect.centerx, enemy.rect.centery, fdir))

        self.enemies   = [e for e in self.enemies
                          if e.alive and e.rect.top < cutoff]
        self.fireballs = [fb for fb in self.fireballs if fb.alive and fb.rect.top < cutoff]
        self.fireballs.extend(new_fbs)

        # ── Fireball updates + player hit ────────────────────────────────────
        damage = 0
        for fb in self.fireballs:
            fb.update()
            if fb.alive and fb.rect.colliderect(player_rect):
                fb.alive = False
                damage += 1

        # Enemy body contact damage (if not killed above)
        for enemy in self.enemies:
            if enemy.rect.colliderect(player_rect):
                damage += 1
                break   # only one damage source per frame

        self.fireballs = [fb for fb in self.fireballs if fb.alive]

        return kills, damage, stomp_bounce

    def check_collect(self, player_rect) -> int:
        n = 0
        for c in self.collectibles:
            if not c.collected and player_rect.colliderect(c.rect):
                c.collected = True
                n += 1
        return n

    def solid_platforms(self):
        """Returns only platforms valid for collision this frame."""
        return [p for p in self.platforms
                if not (isinstance(p, CrumblingPlatform) and not p.collideable)]

    def draw(self, surface, cam_y: float):
        for p in self.platforms:
            p.draw(surface, cam_y)
        for wc in self.wind_currents:
            wc.draw(surface, cam_y)
        for c in self.collectibles:
            c.draw(surface, cam_y)
        for b in self.bisons:
            b.draw(surface, cam_y)
        for e in self.enemies:
            if e.alive:
                e.draw(surface, cam_y)
        for fb in self.fireballs:
            fb.draw(surface, cam_y)
