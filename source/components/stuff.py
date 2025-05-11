import pygame
from .. import setup, tools

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width,height)).convert()
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.name=name

class Checkpoint(Item):
    def __init__(self, x, y, w, h, checkpoint_type,enemy_groupid=None,name='checkpoint'):
        Item.__init__(self,x,y,w,h,name)
        self.checkpoint_type=checkpoint_type
        self.enemy_groupid=enemy_groupid

# 添加旗杆相关类
class Flagpole(Item):
    def __init__(self, x, y, width, height, name='flagpole'):
        Item.__init__(self, x, y, width, height, name)
        self.image.fill((100, 100, 100))  # 灰色旗杆
        print(f"[DEBUG] Flagpole创建: name={self.name}, rect=({self.rect.x},{self.rect.y},{self.rect.width},{self.rect.height})")

class Flag(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = tools.get_image(setup.GRAPHICS['item_objects'], 128, 32, 16, 16, (0, 0, 0), 2.5)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.state = 'top'  # 旗子状态：top(顶部), slide(滑下), bottom(底部)
        self.y_vel = 5  # 下滑速度
        print(f"[DEBUG] Flag创建: rect=({self.rect.x},{self.rect.y},{self.rect.width},{self.rect.height})")

    def update(self):
        if self.state == 'slide':
            self.rect.y += self.y_vel
            if self.rect.bottom >= 485:  # 到达底部位置
                self.state = 'bottom'