import pygame
import random
from settings import *

class Spire:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface, camera_offset):
        draw_rect = self.rect.copy()
        draw_rect.y -= camera_offset
        pygame.draw.rect(surface, SPIRE_COLOR, draw_rect)

class Updraft:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface, camera_offset):
        draw_rect = self.rect.copy()
        draw_rect.y -= camera_offset
        # draw semi-transparent light blue
        s = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
        s.fill((200, 200, 255, 100))
        surface.blit(s, (draw_rect.x, draw_rect.y))

class LevelGenerator:
    def __init__(self):
        self.spires = []
        self.updrafts = []
        self.latest_y = SCREEN_HEIGHT  # Start generating from bottom
        
        # Initial ground platform
        self.spires.append(Spire(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40))
        
        # Generate initial chunk ahead of time
        self.generate_initial_spires()
        
    def generate_initial_spires(self):
        while self.latest_y > -SCREEN_HEIGHT * 2:
            self.spawn_spire()
            
    def spawn_spire(self):
        # Move up by a random interval
        interval = random.randint(120, 220)
        self.latest_y -= interval
        
        width = random.randint(80, 200)
        x = random.randint(0, SCREEN_WIDTH - width)
        y = self.latest_y
        
        self.spires.append(Spire(x, y, width, 20))
        
        # 30% chance to spawn an updraft
        if random.random() < 0.3:
            # Updraft sits on top of the spire, going up
            updraft_height = random.randint(150, 400)
            self.updrafts.append(Updraft(x, y - updraft_height, width, updraft_height))

    def update(self, camera_offset):
        # Generate new spires if we are getting close to the highest generated spire
        while self.latest_y > camera_offset - SCREEN_HEIGHT:
            self.spawn_spire()
            
        # Automatically remove spires out of view (too far below camera) to save memory
        removal_threshold = camera_offset + SCREEN_HEIGHT + 200
        
        self.spires = [s for s in self.spires if s.rect.top < removal_threshold]
        self.updrafts = [u for u in self.updrafts if u.rect.top < removal_threshold]

    def draw(self, surface, camera_offset):
        for spire in self.spires:
            spire.draw(surface, camera_offset)
        for updraft in self.updrafts:
            updraft.draw(surface, camera_offset)
