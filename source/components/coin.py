import pygame
from .. import tools,setup
from .. import constants as C

class FlashingCoin(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.frames=[]
        self.frame_index=0
        frame_rects=[(1,160,5,8),(9,160,5,8),(17,160,5,8),(9,160,5,8)]
        self.load_frames(frame_rects)
        self.image=self.frames[self.frame_index]
        self.rect=self.image.get_rect()
        self.rect.x=280
        self.rect.y=58
        self.timer=0

    def load_frames(self,frame_rects):
        sheet=setup.GRAPHICS['item_objects']
        for frame_rect in frame_rects:
            self.frames.append(tools.get_image(sheet,*frame_rect,(0,0,0),C.BG_MULTI))
    def update(self):
        self.current_time=pygame.time.get_ticks()
        frame_durations=[375,125,125,125]

        if self.timer==0:
            self.timer=self.current_time
        elif self.current_time-self.timer>frame_durations[self.frame_index]:
            self.frame_index+=1
            self.frame_index%=4
            self.timer=self.current_time

        self.image=self.frames[self.frame_index]


class StaticCoin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.frame_index = 0
        self.frames = []
        self.load_frames()
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.animation_timer = 0
        self.name = 'coin'

    def load_frames(self):
        sheet = setup.GRAPHICS['item_objects']
        frame_rect_list = [(3, 98, 9, 13), (19, 98, 9, 13),
                        (35, 98, 9, 13), (51, 98, 9, 13)]
        for frame_rect in frame_rect_list:
            self.frames.append(tools.get_image(sheet, *frame_rect, 
                            (0, 0, 0), C.BG_MULTI))

    def update(self):
        self.current_time = pygame.time.get_ticks()
        if self.animation_timer == 0:
            self.animation_timer = self.current_time
        elif (self.current_time - self.animation_timer) > 180:
            self.frame_index = (self.frame_index + 1) % 4
            self.animation_timer = self.current_time
        
        self.image = self.frames[self.frame_index]


class Coin(pygame.sprite.Sprite):
    """从砖块或宝箱中弹出的金币"""
    def __init__(self, centerx, centery):
        pygame.sprite.Sprite.__init__(self)
        self.frames = []
        self.frame_index = 0
        frame_rects = [(52, 113, 8, 14), (4, 113, 8, 14), 
                        (20, 113, 8, 14), (36, 113, 8, 14)]
        self.load_frames(frame_rects)
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.centerx = centerx
        self.rect.centery = centery
        self.y_vel = -10  # 向上弹出的初始速度
        self.gravity = 0.7  # 重力加速度
        self.initial_height = centery - 500  # 弹出的最大高度
        self.name = 'coin'
        self.timer = 0
        self.state = 'rise'  # 金币状态：rise(上升), fall(下降)

    def load_frames(self, frame_rects):
        sheet = setup.GRAPHICS['item_objects']
        for frame_rect in frame_rects:
            self.frames.append(tools.get_image(sheet, *frame_rect, (0, 0, 0), C.BG_MULTI))

    def update(self, level_info=None):
        self.current_time = pygame.time.get_ticks()
        
        # 更新金币动画
        if self.timer == 0:
            self.timer = self.current_time
        elif self.current_time - self.timer > 50:
            self.frame_index = (self.frame_index + 1) % 4
            self.timer = self.current_time
        
        # 更新金币位置
        if self.state == 'rise':
            self.rect.y += self.y_vel
            self.y_vel += self.gravity
            if self.y_vel >= 0:
                self.state = 'fall'
        elif self.state == 'fall':
            self.rect.y += self.y_vel
            self.y_vel += self.gravity
            if self.rect.centery > self.initial_height + 100:
                setup.SOUND.play_sound('coin')
                self.kill()  # 当金币落到一定高度后消失
                
        self.image = self.frames[self.frame_index]