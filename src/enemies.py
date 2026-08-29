import math
import os
import random
import sys
import pygame
from PIL import Image, ImageSequence


def resource_path(relative_path):
    """Garante o carregamento das imagens tanto no VS Code quanto dentro do .exe PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, speed=10):
        super().__init__()

        enemy_types = [
            ("crab.gif", 110, 85, "ground"),
            ("robotnik.gif", 125, 110, "flying"),
            ("ladybug.png", 95, 80, "flying"),
            ("butterdroid.gif", 105, 90, "flying"),
        ]

        filename, w, h, self.enemy_type = random.choice(enemy_types)
        image_path = resource_path(os.path.join("assets", "img", filename))

        self.frames = []

        if filename.endswith(".gif") and os.path.exists(image_path):
            try:
                pil_image = Image.open(image_path)
                for frame in ImageSequence.Iterator(pil_image):
                    frame_rgba = frame.convert("RGBA")
                    data = frame_rgba.tobytes()
                    size = frame_rgba.size
                    surf = pygame.image.fromstring(data, size, "RGBA")
                    surf = pygame.transform.scale(surf, (w, h))
                    self.frames.append(surf)
            except Exception:
                pass
        elif os.path.exists(image_path):
            try:
                surf = pygame.image.load(image_path).convert_alpha()
                surf = pygame.transform.scale(surf, (w, h))
                self.frames.append(surf)
            except Exception:
                pass

        # Fallback se a imagem não carregar
        if not self.frames:
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(surf, (200, 0, 0), (0, 0, w, h))
            self.frames.append(surf)

        self.current_frame = 0
        self.animation_speed = 0.2
        self.image = self.frames[0]
        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect.x = 1300 + random.randint(30, 150)

        # Calibragem da base: 645 coloca as patas do caranguejo em cima da grama
        if self.enemy_type == "ground":
            self.base_y = 645
            self.rect.bottom = self.base_y
        else:
            self.base_y = random.randint(530, 580)
            self.rect.bottom = self.base_y

        self.speed = speed
        self.float_angle = random.uniform(0, 3.14)

    def update(self):
        old_x = self.rect.x

        if len(self.frames) > 1:
            self.current_frame += self.animation_speed
            if self.current_frame >= len(self.frames):
                self.current_frame = 0
            self.image = self.frames[int(self.current_frame)]
            self.mask = pygame.mask.from_surface(self.image)

        # Atualiza a posição horizontal
        self.rect.x = old_x - self.speed

        # Mantém a altura correta (flutuação para voadores e grama para terrestres)
        if self.enemy_type == "flying":
            self.float_angle += 0.08
            self.rect.bottom = int(self.base_y + math.sin(self.float_angle) * 14)
        else:
            self.rect.bottom = self.base_y

        if self.rect.right < 0:
            self.kill()