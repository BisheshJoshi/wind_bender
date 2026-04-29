import math
import pygame
from constants import *


class Player:
    W, H = 22, 32

    def __init__(self, x, y):
        # x, y = foot position
        self.rect = pygame.Rect(x - self.W // 2, y - self.H, self.W, self.H)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        self.jumps_used = 0     # 0 can jump; 1 used first; 2 used both
        self.gliding = False
        self.scooter_timer = 0
        self.scooter_dir = 1
        self.facing = 1         # 1 = right, -1 = left
        self.dead = False
        self._walk_tick = 0

    # ------------------------------------------------------------------ input

    def handle_input(self, events, keys):
        for ev in events:
            if ev.type == pygame.KEYDOWN and ev.key in (
                    pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                if self.on_ground:
                    self.vel_y = JUMP_VEL
                    self.on_ground = False
                    self.jumps_used = 1
                elif self.jumps_used < 2:
                    self.vel_y = DOUBLE_JUMP_VEL
                    self.jumps_used = 2

        # Air scooter — ground only, X or Shift
        if self.on_ground and self.scooter_timer == 0:
            if keys[pygame.K_x] or keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                self.scooter_timer = SCOOTER_FRAMES
                self.scooter_dir = self.facing
                self.vel_x = SCOOTER_SPEED * self.scooter_dir

        # Walk (suppressed while scooter active)
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

    def update(self, platforms, wind_currents):
        if self.gliding:
            self.vel_y = min(self.vel_y + GLIDE_GRAVITY, GLIDE_MAX_FALL)
        else:
            self.vel_y += GRAVITY

        if self.scooter_timer > 0:
            self.scooter_timer -= 1
            t = self.scooter_timer / SCOOTER_FRAMES
            self.vel_x = SCOOTER_SPEED * self.scooter_dir * t

        self.rect.x += round(self.vel_x)
        self.rect.x = max(0, min(WIDTH - self.W, self.rect.x))

        prev_bottom = self.rect.bottom
        prev_top    = self.rect.top
        self.rect.y += round(self.vel_y)

        self.on_ground = False
        for plat in platforms:
            if not self.rect.colliderect(plat.rect):
                continue
            if self.vel_y >= 0 and prev_bottom <= plat.rect.top + 2:
                self.rect.bottom = plat.rect.top
                self.vel_y = 0.0
                self.on_ground = True
                self.jumps_used = 0
                self.gliding = False
            elif self.vel_y < 0 and prev_top >= plat.rect.bottom - 2:
                self.rect.top = plat.rect.bottom
                self.vel_y = 0.0

        for wc in wind_currents:
            if self.rect.colliderect(wc.rect):
                self.vel_y = WIND_BOOST_VEL
                self.jumps_used = min(self.jumps_used, 1)

        if self.on_ground and self.vel_x != 0:
            self._walk_tick += 1

        if self.rect.top > LEVEL_HEIGHT + 100:
            self.dead = True

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

    # --------------------------------------------------------- state visuals

    def _draw_body(self, surface, dx, dy, cx):
        # Legs (slight walk bob)
        bob = round(2 * math.sin(self._walk_tick * 0.25)) if self.on_ground else 0
        # Left leg
        pygame.draw.rect(surface, C_PANTS, (dx + 2, dy + self.H // 2 + 2, 7, self.H // 2 - 2 + bob))
        # Right leg
        pygame.draw.rect(surface, C_PANTS, (dx + self.W - 9, dy + self.H // 2 + 2, 7, self.H // 2 - 2 - bob))
        # Tunic body
        pygame.draw.rect(surface, C_BODY, (dx, dy, self.W, self.H // 2 + 6))
        # Belt
        pygame.draw.rect(surface, C_BELT, (dx, dy + self.H // 2 + 2, self.W, 3))
        # Arm (front, facing direction)
        arm_x = dx + self.W if self.facing > 0 else dx - 5
        pygame.draw.rect(surface, C_BODY, (arm_x, dy + 4, 5, 10))

    def _draw_glider(self, surface, dx, dy, cx):
        # Body first (slightly raised — arms up)
        pygame.draw.rect(surface, C_PANTS, (dx + 2, dy + self.H // 2 + 2, 8, self.H // 2 - 2))
        pygame.draw.rect(surface, C_PANTS, (dx + self.W - 10, dy + self.H // 2 + 2, 8, self.H // 2 - 2))
        pygame.draw.rect(surface, C_BODY, (dx, dy, self.W, self.H // 2 + 6))
        pygame.draw.rect(surface, C_BELT, (dx, dy + self.H // 2 + 2, self.W, 3))

        # Glider: two swept-back wings from shoulder level
        wing_y = dy + 4
        # Canvas fill
        pygame.draw.polygon(surface, C_GLIDER2, [
            (cx,      wing_y),
            (cx - 30, wing_y + 14),
            (cx - 14, wing_y + 14),
        ])
        pygame.draw.polygon(surface, C_GLIDER2, [
            (cx,      wing_y),
            (cx + 30, wing_y + 14),
            (cx + 14, wing_y + 14),
        ])
        # Staff leading edge
        pygame.draw.line(surface, C_GLIDER, (cx - 30, wing_y + 14), (cx + 30, wing_y + 14), 3)
        pygame.draw.line(surface, C_GLIDER, (cx - 30, wing_y + 14), (cx, wing_y), 2)
        pygame.draw.line(surface, C_GLIDER, (cx + 30, wing_y + 14), (cx, wing_y), 2)

    def _draw_scooter(self, surface, dx, dy, cx):
        t = self.scooter_timer / SCOOTER_FRAMES
        radius = int(9 + 6 * t)
        ball_cy = dy + self.H + radius - 4

        # Outer glow ring
        pygame.draw.circle(surface, C_SCOOTER2, (cx, ball_cy), radius + 5, 2)
        # Ball fill
        pygame.draw.circle(surface, C_SCOOTER, (cx, ball_cy), radius)
        # Spinning spokes
        for i in range(4):
            angle = self._walk_tick * 0.18 + i * (math.pi / 2)
            sx = cx + int(math.cos(angle) * (radius - 2))
            sy = ball_cy + int(math.sin(angle) * (radius - 2))
            pygame.draw.line(surface, C_SCOOTER2, (cx, ball_cy), (sx, sy), 1)
        pygame.draw.circle(surface, C_SCOOTER2, (cx, ball_cy), radius, 1)

        # Crouched body
        pygame.draw.rect(surface, C_PANTS, (dx + 2, dy + self.H // 2 + 4, self.W - 4, self.H // 2 - 4))
        pygame.draw.rect(surface, C_BODY, (dx + 2, dy + 4, self.W - 4, self.H // 2 + 4))
        pygame.draw.rect(surface, C_BELT, (dx + 2, dy + self.H // 2 + 2, self.W - 4, 3))

    # ------------------------------------------------------------ head detail

    def _draw_head(self, surface, cx: int, cy: int):
        # Head circle
        pygame.draw.circle(surface, C_HEAD, (cx, cy), 9)

        # Blue arrow tattoo on forehead (small upward-pointing triangle)
        ax = cx + (1 if self.facing > 0 else -1)
        pygame.draw.polygon(surface, C_ARROW, [
            (ax,     cy - 6),
            (ax - 3, cy - 2),
            (ax + 3, cy - 2),
        ])

        # Eye (on the forward-facing side)
        eye_x = cx + (4 if self.facing > 0 else -4)
        pygame.draw.circle(surface, C_EYE, (eye_x, cy + 2), 2)
        # Tiny highlight
        pygame.draw.circle(surface, C_WHITE, (eye_x + 1, cy + 1), 1)
