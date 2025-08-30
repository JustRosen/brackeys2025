import pygame, asyncio, sys


from scripts.objects import RectButton, TextButton, GunChamber
from scripts.entity import Player, Enemy

class Game:
    #-------------Settings-------------
    resolution = [640, 360] #16:9
    RENDER_SCALE = 2
    WIDTH = resolution[0] * RENDER_SCALE
    HEIGHT = resolution[1] * RENDER_SCALE   
    

    def __init__(self):
        #-------------Settings-------------
        pygame.init()
        self.window = pygame.display.set_mode((Game.WIDTH, Game.HEIGHT))
        self.display = pygame.Surface((Game.WIDTH/Game.RENDER_SCALE, Game.HEIGHT/self.RENDER_SCALE))
        pygame.display.set_caption("6 Round Bluff")
        self.clock = pygame.Clock()


        #Buttons
        pos = [self.display.get_width()-100,self.display.get_height() - 50] #coords are bottom right of screen
        self.shoot_button = TextButton(sysfont=True, font_path="", size=21, text= "Shoot Enemy",
                                       pos=[0,0],
                                       text_color="red", 
                                       scale=Game.RENDER_SCALE)
        
        self.shoot_self_button = TextButton(True, font_path="", size=21, text="shoot self", text_color= "blue", 
                                            pos=[0,self.shoot_button.bg_surf.get_height() + 10], scale=Game.RENDER_SCALE)
        
        #Entities
        self.player = Player([100,100], [100,150], "blue")
        self.enemy = Enemy((100,100), [400,150], "red")
        #Game vars
        self.gun_chamber = GunChamber()
        self.gun_chamber.new_slots(3)
        print(self.gun_chamber.slots)
        
        asyncio.run(self.run())

    async def run(self):

        while True:
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
            print("shooterrrrrr")

        if self.shoot_self_button.check_clicked():
            print("shot me self")


    def graphics(self):
        self.display.fill("light green")

        #Players
        self.player.render(self.display)
        self.enemy.render(self.display)

        #Buttons
        self.shoot_button.render(self.display)
        self.shoot_self_button.render(self.display)




            


if __name__ == "__main__":
    game = Game()