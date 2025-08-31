import pygame, os, json

BASE_IMAGE_PATH = "assets/"

#Duration is in ms
class Timer:
    def __init__(self, duration):
        self.duration = duration
        self.start_time = 0
        self.active = True

    def activate(self):
        self.active = True
        self.start_time = pygame.time.get_ticks()

    def deactivate(self):
        self.active = False
        self.start_time = 0

    def update(self):
        if self.active:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - self.start_time
            if elapsed_time >= self.duration:
                self.deactivate()
                return True
            else:
                return False
        else:
            return False

def load_image(path):
    img = pygame.image.load(BASE_IMAGE_PATH + path).convert_alpha()
    #img.set_colorkey(("Black"))
    
    return img

def load_images(path):
    images = []
    files = os.listdir(BASE_IMAGE_PATH + path)

    #Opens folder and goes thru files
    for image_name in files:
        images.append(load_image(path + '/' + image_name))
    
    return images

def save_score(path, score):
    with open(path, 'w') as file:
        json.dump(score, file) 

def load_score(path):
    with open(path, 'r') as file:
        return json.load(file)
        
def load_images_as_dic(path, remove_suffix = False, suffix = None):
    images = {}
    files = os.listdir(BASE_IMAGE_PATH + path)

    #Opens folder and goes thru files
    for image_name in files:
        key = image_name

        if remove_suffix:
            key = image_name.removesuffix(suffix)
        
        images[key] = load_image(path + '/' + image_name)
        
    return images

