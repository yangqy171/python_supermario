import pygame
from .. import setup
from .. import tools
from .. import constants as C
from ..components import info

class GameComplete:
    def __init__(self):
        self.start({})
        
    def start(self, game_info):
        # 设置默认值，防止缺失导致 KeyError
        default_info = {'score': 0, 'coin': 0, 'lives': 3}
        for k, v in default_info.items():
            if k not in game_info:
                game_info[k] = v
        self.game_info = game_info
        self.finished = False
        self.next = 'main_menu'
        self.timer = 0
        self.info = info.Info('game_complete', self.game_info)
        # 播放通关音乐
        setup.SOUND.play_music('main_theme')
        
    def update(self, surface, keys):
        self.current_time = pygame.time.get_ticks()
        
        # 绘制黑色背景
        surface.fill((0, 0, 0))
        
        # 显示通关信息
        self.info.draw(surface)
        
        # 检测任意键按下，返回主菜单
        if self.timer == 0:
            self.timer = self.current_time
        elif self.current_time - self.timer > 3000:  # 至少显示3秒
            if any(keys):
                self.finished = True
                self.timer = 0