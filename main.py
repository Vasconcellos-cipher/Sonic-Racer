import pygame
import sys
import os

pygame.init()

WIDTH = 850
HEIGHT = 530
screen = pygame.display.set_mode((WIDTH, HEIGHT))

clock = pygame.time.Clock()

running = True

while running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    pygame.display.flip() 
            
pygame.quit()
sys.exit()

