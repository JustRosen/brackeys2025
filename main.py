import pygame, asyncio, sys, json, random, pprint


from scripts.utility import save_score, load_score, load_images_as_dic, Timer
from scripts.objects import RectButton, TextButton, GunChamber, TextSurf, SurfButton, Item, ItemDescription, Floor
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

        pygame.display.set_caption("6 Round Bluff")
        pygame.display.set_icon(pygame.image.load("assets/game icon.png"))
        self.window = pygame.display.set_mode((Game.WIDTH, Game.HEIGHT))
        self.display = pygame.Surface((Game.WIDTH//Game.RENDER_SCALE, Game.HEIGHT//Game.RENDER_SCALE))
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
        entity_width = 11
        tilesize = 16
        pos = [tilesize * 5, (tilesize*8) - entity_height]
        self.player = Player("assets/player.png", pos)
    
        #Its 16 - entity_width = 5
        pos = [tilesize * 10 + (16 - entity_width), (16*8) - entity_height]
        self.enemy = Enemy("assets/enemy.png", pos)

        #Gun Chamber
        self.gun_chamber = GunChamber(pos=[0,0])
        self.gun_chamber.pos = [self.display.get_width()//2 - self.gun_chamber.barrel.get_width()//2 ,10//Game.RENDER_SCALE]
        self.gun_chamber.new_slots(random.randint(1,1))
        

        #Items
        self.item_textures = load_images_as_dic("items", True, '.png')
        self.item_names = list(self.item_textures.keys())
        self.item_func_reference = {
            "reveal": reveal,
            "gamble": gamble,
            "rotate": rotate,
            "skip": skip,
        }

        #Item descriptions
        with open("description/item_descriptions.json", 'r') as file:
            self.item_descriptions = json.load(file)

        self.descriptions_surf = {
            'reveal': ItemDescription(sysfont=False, font_path= "fonts/yoster.ttf", size=15,
                               text= self.item_descriptions['reveal'], text_color="black", pos=[0,0]),
            'gamble': ItemDescription(sysfont=False, font_path= "fonts/yoster.ttf", size=15,
                               text= self.item_descriptions['gamble'], text_color="black", pos=[0,50]),
            'rotate': ItemDescription(sysfont=False, font_path= "fonts/yoster.ttf", size=15,
                               text= self.item_descriptions['rotate'], text_color="black", pos=[0,100]),
            'skip': ItemDescription(sysfont=False, font_path= "fonts/yoster.ttf", size=15,
                               text= self.item_descriptions['skip'], text_color="black", pos=[0,200]),
        }

        #Loaded text
        #Position is right of the chamber 
        loaded_pos = [Game.WIDTH//2 + (self.gun_chamber.barrel.get_width()//2 * Game.RENDER_SCALE) + 10, self.gun_chamber.barrel.get_height()//2 * Game.RENDER_SCALE]
        self.total_loaded_text = TextSurf(sysfont=False, font_path= "fonts/yoster.ttf", size=25, 
                                          text= f"{self.gun_chamber.total_loaded} bullets", text_color="black", pos=loaded_pos)
        
        #Floor
        #16 * 8 = tilesize * tilecord
        self.floor = Floor((16,16), (16,1), (0,16*8))
        self.background = pygame.image.load("assets/background/background.png").convert_alpha()

        
        #-------------Sounds-------------

        #Background music
        pygame.mixer.music.load("sounds/eerie music.ogg")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        self.gun_shot = pygame.mixer.Sound("sounds/shot_sound.wav")
        self.gun_click = pygame.mixer.Sound("sounds/revolver click.wav")

        self.eerie_static = pygame.mixer.Sound("sounds/eerie static.wav")
        self.eerie_static.set_volume(.6)


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
        
        self.death_txt_color = (217, 13, 13)
        self.death_text = TextSurf(sysfont=False, font_path= "fonts/yoster.ttf", size=40,
                                   text="You have died!", text_color= self.death_txt_color, 
                                   pos= [0,0])
        self.death_text.pos = self.set_death_text_pos()


        #Vars
        self.turn = "player"
        self.who_is_dead = None
        self.hover_status = {"is hovering": False, "type": None, "in inventory": None, "pos rect": None}

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
                self.states[self.gamestate_manager.get_state()].handle_events(game=self, event=event)

            self.states[self.gamestate_manager.get_state()].run(self)

            self.window.blit(pygame.transform.scale(self.display, self.window.get_size()), (0,0))

            #Post display graphics

            #Score
            self.score_surf.render(self.window)
            self.highscore_surf.render(self.window)

            #Death text
            if self.gamestate_manager.get_state() == "death scene" and not self.player.animating and not self.enemy.animating:
                self.death_text.render(self.window)

            #Item description
            if self.hover_status["is hovering"]:

                description = self.descriptions_surf[self.hover_status['type']]
                item_pos = self.hover_status['pos rect']
                if self.hover_status["in inventory"]:
                    #Positions to right of item
                    #Do not do this in the future, find a way to make fonts look better when scaled instead of using the window
                    description.bg_rect.x = (item_pos.right + 5) * Game.RENDER_SCALE 
                    description.bg_rect.centery = item_pos.centery * Game.RENDER_SCALE
                    
                elif not self.hover_status["in inventory"]:
                    #Positions at the bottom of item
                    description.bg_rect.centerx = item_pos.centerx * Game.RENDER_SCALE 
                    description.bg_rect.y = (item_pos.bottom + 5) * Game.RENDER_SCALE 

                description.center_text_to_bg()
                description.render(self.window)

            #Amount of loaded bullets
            self.total_loaded_text.render(self.window)
            
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

    def set_death_text_pos(self):
        return [self.window.get_width()//2 - self.death_text.surface.get_width()//2,self.window.get_width()* .2]
    
class GameLoop:
    def __init__(self, game):
        self.gamestate_manager = game.gamestate_manager 
        self.enemy_wait = Timer(2000)

        self.item_cooldown = Timer(500)
        self.item_cooldown.activate() #Pre readies button

        #For dramatic effect of waiting a bit before pulling the trigger
        self.trigger_min = 1000
        self.trigger_max = 2000
        self.trigger_wait_timer = Timer(random.randint(self.trigger_min, self.trigger_max)) #3-6 seconds
        self.waiting_for_trigger = False
        self.wait_for_turn = False

        self.current_entity = game.player
        self.change_scene_to = "none"

    def run(self, game):
        #Turns
        if game.turn == "player" and not game.gun_chamber.rotating and not game.enemy.animating and not self.waiting_for_trigger and not self.wait_for_turn:
            self.current_entity = game.player
            self.player_turn(game)
        #game.turn = "player"
        elif game.turn == "enemy" and not game.gun_chamber.rotating and not game.player.animating and not self.waiting_for_trigger:
            self.current_entity = game.enemy

            #Wait a bit to create the illusion of the enemy deciding to make a choice
            if not self.enemy_wait.active:
                print("activated enemy timer")
                self.enemy_wait.activate()

            if self.enemy_wait.if_ready():
                print("ready for enemy tunr")
                self.enemy_turn(game)


        self.trigger_wait_effect(game)

        #Item use
        if game.turn == "player" and not game.enemy.animating and not self.waiting_for_trigger:
            for item in game.player.inventory:
                if item.check_clicked(game.mpos, game.hover_status) and self.item_cooldown.if_ready():
                    self.item_cooldown.activate()
                    game.item_func_reference[item.type](game) #Call item function
                    game.player.inventory.remove(item)
                    game.player.update_items()
                    break
        
        self.graphics(game)

    def handle_events(self, game, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: #Left click
                #print(game.gun_chamber.current_slot_status)
                #print("y", self.shoot_self_button.hitbox.y)
                #print(pygame.mouse.get_pos())
                pass  
    
    def player_turn(self, game):
        #Shooting enemy
        if game.enemy.check_clicked(game.mpos):
            if game.gun_chamber.slots[0] == "loaded":
                print("enemy dead")
                
                game.who_is_dead = "enemy"
                game.death_scene.dead_entity = game.enemy
                game.death_text.change_text("You have killed the enemy..", game.death_txt_color)
                game.death_text.pos = game.set_death_text_pos()
                game.player.animate_textures = game.player.shoot_textures

                self.change_scene_to = "death scene"

            elif game.gun_chamber.slots[0] == "blank":

                game.gun_chamber.rotating = True
                game.gun_chamber.current_slot_status = "safe"
                game.enemy.update_chamber()
                game.player.animate_textures = game.player.blank_shot_textures

            game.turn = "enemy"
            self.wait_for_turn = True
            game.player.animating = True
            
        #Shooting self
        elif game.player.check_clicked(game.mpos):
            if game.gun_chamber.slots[0] == "loaded":
                print("u shot urself dead")

                game.gun_chamber.current_slot_status = "loaded"
                game.who_is_dead = "player"
                game.death_scene.dead_entity = game.player
                game.death_text.change_text("You are dead!", game.death_txt_color)
                game.death_text.pos = game.set_death_text_pos()
                self.change_scene_to = "death scene"
                game.player.blank_shot = False

            elif game.gun_chamber.slots[0] == "blank":


                game.gun_chamber.rotating = True
                game.gun_chamber.current_slot_status = "safe"
                game.enemy.update_chamber()

                if game.gun_chamber.visible_states[0] == "unknown":
                    self.change_scene_to = "get item"

            game.turn = "enemy"
            self.wait_for_turn = True
            game.player.animate_textures = game.player.shoot_self
            game.player.animating = True

    def enemy_turn(self, game):
        #Enemy Ai
        if game.enemy.decision() == "shoot player":
            if game.gun_chamber.slots[0] == "loaded":
                print("enemy has shot u")

                
                game.gun_chamber.current_slot_status = "loaded"
                
                game.who_is_dead = "player"
                game.death_scene.dead_entity = game.player
                game.death_text.change_text("You are dead!", game.death_txt_color)
                game.death_text.pos = game.set_death_text_pos()
                self.change_scene_to = "death scene"

                game.enemy.animate_textures = game.enemy.shoot_textures
            else:
                print("enemy tried to shoot u")

                game.gun_chamber.rotating = True
                game.gun_chamber.current_slot_status = "safe"
                game.enemy.update_chamber()
                #game.turn = "player"

                game.enemy.animate_textures = game.enemy.blank_shot_textures



        elif game.enemy.decision() == "shoot self":
            if game.gun_chamber.slots[0] == "loaded":
                print("enemy has shot themself to death")
                

                game.who_is_dead = "enemy"
                game.death_scene.dead_entity = game.enemy
                game.death_text.change_text("The enemy is dead..", game.death_txt_color)
                game.death_text.pos = game.set_death_text_pos()
                game.enemy.blank_shot = False
                self.change_scene_to = "death scene"

            else:
                print("enemy tried to shoot themself")

                game.gun_chamber.rotating = True
                game.gun_chamber.current_slot_status = "safe"
                game.enemy.update_chamber()

            game.enemy.animate_textures = game.enemy.shoot_self

        game.turn = "player"
        self.wait_for_turn = True
        game.enemy.animating = True

    def decide_bullet_count(self, game):
        
        minn = 1
        maxn = 1

        if game.score >= 10:
            minn = 1
            maxn = 4
        elif game.score >= 6:
            minn = 1
            maxn = 3
        elif game.score >= 2:
            minn = 1
            maxn = 2

        game.gun_chamber.new_slots(random.randint(minn, maxn))

    def trigger_wait_effect(self, game):
        
        #First we need to stop on the correct frame
        #shooting self/ shooting blank = last frame
        #Shooting rival = 4th frame

        if not self.trigger_wait_timer.active:
            if (self.current_entity.animate_textures == self.current_entity.shoot_self
                or self.current_entity.animate_textures == self.current_entity.blank_shot_textures):
                #print("blank or self textures")
                #Last frame check. It would be better to do -1 but that cause a slight visually bug so imma leave it at 2
                # -2 with a frame duration of 1 leaves the entity at the 2nd last frame
                #But -1 with frame duration of 1 also creates the bug. for now imma just let the bug be
                if self.current_entity.frame == (len(self.current_entity.animate_textures) * self.current_entity.frame_duration) - 2:  
                    print("timer actived for blank or self")
                    self.trigger_wait_timer.activate()
                    self.current_entity.animating = False
                    self.waiting_for_trigger = True

            #Shooting rival
            elif self.current_entity.animate_textures == self.current_entity.shoot_textures:
                if self.current_entity.frame == 3 * self.current_entity.frame_duration:
                    self.trigger_wait_timer.activate()
                    self.current_entity.animating = False
                    self.waiting_for_trigger = True

        if self.trigger_wait_timer.if_ready():
            if not self.change_scene_to == "death scene":
                game.gun_click.play()


            self.current_entity.animating = True
            self.waiting_for_trigger = False
            self.trigger_wait_timer.duration = random.randint(self.trigger_min,self.trigger_max)
            self.wait_for_turn = False
            #Changes the scene
            if not self.change_scene_to == "none":
                self.gamestate_manager.set_state(self.change_scene_to)
                self.change_scene_to = "none"

    def graphics(self, game):
        #Background
        game.display.blit(game.background)
        #game.display.fill((35, 36, 35))
        #game.floor.render(game.display)

        #Players
        game.player.render(game.display)
        game.enemy.render(game.display)

        #Animation
        if game.player.animating:
            game.player.animate()

        if game.enemy.animating:
            game.enemy.animate()

        #Rotating animation
        if game.gun_chamber.rotating and not self.waiting_for_trigger and not game.player.animating and not game.enemy.animating:
            game.gun_chamber.animate_rotate()

        game.gun_chamber.render(game.display)


        #Items
        for item in game.player.inventory:
            item.render(game.display)

class GetItem:
    def __init__(self, game):
        self.gamestate_manager = game.gamestate_manager 
        self.game = game
        
        self.starting_pos = [game.display.get_width()*.5 - (Game.item_size*1.5), (16 * 2.2)]
        self.seperation = 16
        self.create_items(2, game)
    

    def handle_events(self,game, event):
        pass

    def run(self, game):
        game.game_loop.graphics(game)

        if not self.game.player.animating and not self.game.enemy.animating:
            self.show_items()

    def show_items(self):
        for key, item in self.item_choices.items():
            item.render(self.game.display)
            
            #Add item to user inventory and exits out state
            if item.check_clicked(self.game.mpos, self.game.hover_status):
                self.gamestate_manager.set_state("game loop")
                pos = [10, 16 * len(self.game.player.inventory) + (10 * len(self.game.player.inventory))]
                self.game.player.inventory.append(Item(self.game.item_textures[key], pos, key))
                self.game.player.update_items()

                #Add new itmes
                del self.item_choices
                self.create_items(2, self.game)
                
                return
    

    def create_items(self, count, game):
        self.item_choices = {}
        items = game.item_names.copy()
        for i in range(count):
            item = random.choice(items)
            items.remove(item)

            texture = game.item_textures[item]
            pos = [self.starting_pos[0] + (i * self.seperation) + (i *texture.get_width()), self.starting_pos[1]]
            self.item_choices[item] = Item(texture, pos, item, False)

class DeathScene:
    def __init__(self, game):
        self.gamestate_manager = game.gamestate_manager 
        self.game = game
        self.dead_entity = None


    def handle_events(self, game, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.exit_death()
                

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.exit_death()
                

    def run(self, game):   
            
        #print("death")
        self.game.game_loop.graphics(self.game)

        #Does the death animation when the previous animation is done
        play_death = (not self.dead_entity.animate_textures == self.dead_entity.shot_death 
                    and not self.game.player.animating and not self.game.enemy.animating)
        if self.play_death():
            #Animation
            self.dead_entity.animate_textures = self.dead_entity.shot_death
            self.dead_entity.animating = True
            self.dead_entity.texture_after_animation = self.dead_entity.shot_death[-1]

            #Updated chamber
            game.gun_chamber.current_slot_status = "loaded"
            game.gun_chamber.update_chamber(False)
            game.gun_chamber.add_state_textures()

            #Eerie sound
            pygame.mixer.music.stop()
            self.game.gun_shot.play()
            self.game.eerie_static.play(-1)

    def play_death(self):
        
        #If death animation already played
        if self.dead_entity.texture_after_animation == self.dead_entity.shot_death[-1]:
            return False
        
        #If entity shots himself
        elif self.dead_entity.animate_textures == self.dead_entity.shoot_self and not self.dead_entity.animating:
            return True
        
        #If Entity gets shot, it syncs the death animation with the bullet shot animation by starting the death animation before it finishes
        elif not self.dead_entity.animate_textures == self.dead_entity.shoot_self:
            return True
        
        return False
    
    def exit_death(self):
        #When animation is done exit death scree
        if not self.game.player.animating and not self.game.enemy.animating:
            

            if self.game.who_is_dead == "player":
                #Resets Game var
                self.game.score = 0

            elif self.game.who_is_dead == "enemy":
                self.game.score += 1
                

            #Reset Game Vars
            self.game.game_loop.decide_bullet_count(self.game)
            self.game.turn = "player"
            self.game.update_score()
            self.game.update_highscore()
            self.game.total_loaded_text.change_text(f"{self.game.gun_chamber.total_loaded} bullets", "black")

            #Reset entity var
            self.dead_entity.texture_after_animation = self.dead_entity.base_texture
            self.dead_entity.animate_textures = None
            self.dead_entity.current_texture = self.dead_entity.base_texture
            self.dead_entity.pos = self.dead_entity.og_pos.copy()

            #Player specific
            self.game.player.inventory.clear()

            self.gamestate_manager.set_state("game loop")

            #Music
            pygame.mixer.music.play(-1)
            self.game.eerie_static.stop()


if __name__ == "__main__":
    game = Game()