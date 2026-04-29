import pygame
import random

class Particle:
    def __init__(self, x, y, life):
        self.x = x
        self.y = y
        self.dx = random.uniform(-2, 2)
        self.dy = random.uniform(0, 3) # drift downwards mostly
        self.life = life
        self.max_life = life
        self.color = (255, 255, 255)
        
    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1
        
    def draw(self, surface, camera_offset):
        if self.life > 0:
            # simple alpha blending without creating surfaces every frame
            alpha = int((self.life / self.max_life) * 200)
            radius = int((self.life / self.max_life) * 5)
            s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (radius, radius), radius)
            surface.blit(s, (self.x - radius, self.y - camera_offset - radius))

class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def spawn_wind(self, x, y):
        # Spawn wind particles to act as trails
        life = random.randint(15, 30)
        self.particles.append(Particle(x, y, life))
        
    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]
        
    def draw(self, surface, camera_offset):
        for p in self.particles:
            p.draw(surface, camera_offset)