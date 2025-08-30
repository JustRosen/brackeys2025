import pygame, asyncio, sys, json

from scripts.utility import save_score, load_score
from scripts.objects import RectButton, TextButton, GunChamber, TextSurf
from scripts.entity import Player, Enemy

class Game:
    #-------------Settings-------------
    resolution = [640, 360] #16:9
    RENDER_SCALE = 6
    WIDTH = resolution[0] * 2
    HEIGHT = resolution[1] * 2 
    

    def __init__(self):
        #-------------Settings-------------
        pygame.init()
        self.window = pygame.display.set_mode((Game.WIDTH, Game.HEIGHT))
        self.display = pygame.Surface((Game.WIDTH/Game.RENDER_SCALE, Game.HEIGHT/self.RENDER_SCALE))
        pygame.display.set_caption("6 Round Bluff")
        self.clock = pygame.Clock()

        #-------------Objects-------------
        #Buttons
        pos = [self.display.get_width()-100,self.display.get_height() - 50] #coords are bottom right of screen
        self.shoot_button = TextButton(sysfont=True, font_path="", size=10, text= "Shoot Enemy",
                                       pos=[0,0],
                                       text_color="red", 
                                       scale=Game.RENDER_SCALE)
        
        self.shoot_self_button = TextButton(True, font_path="", size=10, text="shoot self", text_color= "blue", 
                                            pos=[0,self.shoot_button.bg_surf.get_height() + 10], scale=Game.RENDER_SCALE)
    
        
        #Entities
        pos = [(self.display.get_width()*.1) * 3, self.display.get_height() - 32]
        self.player = Player("assets/player.png", pos)
        pos = [(self.display.get_width()*.1) * 7, self.display.get_height()- 32]
        self.enemy = Enemy("assets/enemy.png", pos)

        #Gun Chamber
        self.gun_chamber = GunChamber(pos=[0,0])
        self.gun_chamber.pos = [self.display.get_width()//2 - self.gun_chamber.barrel.get_width()//2 ,10//Game.RENDER_SCALE]
        self.gun_chamber.new_slots()
        print(self.gun_chamber.slots)


        #-------------Game vars-------------

        #text

        self.score = 0
        self.highscore = 0
        try:
            self.highscore = load_score("score/highscore.json")
        except FileNotFoundError:
            #Creates highscore save if non exist
            save_score("score/highscore.json", self.highscore)
        
        self.score_surf = TextSurf(sysfont=False, font_path= "fonts/yoster.ttf", size=30,
                                   text= f"Score: {self.score}", text_color="black",
                                   pos=[0,0])
        self.score_surf.pos = [self.window.get_width()-self.score_surf.surface.get_width(),0]

        self.highscore_surf = TextSurf(sysfont=False, font_path= "fonts/yoster.ttf", size=30,
                                   text= f"Highscore: {self.highscore}", text_color="black",
                                   pos=[0,0])
        self.highscore_surf.pos = [self.window.get_width()-self.highscore_surf.surface.get_width(),self.highscore_surf.surface.get_height()]

        self.turn = "player"


        asyncio.run(self.run())

    async def run(self):

        while True:
            await asyncio.sleep(0)

            self.inputs()

            self.graphics()

            self.window.blit(pygame.transform.scale(self.display, self.window.get_size()))

            #Post display graphics
            self.score_surf.render(self.window)
            self.highscore_surf.render(self.window)

            pygame.display.update()
            self.clock.tick(60)


    def inputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_score("score/highscore.json", self.highscore)
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: #Left click
                    pass
                    #print("y", self.shoot_self_button.hitbox.y)
                    #print(pygame.mouse.get_pos())
                    pass

        
        if self.turn == "player":
            self.player_turn()
        elif self.turn == "enemy":
            pygame.time.delay(1000)
            self.enemy_turn()
        


    def player_turn(self):
        if self.shoot_button.check_clicked():
            if self.gun_chamber.slots[0] == "loaded":
                print("enemy dead")


                self.score += 1
                self.update_score()
                self.update_highscore()
                

                self.gun_chamber.new_slots()
            else:
                self.gun_chamber.slot_states[0] = "safe"
                self.enemy.update_chamber()
                self.gun_chamber.rotate_chamber()
                self.turn = "enemy"

        if self.shoot_self_button.check_clicked():
            if self.gun_chamber.slots[0] == "loaded":
                print("your dead")

                self.update_highscore()
     
                self.score = 0
                self.update_score()
                
                self.gun_chamber.new_slots()

            elif self.gun_chamber.slots[0] == "blank":
                self.gun_chamber.slot_states[0] = "safe"
                self.gun_chamber.rotate_chamber()
                self.turn = "enemy"        

    def enemy_turn(self):
         #Enemy Ai
        if self.enemy.decision() == "shoot player":
            if self.gun_chamber.slots[0] == "loaded":
                print("enemy has shot u")

                self.update_highscore()
                self.score = 0
                self.update_score()
                
                self.gun_chamber.new_slots()
            else:
                print("enemy tried to shoot u")
                self.gun_chamber.slot_states[0] = "safe"
                self.gun_chamber.rotate_chamber()
                self.turn = "player"

        elif self.enemy.decision() == "shoot self":
            if self.gun_chamber.slots[0] == "loaded":
                print("enemy has shot themself to death")
                
                self.score += 1
                self.update_score()
                self.update_highscore()

                self.gun_chamber.new_slots()
                self.turn = "player"
            else:
                print("enemy tried to shoot themself")
                self.gun_chamber.slot_states[0] = "safe"
                self.gun_chamber.rotate_chamber()
                self.turn = "player"

    def update_score(self):
        self.score_surf.change_text(f"Score: {self.score}", "black")
        self.score_surf.pos = [self.window.get_width()-self.score_surf.surface.get_width(),0]

    def update_highscore(self):
        self.highscore = max(self.highscore, self.score)
        save_score("score/highscore.json", self.highscore)

        self.highscore_surf.change_text(f"Highscore: {self.highscore}", "black")
        self.highscore_surf.pos = [self.window.get_width()-self.highscore_surf.surface.get_width(),self.highscore_surf.surface.get_height()]



    def graphics(self):
        self.display.fill("dark grey")

        #Players
        self.player.render(self.display)
        self.enemy.render(self.display)

        #Score
        #self.score_surf.render(self.display)
        #Buttons
        self.shoot_button.render(self.display)
        self.shoot_self_button.render(self.display)

        self.gun_chamber.render(self.display)




            


if __name__ == "__main__":
    game = Game()