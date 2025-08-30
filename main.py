import pygame, asyncio, sys


from scripts.objects import RectButton, TextButton, GunChamber

class Game:
    #-------------Settings-------------
    resolution = [640, 360] #16:9
    RENDER_SCALE = 2
    WIDTH = resolution[0] * RENDER_SCALE
    HEIGHT = resolution[1] * RENDER_SCALE   
    
    

    def __init__(self):
        #-------------Settings-------------
        pygame.init()
        pygame.font.init()
        self.window = pygame.display.set_mode((Game.WIDTH, Game.HEIGHT))
        self.display = pygame.Surface((Game.WIDTH/Game.RENDER_SCALE, Game.HEIGHT/self.RENDER_SCALE))
        pygame.display.set_caption("6 Round Bluff")
        self.clock = pygame.Clock()
        self.kills = 0
        self.powerups = 0
        self.hp = True

        #Buttons
        pos = [self.display.get_width()-100,self.display.get_height() - 50] #coords are bottom right of screen
        self.shoot_button = RectButton([100,50], pos, "red", scale=Game.RENDER_SCALE)
        


        self.shoot_self_button = TextButton(True, font_path="", size=21, text="shoot self", text_color= "purple", 
                                            pos=[100,200], scale=Game.RENDER_SCALE)
        
        #Game vars
        self.gun_chamber = GunChamber()
        self.gun_chamber.new_slots(1)#the number represents the bullets
        print(self.gun_chamber.slots)
        
        asyncio.run(self.run())

    async def run(self):
        running = True
        while running:
            await asyncio.sleep(0)

            self.inputs()

            self.graphics()

            self.window.blit(pygame.transform.scale(self.display, self.window.get_size()))
            pygame.display.update()
            self.clock.tick(60)


    def inputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: #Left click
                    pass
                    #print("y", self.shoot_self_button.hitbox.y)
                    #print(pygame.mouse.get_pos())
                    pass


        if self.shoot_button.check_clicked():
            
            if len(self.gun_chamber.slots) == 0: #reloads the gun if no more bullets
                    print("reload")
                    self.gun_chamber.new_slots()

            if self.gun_chamber.slots[0] == "loaded": #checks if the gun is loaded while aimed at enemy
                print("gotteeeeeem")
                self.kills +=1
                self.gun_chamber.slots.pop(0)
            else:
                print("yea ggs you're cooked")#checks if the first bullet wasn't loaded
                self.gun_chamber.slots.pop(0)
            
        if self.shoot_self_button.check_clicked():
            if len(self.gun_chamber.slots) == 0:
                    print("reload")
                    self.gun_chamber.new_slots()
            
            elif self.gun_chamber.slots[0] == "blank":
                self.powerups += 1
                self.gun_chamber.slots.pop(0)
                
            elif self.gun_chamber.slots[0] == "loaded":
               
                print("ME BOMBA CLAT")
                self.hp = False
                
                
            
        
    def graphics(self):
        icon_width = 30
        icon_height = 30
        #image setup
        background = pygame.image.load("brackeys2025/assets/background.png")
        background = pygame.transform.scale(background,(self.WIDTH//2,self.HEIGHT//2))

        heart = pygame.image.load("brackeys2025/assets/heart.png") 
        heart = pygame.transform.scale(heart,(icon_width,icon_height))
        
        broken_heart = pygame.image.load("brackeys2025/assets/brokenheart.png") 
        broken_heart = pygame.transform.scale(broken_heart,(icon_width,icon_height))

        powerup1 = pygame.image.load("brackeys2025/assets/powerup1.png") 
        powerup1 = pygame.transform.scale(powerup1,(icon_width,icon_height))

        powerup2 = pygame.image.load("brackeys2025/assets/powerup2.png") 
        powerup2 = pygame.transform.scale(powerup2,(icon_width,icon_height))

        powerup3 = pygame.image.load("brackeys2025/assets/powerup3.png") 
        powerup3 = pygame.transform.scale(powerup3,(icon_width,icon_height))

        powerup4 = pygame.image.load("brackeys2025/assets/powerup4.png") 
        powerup4 = pygame.transform.scale(powerup4,(icon_width,icon_height))

        powerup5 = pygame.image.load("brackeys2025/assets/powerup5.png") 
        powerup5 = pygame.transform.scale(powerup5,(icon_width,icon_height))

        powerup6 = pygame.image.load("brackeys2025/assets/powerup6.png") 
        powerup6 = pygame.transform.scale(powerup6,(icon_width,icon_height))

        #text setup
        FONT = pygame.font.Font("brackeys2025/assets/Silver.ttf",40)
        kill_counter = FONT.render(str(self.kills), True, "black")
        text_rect = kill_counter.get_rect(center=(self.WIDTH//2*(0.07), self.HEIGHT//2*(0.05)))
        round = FONT.render(str(self.powerups), True, "black")
        round_rect = round.get_rect(center=(self.WIDTH//2*(0.07), self.HEIGHT//2*(0.228)))
        #what's on screen
        self.display.fill("white")
        self.display.blit(background,(0,0))
        self.shoot_button.render(self.display)

        self.shoot_self_button.render(self.display)
        self.display.blit(broken_heart,(0,0))
        self.display.blit(heart,(0,icon_height*2))
        self.display.blit(kill_counter,text_rect)
        self.display.blit(round,round_rect)

        



        #you blit depending on the powerups kill_counter 
        #these can go into a function and make them conditional
        self.display.blit(powerup1,(icon_height*20,icon_height*2))
        self.display.blit(powerup2,(icon_height*18.5,icon_height*2))
        self.display.blit(powerup3,(icon_height*17,icon_height*2))
        self.display.blit(powerup4,(icon_height*15.5,icon_height*2))
        self.display.blit(powerup5,(icon_height*14,icon_height*2))
        self.display.blit(powerup6,(icon_height*12.5,icon_height*2))

        #gameover screen
        if self.hp == False:
            gameover = FONT.render("Was it worth the biscuit?", True, "black","white")
            gameover_rect = gameover.get_rect(center=(self.WIDTH//2*(.5), self.HEIGHT//2*(.5)))
            self.display.blit(gameover,gameover_rect)
            gameover_button = TextButton("Silver.ttf","brackeys2025/assets/Silver.ttf",30,"Retry?","black",(225,250),1)
            gameover_button.render(self.display)

        
            if gameover_button.check_clicked():#retry button
                print("hi")
                
            
    

if __name__ == "__main__":
    game = Game()