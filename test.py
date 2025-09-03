import pygame, sys

class Game:
    #-------------Settings-------------
    resolution = [640, 360] #16:9
    RENDER_SCALE = 5
    WIDTH = resolution[0] * 2
    HEIGHT = resolution[1] * 2 
    item_size = 16

    def __init__(self):
        #-------------Settings-------------
        pygame.init()
        self.window = pygame.display.set_mode((Game.WIDTH, Game.HEIGHT))
        self.display = pygame.Surface((Game.WIDTH//Game.RENDER_SCALE, Game.HEIGHT//Game.RENDER_SCALE))
        pygame.display.set_caption("6 Round Bluff")
        self.clock = pygame.Clock()

        self.enemy_gun = pygame.image.load('assets/enemy shoot/enemy0.png').convert_alpha()
        print("width", self.enemy_gun.get_width())

        self.flipped = self.enemy_gun.copy()
        self.flipped = pygame.transform.flip(self.flipped, True, False)
        self.flipped = pygame.transform.flip(self.flipped, True, False)

        self.run()


    def run(self):
        while True:


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.window.fill("white")

            self.window.blit(self.enemy_gun, (0,0) )
            self.window.blit(self.flipped, (0,32))

            pygame.display.update()
            self.clock.tick(60)



if __name__ == "__main__":
    game = Game()