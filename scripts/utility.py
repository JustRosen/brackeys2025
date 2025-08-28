import pygame

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
