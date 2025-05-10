import pygame
import os
from . import constants as C
from . import tools
from . import sound
pygame.init()
SCREEN=pygame.display.set_mode((C.SCREEN_W,C.SCREEN_H))
# 使用相对于当前脚本的路径加载图形资源
current_dir = os.path.dirname(os.path.abspath(__file__))
resources_path = os.path.join(os.path.dirname(current_dir), 'resources', 'graphics')
GRAPHICS = tools.load_graphics(resources_path)
SOUND = sound.Sound()