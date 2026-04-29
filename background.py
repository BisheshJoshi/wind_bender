import pygame
import random
from settings import *

class Cloud:
    def __init__(self, x, y, speed_factor, size):
        self.x = x
        self.y = y
        self.speed_factor = speed_factor
        self.size = size

class Background:
    def __init__(self):
        self.clouds = []
        # Layer 1: Slow / Far, Layer 2: Medium / Mid, Layer 3: Fast / Close
        for i in range(25):
            self.spawn_cloud(-SCREEN_HEIGHT, SCREEN_HEIGHT * 2)

    def spawn_cloud(self, min_y, max_y):
        layer = random.randint(1, 3)
        if layer == 1:
            size_x = random.randint(40, 80)
            size_y = random.randint(20, 40)
            speed_factor = 0.2
        elif layer == 2:
            size_x = random.randint(80, 140)
            size_y = random.randint(30, 60)
            speed_factor = 0.5
        else:
            size_x = random.randint(140, 200)
            size_y = random.randint(50, 80)
            speed_factor = 0.8
            
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(min_y, max_y)
        self.clouds.append(Cloud(x, y, speed_factor, (size_x, size_y)))

    def update(self, camera_offset):
        # Constantly check if clouds are out of view below the screen
        # If so, cycle them back up above the camera to create infinite parallax
        for cloud in self.clouds:
            visual_y = cloud.y - (camera_offset * cloud.speed_factor)
            if visual_y > SCREEN_HEIGHT + 100:
                cloud.y -= (SCREEN_HEIGHT + 400)
                cloud.x = random.randint(-50, SCREEN_WIDTH)
            
    def draw(self, surface, camera_offset):
        for cloud in self.clouds:
            visual_y = cloud.y - (camera_offset * cloud.speed_factor)
            pygame.draw.ellipse(surface, (255, 255, 255, 128), (cloud.x, visual_y, cloud.size[0], cloud.size[1]))
