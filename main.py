import pygame, asyncio, sys, json, random


from scripts.utility import save_score, load_score, load_images_as_dic, Timer
from scripts.objects import RectButton, TextButton, GunChamber, TextSurf, SurfButton, Item
from scripts.entity import Player, Enemy
from scripts.items import skip, reveal, rotate, gamble
from scripts.gamestate import GameStateManager

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
        self.display = pygame.Surface((Game.WIDTH/Game.RENDER_SCALE, Game.HEIGHT/self.RENDER_SCALE))
        pygame.display.set_caption("6 Round Bluff")
        self.clock = pygame.Clock()

        #-------------Objects-------------

        #Buttons
        #pos = [self.display.get_width()-100,self.display.get_height() - 50] #coords are bottom right of screen
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
        self.gun_chamber.new_slots(random.randint(1,1))


        #Items
        self.item_textures = load_images_as_dic("items", True, '.png')
        self.item_names = list(self.item_textures.keys())

        print(random.choice(list(self.item_textures.keys())))
        #-------------Game vars-------------

        #Score
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

        self.death_text = TextSurf(sysfont=False, font_path= "fonts/yoster.ttf", size=40,
                                   text="You have died!", text_color="red", 
                                   pos= [0,0])
        self.death_text.pos = [self.window.get_width()//2 - self.death_text.surface.get_width()//2, self.window.get_width()* .2]


        #Vars
        self.turn = "player"


        #Game states
        self.gamestate_manager = GameStateManager("game loop")
        self.game_loop = GameLoop(self)
        self.get_item = GetItem(self)
        self.death_scene = DeathScene(self)

        self.states = {"game loop": self.game_loop, "get item": self.get_item, "death scene": self.death_scene}

        asyncio.run(self.run())

    async def run(self):

        while True:
            await asyncio.sleep(0)

            self.events = pygame.event.get()
            for event in self.events:
                if event.type == pygame.QUIT:
                    save_score("score/highscore.json", self.highscore)
                    pygame.quit()
                    sys.exit()

            self.states[self.gamestate_manager.get_state()].run(self)

            self.window.blit(pygame.transform.scale(self.display, self.window.get_size()))

            #Post display graphics
            self.score_surf.render(self.window)
            self.highscore_surf.render(self.window)
            if self.gamestate_manager.current_state == "death scene":
                self.death_text.render(self.window)

            pygame.display.update()
            self.clock.tick(60)
        
    def update_score(self):
        self.score_surf.change_text(f"Score: {self.score}", "black")
        self.score_surf.pos = [self.window.get_width()-self.score_surf.surface.get_width(),0]

    def update_highscore(self):
        self.highscore = max(self.highscore, self.score)
        save_score("score/highscore.json", self.highscore)

        self.highscore_surf.change_text(f"Highscore: {self.highscore}", "black")
        self.highscore_surf.pos = [self.window.get_width()-self.highscore_surf.surface.get_width(),self.highscore_surf.surface.get_height()]





class GameLoop:
    def __init__(self, game):
        self.gamestate_manager = game.gamestate_manager 
        self.enemy_turn_timer = Timer(2000)

    def run(self, game):

        self.inputs(game)
        self.graphics(game)

    def inputs(self, game): 
        if game.turn == "player" and not game.gun_chamber.rotating and not game.enemy.animating:
            self.player_turn(game)
        elif game.turn == "enemy" and not game.gun_chamber.rotating and not game.player.animating:
            self.enemy_turn(game)
    
    def player_turn(self, game):
        if game.shoot_button.check_clicked():
            if game.gun_chamber.slots[0] == "loaded":
                print("enemy dead")


                game.score += 1
                game.update_score()
                game.update_highscore()
                
                game.player.inventory.clear()
                self.decide_bullet_count(game)

                #game.player.animate_textures = game.player.shoot_textures

            elif game.gun_chamber.slots[0] == "blank":

                game.gun_chamber.rotating = True
                game.gun_chamber.slot_states[0] = "safe"
                game.enemy.update_chamber()
                game.gun_chamber.rotate_chamber()

                game.turn = "enemy"

            game.player.animate_textures = game.player.shoot_textures
            game.player.animating = True
            

        if game.shoot_self_button.check_clicked():
            if game.gun_chamber.slots[0] == "loaded":
                print("your dead")

                game.update_highscore()
     
                game.score = 0
                game.update_score()
                
                game.player.inventory.clear()
                self.decide_bullet_count(game)
                game.turn = "player"
                     
                self.gamestate_manager.set_state("death scene")

            elif game.gun_chamber.slots[0] == "blank":
                print("another turn")

                game.gun_chamber.rotating = True
                game.gun_chamber.slot_states[0] = "safe"
                game.gun_chamber.rotate_chamber()    

                #game.player.animate_textures = game.player.shoot_self_safe

            game.player.animate_textures = game.player.shoot_self_safe
            game.player.animating = True

    def enemy_turn(self, game):
         #Enemy Ai
        if game.enemy.decision() == "shoot player":
            if game.gun_chamber.slots[0] == "loaded":
                print("enemy has shot u")

                game.update_highscore()
                game.score = 0
                game.update_score()
                
                game.player.inventory.clear()
                self.decide_bullet_count(game)
                game.turn = "player"

                self.gamestate_manager.set_state("death scene")

                #game.enemy.animate_textures = game.enemy.shoot_textures

                
            else:
                print("enemy tried to shoot u")

                game.gun_chamber.rotating = True
                game.gun_chamber.slot_states[0] = "safe"
                game.gun_chamber.rotate_chamber()
                game.turn = "player"

            game.enemy.animate_textures = game.enemy.shoot_textures
            game.enemy.animating = True

        elif game.enemy.decision() == "shoot self":
            if game.gun_chamber.slots[0] == "loaded":
                print("enemy has shot themself to death")
                
                game.score += 1
                game.update_score()
                game.update_highscore()

                game.player.inventory.clear()
                self.decide_bullet_count(game)
                game.turn = "player"
            else:
                print("enemy tried to shoot themself")

                game.gun_chamber.rotating = True
                game.gun_chamber.slot_states[0] = "safe"
                game.gun_chamber.rotate_chamber()
                

                #game.enemy.animate_textures = game.enemy.shoot_self_safe

            game.enemy.animate_textures = game.enemy.shoot_self_safe
            game.enemy.animating = True

    def decide_bullet_count(self, game):
        
        minn = 1
        maxn = 1

        if game.score >= 18:
            minn = 2
            maxn = 5
        elif game.score >= 14:
            minn = 1
            maxn = 5
        elif game.score >= 10:
            minn = 1
            maxn = 4
        elif game.score >= 6:
            minn = 1
            maxn = 3
        elif game.score >= 2:
            minn = 1
            maxn = 2

        game.bullet_count = random.randint(minn, maxn)
        game.gun_chamber.new_slots(game.bullet_count)

    def graphics(self, game):
        game.display.fill((28, 31, 29))

        #Players
        game.player.render(game.display)
        game.enemy.render(game.display)

        #Buttons
        game.shoot_button.render(game.display)
        game.shoot_self_button.render(game.display)

        #Rotating animation
        if game.gun_chamber.rotating:
            game.gun_chamber.animate_rotate()
        game.gun_chamber.render(game.display)

        #Animation
        if game.player.animating:
            game.player.animate()

        if game.enemy.animating:
            game.enemy.animate()

        # #Items
        # if game.player.inventory:
        #     for item in game.player.inventory:
        #         item.render(game.display)

class GetItem:
    def __init__(self, game):
        self.gamestate_manager = game.gamestate_manager 

        
        self.starting_pos = [game.display.get_width()*.5 - (Game.item_size*1.5), (16 * 2.2)]
        self.seperation = 16
        self.create_items(2, game)

    def run(self, game):
        game.game_loop.graphics(game)

        for key, item in self.item_choices.items():
            item.render(game.display)
            
            #Add item to user inventory and exits out state
            if item.check_clicked():
                self.gamestate_manager.set_state("game loop")
                pos = [10, 16 * len(game.player.inventory) + (10 * len(game.player.inventory))]
                game.player.inventory.append(Item(game.item_textures[key], pos, Game.RENDER_SCALE, key))
                del self.item_choices
                self.create_items(2, game)
                print(game.player.inventory)
                return
    

    def create_items(self, count, game):
        self.item_choices = {}
        items = game.item_names.copy()
        for i in range(count):
            item = random.choice(items)
            items.remove(item)

            texture = game.item_textures[item]
            pos = [self.starting_pos[0] + (i * self.seperation) + (i *texture.get_width()), self.starting_pos[1]]
            self.item_choices[item] = Item(texture, pos, Game.RENDER_SCALE, item)



class DeathScene:
    def __init__(self, game):
        self.gamestate_manager = game.gamestate_manager 
        self.game = game

    def run(self, game):   
        
        for event in self.game.events:
            if event.type == pygame.QUIT:
                save_score("score/highscore.json", game.highscore)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    print("oututututut")
                    self.gamestate_manager.set_state("game loop")

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    print("oututututut")
                    self.gamestate_manager.set_state("game loop")

        #print("death")
        self.game.game_loop.graphics(self.game)
          



if __name__ == "__main__":
    game = Game()