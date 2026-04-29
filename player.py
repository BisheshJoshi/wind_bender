import math
import pygame
import sprite_loader
from constants import *


class Player:
    W, H = 22, 32

    # Sprites loaded once at first instantiation
    _sprites: dict = {}
    _sprites_loaded = False

    @classmethod
    def _load_sprites(cls):
        if not cls._sprites_loaded:
            cls._sprites = sprite_loader.load()
            cls._sprites_loaded = True

    def __init__(self, x, y):
        self._load_sprites()
        self.rect = pygame.Rect(x - self.W // 2, y - self.H, self.W, self.H)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground  = False
        self.jumps_used = 0
        self.gliding    = False
        self.scooter_timer = 0
        self.scooter_dir   = 1
        self.facing = 1
        self.dead   = False
        self._tick  = 0

        # Health & combat
        self.health       = PLAYER_MAX_HEALTH
        self.inv_timer    = 0           # invincibility frames remaining
        self.blast_cd     = 0           # blast cooldown frames
        self._blast_active = False      # True for one frame on trigger
        self._blast_anim  = 0           # visual countdown

    # ------------------------------------------------------------------ input

    def handle_input(self, events, keys):
        for ev in events:
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    if self.on_ground:
                        self.vel_y = JUMP_VEL
                        self.on_ground  = False
                        self.jumps_used = 1
                    elif self.jumps_used < 2:
                        self.vel_y = DOUBLE_JUMP_VEL
                        self.jumps_used = 2
                if ev.key in (pygame.K_z, pygame.K_q) and self.blast_cd == 0:
                    self._blast_active = True
                    self.blast_cd      = BLAST_COOLDOWN
                    self._blast_anim   = BLAST_ANIM_FRAMES

        if self.on_ground and self.scooter_timer == 0:
            if keys[pygame.K_x] or keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                self.scooter_timer = SCOOTER_FRAMES
                self.scooter_dir   = self.facing
                self.vel_x = SCOOTER_SPEED * self.scooter_dir

        if self.scooter_timer == 0:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.vel_x = -WALK_SPEED
                self.facing = -1
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.vel_x = WALK_SPEED
                self.facing = 1
            else:
                self.vel_x = 0.0

        glide_held = (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w])
        self.gliding = (self.jumps_used >= 2 and self.vel_y > 0 and glide_held)

    # ----------------------------------------------------------------- update

    def update(self, platforms, wind_currents, bisons=()):
        self._tick += 1

        if self.inv_timer  > 0: self.inv_timer  -= 1
        if self.blast_cd   > 0: self.blast_cd   -= 1
        if self._blast_anim > 0: self._blast_anim -= 1

        if self.gliding:
            self.vel_y = min(self.vel_y + GLIDE_GRAVITY, GLIDE_MAX_FALL)
        else:
            self.vel_y += GRAVITY

        if self.scooter_timer > 0:
            self.scooter_timer -= 1
            t = self.scooter_timer / SCOOTER_FRAMES
            self.vel_x = SCOOTER_SPEED * self.scooter_dir * t

        self.rect.x += round(self.vel_x)
        self.rect.x  = max(0, min(WIDTH - self.W, self.rect.x))

        prev_bottom = self.rect.bottom
        prev_top    = self.rect.top
        self.rect.y += round(self.vel_y)

        self.on_ground = False

        for plat in platforms:
            if not self.rect.colliderect(plat.rect):
                continue
            if self.vel_y >= 0 and prev_bottom <= plat.rect.top + 2:
                self.rect.bottom = plat.rect.top
                self.vel_y  = 0.0
                self.on_ground  = True
                self.jumps_used = 0
                self.gliding    = False
            elif self.vel_y < 0 and prev_top >= plat.rect.bottom - 2:
                self.rect.top = plat.rect.bottom
                self.vel_y = 0.0

        for bison in bisons:
            if not self.rect.colliderect(bison.rect):
                continue
            if self.vel_y >= 0 and prev_bottom <= bison.rect.top + 2:
                self.rect.bottom = bison.rect.top
                self.vel_y  = 0.0
                self.on_ground  = True
                self.jumps_used = 0
                self.gliding    = False
                self.rect.x += round(bison.vel_x)
                self.rect.x  = max(0, min(WIDTH - self.W, self.rect.x))

        for wc in wind_currents:
            if self.rect.colliderect(wc.rect):
                self.vel_y = WIND_BOOST_VEL
                self.jumps_used = min(self.jumps_used, 1)

        # Fall off world
        if self.rect.top > PLAYER_START_Y + 120:
            self.dead = True

    # ----------------------------------------------------------------- combat

    def get_blast_rect(self):
        """One-frame blast hitbox, then clears the flag."""
        if not self._blast_active:
            return None
        self._blast_active = False
        if self.facing > 0:
            return pygame.Rect(self.rect.right, self.rect.top, BLAST_RANGE, self.H)
        else:
            return pygame.Rect(self.rect.left - BLAST_RANGE, self.rect.top, BLAST_RANGE, self.H)

    def take_damage(self) -> bool:
        """Returns True if damage was applied."""
        if self.inv_timer > 0:
            return False
        self.health   -= 1
        self.inv_timer = INV_FRAMES
        if self.health <= 0:
            self.dead = True
        return True

    def stomp_bounce(self):
        self.vel_y = JUMP_VEL * 0.55
        self.jumps_used = 1

    # ------------------------------------------------------------------ draw

    def draw(self, surface, cam_y: float):
        # Flash during invincibility
        if self.inv_timer > 0 and (self.inv_timer // 5) % 2 == 0:
            return

        dx = self.rect.x
        dy = self.rect.y - round(cam_y)
        cx = dx + self.W // 2

        if self._sprites and not self._draw_sprite(surface, dx, dy):
            # Sprite draw failed; fall back to primitives
            if self.scooter_timer > 0:
                self._draw_scooter(surface, dx, dy, cx)
            elif self.gliding:
                self._draw_glider(surface, dx, dy, cx)
            else:
                self._draw_body(surface, dx, dy, cx)
            self._draw_head(surface, cx, dy - 9)
        elif not self._sprites:
            if self.scooter_timer > 0:
                self._draw_scooter(surface, dx, dy, cx)
            elif self.gliding:
                self._draw_glider(surface, dx, dy, cx)
            else:
                self._draw_body(surface, dx, dy, cx)
            self._draw_head(surface, cx, dy - 9)

        self._draw_blast(surface, dx, dy)

    def _draw_sprite(self, surface, dx: int, dy: int) -> bool:
        """Draw the correct animated sprite frame. Returns False if no frames."""
        sp = self._sprites

        if self.scooter_timer > 0:
            key = "scoot_r" if self.scooter_dir > 0 else "scoot_l"
        elif self.gliding:
            key = "glide"
        elif self._blast_anim > 0:
            key = "blast"
        elif self.vel_x != 0 and self.on_ground:
            key = "walk_r" if self.facing > 0 else "walk_l"
        else:
            key = "idle"

        # Fallback chain
        frames = sp.get(key) or sp.get("idle") or []
        if not frames:
            return False

        if key == "idle":
            frame_idx = 0   # standing still = no animation
        else:
            fps_divisor = 5
            frame_idx   = (self._tick // fps_divisor) % len(frames)
        frame = frames[frame_idx]

        fw, fh = frame.get_size()
        # Centre the sprite on the player rect, bottom-aligned
        sx = dx + self.W // 2 - fw // 2
        sy = dy + self.H - fh

        # Flip for left-facing states that only have right-facing art
        needs_flip = (self.facing < 0 and key in ("idle", "glide", "blast"))
        if needs_flip:
            frame = pygame.transform.flip(frame, True, False)

        surface.blit(frame, (sx, sy))
        return True

    def _draw_body(self, surface, dx, dy, cx):
        bob = round(2 * math.sin(self._tick * 0.25)) if self.on_ground and self.vel_x != 0 else 0
        pygame.draw.rect(surface, C_PANTS, (dx + 2,          dy + self.H // 2 + 2, 7, self.H // 2 - 2 + bob))
        pygame.draw.rect(surface, C_PANTS, (dx + self.W - 9, dy + self.H // 2 + 2, 7, self.H // 2 - 2 - bob))
        pygame.draw.rect(surface, C_BODY,  (dx,              dy,                  self.W, self.H // 2 + 6))
        pygame.draw.rect(surface, C_BELT,  (dx,              dy + self.H // 2 + 2, self.W, 3))
        arm_x = dx + self.W if self.facing > 0 else dx - 5
        pygame.draw.rect(surface, C_BODY, (arm_x, dy + 4, 5, 10))

    def _draw_glider(self, surface, dx, dy, cx):
        pygame.draw.rect(surface, C_PANTS, (dx + 2,           dy + self.H // 2 + 2, 8, self.H // 2 - 2))
        pygame.draw.rect(surface, C_PANTS, (dx + self.W - 10, dy + self.H // 2 + 2, 8, self.H // 2 - 2))
        pygame.draw.rect(surface, C_BODY,  (dx, dy, self.W, self.H // 2 + 6))
        pygame.draw.rect(surface, C_BELT,  (dx, dy + self.H // 2 + 2, self.W, 3))
        wy = dy + 4
        pygame.draw.polygon(surface, C_GLIDER2, [(cx, wy), (cx - 30, wy + 14), (cx - 14, wy + 14)])
        pygame.draw.polygon(surface, C_GLIDER2, [(cx, wy), (cx + 30, wy + 14), (cx + 14, wy + 14)])
        pygame.draw.line(surface, C_GLIDER, (cx - 30, wy + 14), (cx + 30, wy + 14), 3)
        pygame.draw.line(surface, C_GLIDER, (cx - 30, wy + 14), (cx, wy), 2)
        pygame.draw.line(surface, C_GLIDER, (cx + 30, wy + 14), (cx, wy), 2)

    def _draw_scooter(self, surface, dx, dy, cx):
        t      = self.scooter_timer / SCOOTER_FRAMES
        radius = int(9 + 6 * t)
        bcy    = dy + self.H + radius - 4
        pygame.draw.circle(surface, C_SCOOTER2, (cx, bcy), radius + 5, 2)
        pygame.draw.circle(surface, C_SCOOTER,  (cx, bcy), radius)
        for i in range(4):
            angle = self._tick * 0.18 + i * (math.pi / 2)
            sx = cx + int(math.cos(angle) * (radius - 2))
            sy = bcy + int(math.sin(angle) * (radius - 2))
            pygame.draw.line(surface, C_SCOOTER2, (cx, bcy), (sx, sy), 1)
        pygame.draw.circle(surface, C_SCOOTER2, (cx, bcy), radius, 1)
        pygame.draw.rect(surface, C_PANTS, (dx + 2, dy + self.H // 2 + 4, self.W - 4, self.H // 2 - 4))
        pygame.draw.rect(surface, C_BODY,  (dx + 2, dy + 4,              self.W - 4, self.H // 2 + 4))
        pygame.draw.rect(surface, C_BELT,  (dx + 2, dy + self.H // 2 + 2, self.W - 4, 3))

    def _draw_head(self, surface, cx: int, cy: int):
        pygame.draw.circle(surface, C_HEAD, (cx, cy), 9)
        ax = cx + (1 if self.facing > 0 else -1)
        pygame.draw.polygon(surface, C_ARROW, [(ax, cy - 6), (ax - 3, cy - 2), (ax + 3, cy - 2)])
        ex = cx + (4 if self.facing > 0 else -4)
        pygame.draw.circle(surface, C_EYE,   (ex, cy + 2), 2)
        pygame.draw.circle(surface, C_WHITE, (ex + 1, cy + 1), 1)

    def _draw_blast(self, surface, dx, dy):
        if self._blast_anim <= 0:
            return
        t  = self._blast_anim / BLAST_ANIM_FRAMES
        bx = (self.rect.right if self.facing > 0 else self.rect.left - BLAST_RANGE) - round(0)
        # Adjust to screen coords (dy already has cam subtracted for body, use rect directly)
        bx_s = bx
        by_s = dy + 4
        blast_surf = pygame.Surface((BLAST_RANGE, self.H - 8), pygame.SRCALPHA)
        alpha = int(160 * t)
        blast_surf.fill((*C_WIND_GLOW, alpha))
        surface.blit(blast_surf, (bx_s, by_s))
        # Streak lines
        lx_start = bx_s if self.facing > 0 else bx_s + BLAST_RANGE
        lx_step  = (BLAST_RANGE // 4) * self.facing
        for i in range(4):
            lx = lx_start + lx_step * i
            pygame.draw.line(surface, C_WIND_GLOW,
                             (lx, by_s + 4), (lx + lx_step, by_s + self.H // 2 - 4), 1)
