import pygame

class Player:
    def __init__(self, size, pos,color):
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.pos = pos
    
    def render(self, surface):
        surface.blit(self.image, self.pos)

class Enemy:
    def __init__(self, size, pos, color):
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.pos = pos
    
    def render(self, surface):
        surface.blit(self.image, self.pos)