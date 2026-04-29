import random
import pygame
from constants import *


class Background:
    """Pre-generated parallax layers: far spires, mid spires, clouds."""

    def __init__(self, seed: int = 7):
        rng = random.Random(seed)

        # Far spires — scroll at 15 % of cam speed
        self.far = [
            (rng.randint(-70, WIDTH + 70),
             rng.randint(-400, LEVEL_HEIGHT + 400),
             rng.randint(18, 46),
             rng.randint(280, 760))
            for _ in range(30)
        ]

        # Mid spires — scroll at 35 %
        self.mid = [
            (rng.randint(-90, WIDTH + 90),
             rng.randint(-400, LEVEL_HEIGHT + 400),
             rng.randint(30, 68),
             rng.randint(380, 950))
            for _ in range(20)
        ]

        # Clouds — scroll at 22 %
        self.clouds = [
            (rng.randint(-120, WIDTH + 120),
             rng.randint(0, LEVEL_HEIGHT),
             rng.randint(80, 210),
             rng.randint(20, 42))
            for _ in range(24)
        ]

    # ---------------------------------------------------------------- helpers

    @staticmethod
    def _spire(surface, x: int, y: int, w: int, h: int, color):
        """Rectangle body + triangular pointed cap."""
        pygame.draw.rect(surface, color, (x, y, w, h))
        tip_h = max(w + 10, 32)
        pygame.draw.polygon(surface, color, [
            (x,           y),
            (x + w,       y),
            (x + w // 2,  y - tip_h),
        ])

    @staticmethod
    def _cloud(surface, x: int, y: int, w: int, h: int):
        """Puffy cloud made of overlapping ellipses."""
        # Base oblong
        pygame.draw.ellipse(surface, C_CLOUD, (x, y, w, h))
        # Three puffs along the top
        r = h // 2 + 5
        for i, (ox, oh) in enumerate([(w // 5, 0), (w // 2, -4), (4 * w // 5, 2)]):
            pygame.draw.circle(surface, C_CLOUD, (x + ox, y + r + oh), r + i)

    # ---------------------------------------------------------------- public

    def draw(self, surface, cam_y: float):
        # Far layer
        for (x, wy, w, h) in self.far:
            dy = int(wy - cam_y * 0.15)
            if dy + h + w < 0 or dy > HEIGHT:
                continue
            self._spire(surface, x, dy, w, h, C_FAR_SPIRE)

        # Mid layer
        for (x, wy, w, h) in self.mid:
            dy = int(wy - cam_y * 0.35)
            if dy + h + w < 0 or dy > HEIGHT:
                continue
            self._spire(surface, x, dy, w, h, C_MID_SPIRE)

        # Clouds
        for (x, wy, w, h) in self.clouds:
            dy = int(wy - cam_y * 0.22)
            if dy > HEIGHT or dy + h + h < 0:
                continue
            self._cloud(surface, x, dy, w, h)
