import random, pygame

def skip(game):
    game.turn = "enemy"

def reveal(game):
    viable_slots = []
    #Goes in reverse since slots after 0 will prolly be safe
    for index in range(0,-5,-1):
        if game.gun_chamber.slot_states[index] == "loaded": #looks for loaded slots
            viable_slots.append(index)
    
    choice = random.choice(viable_slots) #Picks a random loaded slot to reveal

    game.gun_chamber.visible_states[choice] = "loaded"
    game.gun_chamber.add_state_textures()

def gamble(game):
    game.player.animating = True
    game.player.animate_textures = game.player.shoot_self

    if game.gun_chamber.slot_states[0] == "loaded":
        print("u gambled and died")
        #Play death anim
        game.who_is_dead = "player"
        game.death_scene.dead_entity = game.player
        game.game_loop.change_scene_to = "death scene"

    elif game.gun_chamber.slot_states[0] in {"safe", "unknown"}: #If its not loaded
        game.gun_chamber.rotating = True
        game.gun_chamber.current_slot = "safe"
        game.enemy.update_chamber()
        
def rotate(game):

    #Keep in mind when the rotate animation is called, it also updates the chamber state graphics
    game.gun_chamber.rotating = True

    if game.gun_chamber.visible_states[0] == "unknown":
        game.gun_chamber.current_slot_status = "unknown"
    else:
        #Might not be the best code but basically keeps the state the same if its already known
        game.gun_chamber.current_slot_status = game.gun_chamber.visible_states[0] 

    game.enemy.update_chamber()
  