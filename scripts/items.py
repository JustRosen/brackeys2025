

def get_item(game):
    pass


def skip(game):
    pass

def reveal(game):
    pass

def gamble(game):
    pass

def rotate(game):
    game.gun_barrel.rotating = True
    game.gun_barrel.rotate_chamber()
    game.enemy.update_chamber()
    game.turn = "enemy"