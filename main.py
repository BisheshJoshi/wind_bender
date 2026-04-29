import sys
import random
import pygame

from settings import *
from level_generator import LevelGenerator
from background import Background
from particles import ParticleSystem

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.velocity = pygame.math.Vector2(0, 0)
        self.on_ground = False
        self.is_scooting = False
        self.prev_keys = pygame.key.get_pressed()

    def update(self, keys, spires, updrafts):
        accel = 1.2
        friction = 0.82
        
        self.velocity.x *= friction
        
        if keys[pygame.K_d]:
            self.velocity.x += accel
        if keys[pygame.K_a]:
            self.velocity.x -= accel

        just_pressed_space = keys[pygame.K_SPACE] and not self.prev_keys[pygame.K_SPACE]
        
        if just_pressed_space and self.on_ground:
            self.velocity.y = -12.0
            
        self.is_scooting = keys[pygame.K_LSHIFT] and self.on_ground and abs(self.velocity.x) > 0.5
        if self.is_scooting:
            # Air Scooter: double velocity x roughly
            if keys[pygame.K_d]:
                self.velocity.x = min(self.velocity.x + accel * 2, 10.0)
            if keys[pygame.K_a]:
                self.velocity.x = max(self.velocity.x - accel * 2, -10.0)

        # Gravity and Glide
        is_gliding = keys[pygame.K_SPACE] and self.velocity.y > 0 and not self.on_ground
        if is_gliding:
            self.velocity.y = min(self.velocity.y + GRAVITY, 2.0)
        else:
            self.velocity.y += GRAVITY
            
        self.move_and_collide(spires, updrafts)
        self.prev_keys = keys

    def move_and_collide(self, spires, updrafts):
        self.rect.x += self.velocity.x
        
        for spire in spires:
            if self.rect.colliderect(spire.rect):
                if self.velocity.x > 0:
                    self.rect.right = spire.rect.left
                elif self.velocity.x < 0:
                    self.rect.left = spire.rect.right
                self.velocity.x = 0

        self.rect.y += self.velocity.y
        self.on_ground = False
        
        for spire in spires:
            if self.rect.colliderect(spire.rect):
                if self.velocity.y > 0:
                    self.rect.bottom = spire.rect.top
                    self.velocity.y = 0
                    self.on_ground = True
                elif self.velocity.y < 0:
                    self.rect.top = spire.rect.bottom
                    self.velocity.y = 0

        for updraft in updrafts:
            if self.rect.colliderect(updraft.rect):
                self.velocity.y = -12.0
                break
                
        # Basic floor
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity.y = 0
            self.on_ground = True

    def draw(self, surface, camera_offset):
        draw_rect = self.rect.copy()
        
        stretch_factor = abs(self.velocity.y) * 0.03
        if self.on_ground:
            width, height = 40, 40
        else:
            width = int(40 * (1 - stretch_factor))
            height = int(40 * (1 + stretch_factor))
            
        width = max(20, min(60, width))
        height = max(20, min(60, height))
        
        draw_rect.width = width
        draw_rect.height = height
        draw_rect.midbottom = self.rect.midbottom
        
        draw_rect.y -= camera_offset
        pygame.draw.rect(surface, PLAYER_COLOR, draw_rect)

# Initialize pygame
pygame.init()

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Airbender Spires")
    clock = pygame.time.Clock()

    # Initialize game objects
    player = Player(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT - 100)
    level_gen = LevelGenerator()
    background = Background()
    particle_system = ParticleSystem()
    
    # Camera setup
    camera_offset = 0

    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Get key states for the frame
        keys = pygame.key.get_pressed()

        # --- Update Game State ---
        player.update(keys, level_gen.spires, level_gen.updrafts)
        level_gen.update(camera_offset)
        background.update(camera_offset)
        particle_system.update()

        # Particles from Air Scooter or Updrafts
        in_updraft = any(player.rect.colliderect(u.rect) for u in level_gen.updrafts)
        if player.is_scooting or in_updraft:
            # Spawn multiple particles for thicker effect
            for _ in range(3):
                particle_system.spawn_wind(player.rect.centerx + random.uniform(-10, 10), player.rect.bottom)

        # Update camera offset to follow player vertically
        # Adjust so the player stays around the middle/bottom third of the screen
        target_camera_y = player.rect.y - (SCREEN_HEIGHT // 2)
        
        # Only scroll up (prevent going back down a vertical platformer)
        if target_camera_y < camera_offset:
            camera_offset = target_camera_y

        # --- Rendering ---
        screen.fill(SKY_BLUE)

        background.draw(screen, camera_offset)
        level_gen.draw(screen, camera_offset)
        particle_system.draw(screen, camera_offset)
        player.draw(screen, camera_offset)

        # Update display
        pygame.display.flip()
        
        # Cap frame rate
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
