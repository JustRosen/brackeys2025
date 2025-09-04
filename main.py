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
        self.display = pygame.Surface((Game.WIDTH//Game.RENDER_SCALE, Game.HEIGHT//Game.RENDER_SCALE))
        pygame.display.set_caption("6 Round Bluff")
        self.clock = pygame.Clock()

        #-------------Objects-------------

        #Buttons #Depreciated (meaning theyre not used anymore)
        #pos = [self.display.get_width()-100,self.display.get_height() - 50] #coords are bottom right of screen
        self.shoot_button = TextButton(sysfont=True, font_path="", size=10, text= "Shoot Enemy",
                                       pos=[0,0],
                                       text_color="red", 
                                       scale=Game.RENDER_SCALE)
        
        self.shoot_self_button = TextButton(True, font_path="", size=10, text="shoot self", text_color= "blue", 
                                            pos=[0,self.shoot_button.bg_surf.get_height() + 10], scale=Game.RENDER_SCALE)
    
        
        #Entities
        entity_height = 32
        pos = [self.display.get_width()*.3, int(self.display.get_height() - entity_height)-10]
        self.player = Player("assets/player.png", pos)
    

        pos = [self.display.get_width()*.7, int(self.display.get_height() - entity_height)-10]
        self.enemy = Enemy("assets/enemy.png", pos)

        #Gun Chamber
        self.gun_chamber = GunChamber(pos=[0,0])
        self.gun_chamber.pos = [self.display.get_width()//2 - self.gun_chamber.barrel.get_width()//2 ,10//Game.RENDER_SCALE]
        self.gun_chamber.new_slots(random.randint(1,1))


        #Items
        self.item_textures = load_images_as_dic("items", True, '.png')
        self.item_names = list(self.item_textures.keys())

        #Timers
        self.enemy_wait = Timer(5000)

    
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

            self.mpos = self.mouse_pos_in_display()

            self.events = pygame.event.get()
            for event in self.events:
                if event.type == pygame.QUIT:
                    save_score("score/highscore.json", self.highscore)
                    pygame.quit()
                    sys.exit()

                # if event.type == pygame.MOUSEBUTTONDOWN:
                #     if event.button == 1:
                #         pygame.draw.rect(self.window, "green", self.player.box)
                #         pygame.draw.rect(self.window, "red", self.enemy.box)
            self.states[self.gamestate_manager.get_state()].run(self)

            self.window.blit(pygame.transform.scale(self.display, self.window.get_size()), (0,0))

            #Post display graphics
            self.score_surf.render(self.window)
            self.highscore_surf.render(self.window)

            
            

            #Testing how items would look
            # for i in range(4):
            #     if i % 2:
            #         color = "black"
            #     else:
            #         color = "yellow"
            #     pygame.draw.rect(self.window, color, [[0,i*16*Game.RENDER_SCALE], [16*Game.RENDER_SCALE,16*Game.RENDER_SCALE]], border_radius= 10)

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


    def mouse_pos_in_display(self):
        mx, my = pygame.mouse.get_pos()
        sx = self.window.get_width()  / self.display.get_width()
        sy = self.window.get_height() / self.display.get_height()
        return [int(mx / sx), int(my / sy)]


class GameLoop:
    def __init__(self, game):
        self.gamestate_manager = game.gamestate_manager 
        self.enemy_wait = Timer(1500)

    def run(self, game):

        self.inputs(game)
        self.graphics(game)

    def inputs(self, game):
        for event in game.events:
            if event.type == pygame.QUIT:
                save_score("score/highscore.json", game.highscore)
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: #Left click
                    pass
                    #print("y", self.shoot_self_button.hitbox.y)
                    #print(pygame.mouse.get_pos())
                    pass
        

        
        if game.turn == "player" and not game.gun_chamber.rotating and not game.enemy.animating:
            self.player_turn(game)
        elif game.turn == "enemy" and not game.gun_chamber.rotating and not game.player.animating:
            #Wait a bit to create the illusion of the enemy deciding to make a choice
            if not self.enemy_wait.active:
                self.enemy_wait.activate()
            if self.enemy_wait.if_ready():
                self.enemy_turn(game)
    
    
    def player_turn(self, game):
        #Shooting enemy
        if game.enemy.check_clicked(game.mpos):
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
                game.gun_chamber.current_slot_status = "safe"
                game.enemy.update_chamber()
      

                game.turn = "enemy"

            
            game.player.animate_textures = game.player.shoot_textures
            game.player.animating = True
            
        #Shooting self
        elif game.player.check_clicked(game.mpos):
            if game.gun_chamber.slots[0] == "loaded":
                print("your dead")

                game.update_highscore()
     
                game.score = 0
                game.update_score()
                
                game.player.inventory.clear()
                self.decide_bullet_count(game)

                self.gamestate_manager.set_state("death scene")

            elif game.gun_chamber.slots[0] == "blank":


                game.gun_chamber.rotating = True
                game.gun_chamber.current_slot_status = "safe"

                game.turn = "enemy"       
                self.gamestate_manager.set_state("get item") 

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

                self.gamestate_manager.set_state("death scene")
                #game.enemy.animate_textures = game.enemy.shoot_textures

                
            else:
                print("enemy tried to shoot u")

                game.gun_chamber.rotating = True
                game.gun_chamber.current_slot_status = "safe"
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
                game.gun_chamber.current_slot_status = "safe"
                game.turn = "player"

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
        game.display.fill("dark grey")

        #Players
        game.player.render(game.display)
        game.enemy.render(game.display)

        #Animation
        if game.player.animating:
            game.player.animate()

        elif game.enemy.animating:
            game.enemy.animate()
        #Rotating animation
        elif game.gun_chamber.rotating:
            game.gun_chamber.animate_rotate()

        game.gun_chamber.render(game.display)


        #Items
        if game.player.inventory:
            for item in game.player.inventory:
                item.render(game.display)

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
            if item.check_clicked(game.mpos):
                self.gamestate_manager.set_state("game loop")
                pos = [10, 16 * len(game.player.inventory) + (10 * len(game.player.inventory))]
                game.player.inventory.append(Item(game.item_textures[key], pos, key))
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
            self.item_choices[item] = Item(texture, pos, item)



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