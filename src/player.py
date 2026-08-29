import os
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


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # 1. Animação Correndo
        run_path = resource_path(os.path.join("assets", "img", "sonic.gif"))
        self.run_frames = self._load_gif_frames(run_path, (175, 160))

        # 2. Frames de Giro no Pulo
        spin_path = resource_path(os.path.join("assets", "img", "girando.gif"))
        if not os.path.exists(spin_path):
            spin_path = resource_path(os.path.join("assets", "img", "destaque_sonic.gif"))

        if os.path.exists(spin_path):
            self.spin_frames = self._load_gif_frames(spin_path, (140, 140))
        else:
            self.spin_frames = self.run_frames

        # 3. Sprite Abaixado
        duck_path = resource_path(os.path.join("assets", "img", "sonic-down.png"))
        if not os.path.exists(duck_path):
            duck_path = resource_path(os.path.join("assets", "img", "abaixa.png"))

        if os.path.exists(duck_path):
            self.duck_image = pygame.image.load(duck_path).convert_alpha()
            self.duck_image = pygame.transform.scale(self.duck_image, (145, 105))
        else:
            self.duck_image = pygame.transform.scale(self.run_frames[0], (145, 100))

        # 4. Sprite Dano
        hit_path = resource_path(os.path.join("assets", "img", "contato-sonic.png"))
        if os.path.exists(hit_path):
            self.hit_image = pygame.image.load(hit_path).convert_alpha()
            self.hit_image = pygame.transform.scale(self.hit_image, (130, 130))
        else:
            self.hit_image = self.run_frames[0]

        self.current_frame = 0
        self.animation_speed = 0.28
        self.image = self.run_frames[0]
        self.mask = pygame.mask.from_surface(self.image)

        # Nível do Chão Calibrado para 720p de altura
        self.ground_stand = 680
        self.ground_duck = 650
        self.ground_y = self.ground_stand

        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.bottom = self.ground_y

        # Física do Personagem
        self.vel_y = 0
        self.gravity = 0.90
        self.jump_power = -21.0
        self.is_jumping = False
        self.is_ducking = False
        self.is_hit = False

        self.rings = 0
        self.invincible_timer = 0

    def _load_gif_frames(self, path, size):
        frames = []
        try:
            pil_image = Image.open(path)
            for frame in ImageSequence.Iterator(pil_image):
                frame_rgba = frame.convert("RGBA")
                data = frame_rgba.tobytes()
                s = frame_rgba.size
                surf = pygame.image.fromstring(data, s, "RGBA")
                surf = pygame.transform.scale(surf, size)
                frames.append(surf)
        except Exception:
            surf = pygame.Surface(size, pygame.SRCALPHA)
            pygame.draw.circle(surf, (0, 0, 255), (size[0] // 2, size[1] // 2), size[0] // 2)
            frames.append(surf)
        return frames

    def jump(self):
        if not self.is_jumping and not self.is_ducking and not self.is_hit:
            self.vel_y = self.jump_power
            self.is_jumping = True

    def cut_jump(self):
        if self.is_jumping and self.vel_y < -8:
            self.vel_y = -8

    def duck(self):
        if not self.is_jumping and not self.is_hit:
            self.is_ducking = True
            self.ground_y = self.ground_duck
            self.image = self.duck_image
            self.rect = self.image.get_rect(bottomleft=(self.rect.x, self.ground_y))
            self.mask = pygame.mask.from_surface(self.image)

    def stand_up(self):
        if self.is_ducking and not self.is_hit:
            self.is_ducking = False
            self.ground_y = self.ground_stand
            self.image = self.run_frames[int(self.current_frame)]
            self.rect = self.image.get_rect(bottomleft=(self.rect.x, self.ground_y))
            self.mask = pygame.mask.from_surface(self.image)

    def take_hit(self):
        if self.invincible_timer > 0:
            return False

        if self.rings > 0:
            self.rings = 0
            self.invincible_timer = 90
            self.vel_y = -9
            return False
        else:
            self.is_hit = True
            self.image = self.hit_image
            self.rect = self.image.get_rect(bottomleft=(self.rect.x, self.ground_y))
            self.vel_y = -11
            self.mask = pygame.mask.from_surface(self.image)
            return True

    def bounce(self):
        self.vel_y = -15
        self.is_jumping = True

    def update(self):
        if self.invincible_timer > 0:
            self.invincible_timer -= 1

        if self.is_hit:
            self.vel_y += self.gravity
            self.rect.y += self.vel_y
            if self.rect.bottom >= self.ground_y:
                self.rect.bottom = self.ground_y
                self.vel_y = 0
            return

        # Aplica gravidade e movimento vertical
        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        # Checagem de colisão com o chão
        if self.rect.bottom >= self.ground_y:
            self.rect.bottom = self.ground_y
            self.vel_y = 0
            self.is_jumping = False

        # Animações
        if self.is_jumping:
            self.current_frame += 0.35
            if self.current_frame >= len(self.spin_frames):
                self.current_frame = 0
            old_center = self.rect.center
            self.image = self.spin_frames[int(self.current_frame)]
            self.rect = self.image.get_rect(center=old_center)
            self.mask = pygame.mask.from_surface(self.image)
        elif not self.is_ducking:
            self.current_frame += self.animation_speed
            if self.current_frame >= len(self.run_frames):
                self.current_frame = 0
            old_x = self.rect.x
            self.image = self.run_frames[int(self.current_frame)]
            # Trava o pé do Sonic na superfície exata da grama (680)
            self.rect = self.image.get_rect(bottomleft=(old_x, self.ground_stand))
            self.mask = pygame.mask.from_surface(self.image)