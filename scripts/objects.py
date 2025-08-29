import pygame, random


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
    

class GunChamber:
    def __init__(self):
        self.slots = ['blank']*6
  
    
    def new_slots(self, bullets=1):
        self.slots = ['blank']*6 #Resets
        spots_left = [i for i in range(6)]

        for _ in range(bullets):
            spot = random.choice(spots_left)
            self.slots[spot] = "loaded"
            spots_left.remove(spot)

    