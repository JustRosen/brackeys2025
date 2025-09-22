import pygame, random

from scripts.utility import load_images


class TextSurf:
    def __init__(self, sysfont, font_path, size, text, text_color, pos):
        
        #Font Attributes
        self.is_sysfont = sysfont
        self.path = font_path
        self.text = text
        self.pos = list(pos)
        self.color = text_color

        TextSurf.change_size(self, size)

        self.surface = self.font.render(text, True, text_color)
        

    def change_text(self, text, text_color):
        self.color = text_color
        self.text = text
        self.surface = self.font.render(text, True, text_color)

    def change_size(self, size):
        if self.is_sysfont:
            self.font = pygame.font.SysFont(self.path, size)
        else:
            self.font = pygame.font.Font(self.path, size)

        self.surface = self.font.render(self.text, True, self.color)

    def render(self, surface):
        surface.blit(self.surface, self.pos)


class TextButton(TextSurf):
        
    def __init__(self, sysfont, font_path, size, text, text_color, pos, scale):
        super().__init__(sysfont, font_path, size, text, text_color, pos)

        self.bg_surf = self.surface.copy()
        self.bg_surf.fill("white")
        #Note: a rect's pos&size needs to scale with the render scale
        #The pos matches with the one on the display surface not the main one (self.window)\
        hitbox_pos = [pos[0] * scale, pos[1] * scale]
        hitbox_size = [self.surface.get_width()* scale, self.surface.get_height()* scale]
        self.hitbox = pygame.Rect(hitbox_pos, hitbox_size)

        self.click_cooldown = False

    def check_clicked(self):
        mpos = pygame.mouse.get_pos()
        if self.hitbox.collidepoint(mpos) and not self.click_cooldown:
            if pygame.mouse.get_pressed()[0] == 1: #If left click #True prolly works too like "if True:""
                self.click_cooldown = True 
                return True
            
        if pygame.mouse.get_pressed()[0] == 0:
            self.click_cooldown = False
            return False

    def change_size(self, size):
        super().change_size(size)
        self.hitbox = self.surface.get_rect()
        self.hitbox.left = self.pos[0]
        self.hitbox.top = self.pos[1]

    def change_text(self, text, text_color):
        super().change_text(text, text_color)
        self.hitbox = self.surface.get_rect()
        self.hitbox.left = self.pos[0]
        self.hitbox.top = self.pos[1]


    def render(self, surface):
        surface.blit(self.bg_surf, self.pos)
        super().render(surface)
        
#This rect button has a surface bc i need to scale up the rect and the it wont match the image
class RectButton():
    def __init__(self, size, pos, color, scale):
        
        self.color = color
        self.pos = pos
        self.surface = pygame.Surface(size)
        self.surface.fill(color)

        self.box = pygame.Rect(pos[0]*scale, pos[1]*scale, size[0] * scale, size[1] * scale)
        self.clicked = False
    def render(self,surface):
        surface.blit(self.surface, self.pos)

    def check_clicked(self):
        action = False #Action will be returned to determine if the button was pressed or not

        mpos = pygame.mouse.get_pos()

        if self.box.collidepoint(mpos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                action = True

        if not pygame.mouse.get_pressed()[0]: #if it returns a 0 it means false
            self.clicked = False

        return action
    
class SurfButton:
    def __init__(self, image, pos):
        
        self.pos = pos
        self.surface = image.copy()

        self.box = pygame.Rect(pos[0], pos[1], self.surface.get_width(), self.surface.get_height())
        self.clicked = False

    def render(self,surface):
        surface.blit(self.surface, self.pos)

    def check_clicked(self, mpos):
        action = False #Action will be returned to determine if the button was pressed or not

        if self.box.collidepoint(mpos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                action = True

        if not pygame.mouse.get_pressed()[0]: #if it returns a 0 it means false
            self.clicked = False

        return action
    
class Item(SurfButton):
    def __init__(self, image, pos, type):
        super().__init__(image, pos)
        self.type = type


class GunChamber:
    def __init__(self, pos):
        self.state_textures = {
            "unknown": pygame.image.load("assets/chamber_states/unknown slot.png"),
            "loaded": pygame.image.load("assets/chamber_states/loaded slot.png"),
            "safe": pygame.image.load("assets/chamber_states/safe slot.png"),
        }

        self.rotate_textures = load_images("rotate")

        #The first slot is the top most and the next ones are in clockwise order
        self.slot_pos = [
            [12,2], #Top most
            [21,7], #Top right
            [21,17], #Bot right
            [12,22], #Bot most
            [3,16], #Bot left
            [3,7], #Top left
        ]

        #Note: tbh the slot attri might be redundent
        self.slots = ['blank']*6 #
        self.slot_states = ['unknown']*6 #Knowns all the states
        self.visible_states = ['unknown']*6 #Only shows visible states

        self.barrel = pygame.image.load("assets/gun_chamber.png")
        self.barrel_states = self.barrel.copy()
        self.current_texture = self.barrel_states
        self.pos = pos

        self.rotating = False
        self.frame = 0
        self.frame_duration = 5

        self.current_slot_status = "unknown"
  
    
    def new_slots(self, bullets=1):
        self.slots = ['blank']*6 
        self.slot_states = ['unknown']*6 
        self.visible_states = ['unknown']*6
        spots_left = [i for i in range(6)]

        for _ in range(bullets):
            spot = random.choice(spots_left)
            self.slots[spot] = "loaded"
            self.slot_states[spot] = "loaded"
            spots_left.remove(spot)
        
        self.add_state_textures()
    
    def rotate_chamber(self):
        old_slots = self.slots.copy()
        old_states = self.slot_states.copy()
        old_visible = self.visible_states.copy()
        for index in range(-1, len(self.slots)-1):
            self.slots[index+1] = old_slots[index]
            self.slot_states[index+1] = old_states[index]
            self.visible_states[index+1] = old_visible[index]
        self.add_state_textures()
        #print("new:", self.slots)

    def update_chamber(self, rotate = True):
        self.visible_states[0] = self.current_slot_status #Safe or unknown. It loaded then player just dies yk\
        if rotate:
            self.rotate_chamber()
    #Graphical

    def add_state_textures(self):
        self.barrel_states = self.barrel.copy()
        for index, state in enumerate(self.visible_states): #slot_states to know everything 
            texture = self.state_textures[state]
            pos = self.slot_pos[index]
            self.barrel_states.blit(texture, pos)

        self.current_texture = self.barrel_states

    #Note: The chamber does the rotating animation before updating to the new state
    def animate_rotate(self):
    
        #If its the last frame then end the animation
        max_frame = (len(self.rotate_textures) * self.frame_duration)
        #This makes sure its on the VERY last frame, i prev had it check the last "converted frame" 
        # so basically, the last frame would only last 1 second instead of the full frame duration
        if self.frame == max_frame - 1: 
            self.frame = 0
            self.rotating = False
            self.current_texture = self.barrel_states
            self.update_chamber()
            return

        self.frame = (self.frame+1) % max_frame
        converted_frame = self.frame // self.frame_duration

        self.current_texture = self.rotate_textures[converted_frame]

    def render(self, surface):
        surface.blit(self.current_texture, self.pos)

    def test_render(self, surface):
        color = "grey"
        sep = 20
        for index, bullet in enumerate(self.slots):
            if bullet == "loaded":
                color = "red"
            else:
                color = "grey"
            pos = [400 + (sep * index) + index * 40, 50]
            pygame.draw.rect(surface, color, pygame.Rect(pos, [40,40]))
        

    