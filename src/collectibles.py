import pygame
import math
import random

class Ring(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=10):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (255, 215, 0), (2, 2, 36, 36), 5)
        pygame.draw.ellipse(self.image, (255, 255, 224), (8, 8, 24, 24), 3)
        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed
        self.float_offset = random.uniform(0, 6.28)

    def update(self):
        self.rect.x -= self.speed
        self.float_offset += 0.1
        self.rect.y += int(math.sin(self.float_offset) * 2)
        if self.rect.right < 0:
            self.kill()

class Signpost(pygame.sprite.Sprite):
    def __init__(self, x=1350, ground_y=680, speed=8):
        super().__init__()
        self.width = 80
        self.height = 135
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        pygame.draw.rect(self.image, (160, 160, 160), (35, 55, 10, 80))
        pygame.draw.ellipse(self.image, (220, 20, 60), (5, 5, 70, 70))
        pygame.draw.circle(self.image, (255, 255, 255), (40, 40), 24)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = ground_y
        self.speed = speed
        self.is_passed = False

    def spin(self):
        if not self.is_passed:
            self.is_passed = True
            self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (160, 160, 160), (35, 55, 10, 80))
            pygame.draw.ellipse(self.image, (30, 144, 255), (5, 5, 70, 70))
            pygame.draw.circle(self.image, (255, 215, 0), (40, 40), 24)

    def update(self):
        self.rect.x -= self.speed