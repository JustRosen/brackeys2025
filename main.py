import pygame, asyncio, sys


class Game:
    #-------------Settings-------------
    WIDTH = 1100
    HEIGHT = 470
    SCALE = 2

    def __init__(self):
        #-------------Settings-------------
        pygame.init()
        self.WINDOW = pygame.display.set_mode((Game.WIDTH, Game.HEIGHT))
        pygame.display.set_caption("Brackeys 2025")
        self.clock = pygame.Clock()
        print("hello world")
        print("smth")
        
        asyncio.run(self.run())

    async def run(self):

        while True:
            await asyncio.sleep(0)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()


            self.WINDOW.fill("light green")
            pygame.display.update()
            self.clock.tick(60)

            


if __name__ == "__main__":
    game = Game()