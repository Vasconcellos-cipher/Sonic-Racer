import pygame
import os
import random
import math
from PIL import Image, ImageSequence

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, speed=10):
        super().__init__()
        
        enemy_types = [
            ("crab.gif", 110, 85, "ground"),
            ("robotnik.gif", 125, 110, "flying"),
            ("ladybug.png", 95, 80, "flying"),
            ("butterdroid.gif", 105, 90, "flying")
        ]

        filename, w, h, self.enemy_type = random.choice(enemy_types)
        image_path = os.path.join("assets", "img", filename)

        self.frames = []

        if filename.endswith(".gif") and os.path.exists(image_path):
            pil_image = Image.open(image_path)
            for frame in ImageSequence.Iterator(pil_image):
                frame_rgba = frame.convert("RGBA")
                data = frame_rgba.tobytes()
                size = frame_rgba.size
                surf = pygame.image.fromstring(data, size, "RGBA")
                surf = pygame.transform.scale(surf, (w, h))
                self.frames.append(surf)
        elif os.path.exists(image_path):
            surf = pygame.image.load(image_path).convert_alpha()
            surf = pygame.transform.scale(surf, (w, h))
            self.frames.append(surf)
        else:
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(surf, (200, 0, 0), (0, 0, w, h))
            self.frames.append(surf)

        self.current_frame = 0
        self.animation_speed = 0.2
        self.image = self.frames[0]
        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect.x = 1300 + random.randint(30, 150)

        # Ajuste de altura no chão 680p
        if self.enemy_type == "ground":
            self.rect.bottom = 680
            self.base_y = 680
        else:
            self.base_y = random.randint(550, 595)
            self.rect.bottom = self.base_y

        self.speed = speed
        self.float_angle = random.uniform(0, 3.14)

    def update(self):
        if len(self.frames) > 1:
            self.current_frame += self.animation_speed
            if self.current_frame >= len(self.frames):
                self.current_frame = 0
            self.image = self.frames[int(self.current_frame)]
            self.mask = pygame.mask.from_surface(self.image)

        self.rect.x -= self.speed

        if self.enemy_type == "flying":
            self.float_angle += 0.08
            self.rect.bottom = int(self.base_y + math.sin(self.float_angle) * 14)

        if self.rect.right < 0:
            self.kill()