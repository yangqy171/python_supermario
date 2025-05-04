import pygame
from . import constants as C
from . import tools
from . import sound
pygame.init()
SCREEN=pygame.display.set_mode((C.SCREEN_W,C.SCREEN_H))
GRAPHICS = tools.load_graphics('resources/graphics')
SOUND = sound.Sound()