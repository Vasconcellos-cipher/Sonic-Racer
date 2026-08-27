import pygame
import sys
import os

pygame.init()

WIDTH = 850
HEIGHT = 530
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sonic Race Remastered")

bg_path = os.path.join("assets", "img", "background.png")
background = pygame.image.load(bg_path).convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
bg_x = 0
bg_speed = 3

clock = pygame.time.Clock()

running = True

while running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    bg_x -= bg_speed
    if bg_x <= -WIDTH:
        bg_x = 0
        
    screen.blit(background, (bg_x, 0))
    screen.blit(background, (bg_x + WIDTH, 0))
        
    pygame.display.flip() 
            
pygame.quit()
sys.exit()

