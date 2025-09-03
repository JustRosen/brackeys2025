import pygame, random, math

from scripts.utility import load_images

class Player:
    def __init__(self, path, pos):
        self.base_texture = pygame.image.load(path).convert_alpha()
        self.pos = pos.copy()
        self.og_pos = pos.copy()

        self.shoot_textures = load_images("player shoot")
        self.shoot_self_safe = load_images("player shoot self safe")
        self.with_gun_texture = self.shoot_textures[0]
        self.outlined_texture = self.outline_surface(self.with_gun_texture, "yellow")

        self.frame = 0
        self.frame_duration = 6
        self.inventory = []
        self.animating = False
        
        self.animate_textures = None
        self.current_texture = self.with_gun_texture #Current texture switches all the time
        self.is_turn = True

        rect_pos = [self.pos[0], self.pos[1]]
        rect_size = [ self.base_texture.get_width(), self.base_texture.get_height()]
        self.box = pygame.Rect(rect_pos, rect_size)


    def animate(self):
        
        #Very Last frame check
        max_frame = (len(self.animate_textures) * self.frame_duration)
        if self.frame == max_frame - 1:
            self.frame = 0
            self.animating = False
            self.current_texture = self.base_texture

            return
            
        self.frame = (self.frame+1) % (len(self.animate_textures) * self.frame_duration)
        converted_frame = self.frame // self.frame_duration

        self.current_texture = self.animate_textures[converted_frame]

    def check_clicked(self, mpos):
        action = False #Action will be returned to determine if the button was pressed or not

        if self.box.collidepoint(mpos):
            if not self.current_texture == self.outlined_texture:
                self.current_texture = self.outlined_texture
                #Ok so the outline is only 1 pixel big so im just gunna subtract it
                #I cant use the change texture function because the with gun texture actually has transparent pixel so that increases its width
                #so i cant just get the 1 pixel difference cuz it would be off
                #This is hard coded but tbh im kinda lazy and just wanna finish this
                self.pos[0] = self.og_pos[0] - 1
                self.pos[1] = self.og_pos[1] - 1

            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                action = True
                self.pos = self.og_pos.copy()
        else:
            if self.current_texture == self.outlined_texture or self.current_texture == self.base_texture:
                self.current_texture = self.with_gun_texture
                self.pos = self.og_pos.copy()

        if not pygame.mouse.get_pressed()[0]: #if it returns a 0 it means false
            self.clicked = False
            

        return action

    def change_current_texture(self, new_surf: pygame.Surface):
        self.pos = self.og_pos.copy()

        self.pos[0] -= new_surf.get_width() - self.base_texture.get_width()
        self.pos[1] -= new_surf.get_height() - self.base_texture.get_height()
        self.current_texture = new_surf
    
    def outline_surface(self, surface, color = 'black', outline_only = False):
        
        convolution_mask = pygame.mask.Mask((3, 3), fill = True)
        mask = pygame.mask.from_surface(surface)
        
        surface_outline = mask.convolve(convolution_mask).to_surface(setcolor = color, unsetcolor = surface.get_colorkey())
        
        if outline_only:
            mask_surface = mask.to_surface()
            mask_surface.set_colorkey('black')
            
            surface_outline.blit(mask_surface, (1, 1))
            
        else:
            surface_outline.blit(surface, (1, 1))
        
        return surface_outline

    def render(self, surface):
        surface.blit(self.current_texture, self.pos)

class Enemy:
    def __init__(self, path, pos):
        self.base_texture = pygame.image.load(path).convert_alpha()

        self.shoot_textures = load_images("enemy shoot")
        self.shoot_self_safe = load_images("enemy shoot self safe")
        self.with_gun_texture = self.shoot_textures[0]
        self.outlined_texture = self.outline_surface(self.base_texture, "yellow")

        self.pos = pos
        self.og_pos = pos.copy()
        self.inventory = []

        self.chamber_state = ["unknown"] * 6

        self.frame = 0
        self.frame_duration = 6
        self.animating = False

        self.animate_textures = None
        self.current_texture = self.base_texture

        rect_pos = [self.pos[0], self.pos[1]]
        rect_size = [ self.base_texture.get_width(), self.base_texture.get_height()]
        self.box = pygame.Rect(rect_pos, rect_size)

   
    def check_clicked(self, mpos):
        action = False #Action will be returned to determine if the button was pressed or not

        if self.box.collidepoint(mpos):
            if not self.current_texture == self.outlined_texture:
                self.change_current_texture(self.outlined_texture)
                #This is hard coded ik but bruuuv the textures are so wack, since the position of the surface is top left its wack if theres
                #extra space on the left, idk what would happen if i flipped the texture 
                #I just tested it and flipping the image would create the same problem
                self.pos[0] += 1
                self.pos[1] += 1

            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                action = True
                self.change_current_texture(self.base_texture)
        else:
            if self.current_texture == self.outlined_texture:
                self.change_current_texture(self.base_texture)

        if not pygame.mouse.get_pressed()[0]: #if it returns a 0 it means false
            self.clicked = False

        return action

    def change_current_texture(self, new_surf: pygame.Surface):
        self.pos = self.og_pos.copy()

        self.pos[0] -= new_surf.get_width() - self.base_texture.get_width()
        self.pos[1] -= new_surf.get_height() - self.base_texture.get_height()
        self.current_texture = new_surf
        
    
    #Graphical -------------
    def animate(self):

        #If its the last frame then end the animation
        max_frame = (len(self.animate_textures) * self.frame_duration)
        if self.frame == max_frame - 1:
            self.frame = 0
            self.animating = False
            self.current_texture = self.base_texture

            self.pos = self.og_pos.copy()
            return

            #self.pos[0] = self.og_pos[0] + (self.animate_textures[0].get_width() - self.image.get_width())
        elif self.frame == 0:
            self.pos[0] = self.og_pos[0] - (self.animate_textures[0].get_width() - self.base_texture.get_width())
            self.pos[1] = self.og_pos[1] - (self.animate_textures[0].get_height() - self.base_texture.get_height())


        self.frame = (self.frame+1) % max_frame
        converted_frame = self.frame // self.frame_duration

        self.current_texture = self.animate_textures[converted_frame]
     
        
    def outline_surface(self, surface, color = 'black', outline_only = False):
        
        convolution_mask = pygame.mask.Mask((3, 3), fill = True)
        mask = pygame.mask.from_surface(surface)
        
        surface_outline = mask.convolve(convolution_mask).to_surface(setcolor = color, unsetcolor = surface.get_colorkey())
        
        if outline_only:
            mask_surface = mask.to_surface()
            mask_surface.set_colorkey('black')
            
            surface_outline.blit(mask_surface, (1, 1))
            
        else:
            surface_outline.blit(surface, (1, 1))
        
        return surface_outline
    
    def render(self, surface):
        surface.blit(self.current_texture, self.pos)

    #Data
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
            return random.choice(['shoot self', 'shoot self'])
