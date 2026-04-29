import math
import pygame
from constants import *


class Player:
    W, H = 22, 32

    def __init__(self, x, y):
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

    # ------------------------------------------------------------------ input

    def handle_input(self, events, keys):
        for ev in events:
            if ev.type == pygame.KEYDOWN and ev.key in (
                    pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                if self.on_ground:
                    self.vel_y = JUMP_VEL
                    self.on_ground  = False
                    self.jumps_used = 1
                elif self.jumps_used < 2:
                    self.vel_y = DOUBLE_JUMP_VEL
                    self.jumps_used = 2

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

        # Static platform collision
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

        # Bison collision — same as platform + carry player horizontally
        for bison in bisons:
            if not self.rect.colliderect(bison.rect):
                continue
            if self.vel_y >= 0 and prev_bottom <= bison.rect.top + 2:
                self.rect.bottom = bison.rect.top
                self.vel_y  = 0.0
                self.on_ground  = True
                self.jumps_used = 0
                self.gliding    = False
                # Move with bison
                self.rect.x += round(bison.vel_x)
                self.rect.x  = max(0, min(WIDTH - self.W, self.rect.x))

        # Wind current
        for wc in wind_currents:
            if self.rect.colliderect(wc.rect):
                self.vel_y = WIND_BOOST_VEL
                self.jumps_used = min(self.jumps_used, 1)

    # ------------------------------------------------------------------ draw

    def draw(self, surface, cam_y: float):
        dx = self.rect.x
        dy = self.rect.y - round(cam_y)
        cx = dx + self.W // 2

        if self.scooter_timer > 0:
            self._draw_scooter(surface, dx, dy, cx)
        elif self.gliding:
            self._draw_glider(surface, dx, dy, cx)
        else:
            self._draw_body(surface, dx, dy, cx)

        self._draw_head(surface, cx, dy - 9)

    def _draw_body(self, surface, dx, dy, cx):
        bob = round(2 * math.sin(self._tick * 0.25)) if self.on_ground and self.vel_x != 0 else 0
        pygame.draw.rect(surface, C_PANTS, (dx + 2,          dy + self.H // 2 + 2, 7, self.H // 2 - 2 + bob))
        pygame.draw.rect(surface, C_PANTS, (dx + self.W - 9, dy + self.H // 2 + 2, 7, self.H // 2 - 2 - bob))
        pygame.draw.rect(surface, C_BODY,  (dx,              dy,                  self.W, self.H // 2 + 6))
        pygame.draw.rect(surface, C_BELT,  (dx,              dy + self.H // 2 + 2, self.W, 3))
        arm_x = dx + self.W if self.facing > 0 else dx - 5
        pygame.draw.rect(surface, C_BODY, (arm_x, dy + 4, 5, 10))

    def _draw_glider(self, surface, dx, dy, cx):
        pygame.draw.rect(surface, C_PANTS, (dx + 2,          dy + self.H // 2 + 2, 8, self.H // 2 - 2))
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
