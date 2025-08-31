import pygame, random

from scripts.utility import load_images

class Player:
    def __init__(self, path, pos):
        self.image = pygame.image.load(path).convert_alpha()
        self.pos = pos

        self.shoot_textures = load_images("player shoot")
        self.shoot_self_safe = load_images("player shoot self safe")
        self.with_gun_texture = self.shoot_textures[0]
        
        self.frame = 0
        self.frame_duration = 6
        self.inventory = []
        self.animating = False
        
        self.animate_textures = None
        self.current_texture = self.image

    def animate(self):

        #If its the last frame then end the animation
        if self.frame // self.frame_duration == len(self.animate_textures) - 1:
            self.frame = 0
            self.animating = False
            self.current_texture = self.image


        self.frame = (self.frame+1) % (len(self.animate_textures) * self.frame_duration)
        converted_frame = self.frame // self.frame_duration

        self.current_texture = self.animate_textures[converted_frame]

        
    
    def render(self, surface):
        surface.blit(self.current_texture, self.pos)

class Enemy:
    def __init__(self, path, pos):
        self.image = pygame.image.load(path).convert_alpha()

        self.shoot_textures = load_images("enemy shoot")
        self.shoot_self_safe = load_images("enemy shoot self safe")
        
        self.with_gun_texture = self.shoot_textures[0]

        self.pos = pos
        self.inventory = []

        self.chamber_state = ["unknown"] * 6

        self.frame = 0
        self.frame_duration = 6
        self.animating = False

        self.animate_textures = None
        self.current_texture = self.image

    def animate(self):

        converted_frame = self.frame // self.frame_duration
        #If its the last frame then end the animation
        if converted_frame == len(self.animate_textures) - 1:
            self.frame = 0
            self.animating = False


            self.current_texture = self.image
            
        elif self.frame == 0:
            self.pos[0] -= (self.animate_textures[0].get_width() - self.image.get_width())


        self.frame = (self.frame+1) % (len(self.animate_textures) * self.frame_duration)
        converted_frame = self.frame // self.frame_duration

        self.current_texture = self.animate_textures[converted_frame]

        

        

    def render(self, surface):
        surface.blit(self.current_texture, self.pos)

    def update_chamber(self):
        self.chamber_state[0] = "known"
        old_slots = self.chamber_state.copy()
        for index in range(-1, len(self.chamber_state)-1):
            self.chamber_state[index+1] = old_slots[index]

    def decision(self):
        #hit_chance = total_bullets/6

        #hit_chance = hit_chance * self.chamber_state.count("known") + hit_chance

        known_loaded = self.chamber_state.count("known")

        if self.chamber_state[0] == "loaded" or known_loaded >= 5:
            return "shoot player"
        elif known_loaded <= 4:
            return random.choice(['shoot player', 'shoot self'])
