import pygame, random

class Player:
    def __init__(self, path, pos):
        self.image = pygame.image.load(path).convert_alpha()
        self.pos = pos

        self.inventory = []
    
    def render(self, surface):
        surface.blit(self.image, self.pos)

class Enemy:
    def __init__(self, path, pos):
        self.image = pygame.image.load(path).convert_alpha()
        
        self.pos = pos

        self.chamber_state = ["unknown"] * 6
    
    def render(self, surface):
        surface.blit(self.image, self.pos)

    def update_chamber(self):
        self.chamber_state[0] = "known"
        old_slots = self.chamber_state.copy()
        for index in range(-1, len(self.chamber_state)-1):
            self.chamber_state[index+1] = old_slots[index]

    def decision(self):
        #hit_chance = total_bullets/6

        #hit_chance = hit_chance * self.chamber_state.count("known") + hit_chance

        known_loaded = self.chamber_state.count("known")

        if known_loaded >= 5:
            return "shoot player"
        elif known_loaded <= 4:
            return random.choice(['shoot player', 'shoot self'])
