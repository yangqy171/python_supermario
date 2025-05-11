import pygame
from .. import constants as C
from . import coin
pygame.font.init()
from ..import setup,tools

class Info:
    def __init__(self,state,game_info):
        self.state=state
        self.game_info=game_info
        self.create_state_labels()
        self.create_info_labels()
        self.flash_coin=coin.FlashingCoin()

    def create_state_labels(self):
        self.state_labels=[]
        if self.state=='main_menu':
            self.state_labels.append((self.create_label('1 PLATER  GAME'),(272,360)))
            self.state_labels.append((self.create_label('2 PLATER  GAME'),(272,405)))
            self.state_labels.append((self.create_label('TOP - '),(290,465)))
            self.state_labels.append((self.create_label('000000'),(400,465)))
        elif self.state=='load_screen':
            self.state_labels.append((self.create_label('WORLD'),(280,200)))
            level_num = self.game_info.get('level_num', 1)
            self.state_labels.append((self.create_label(f'1 - {level_num}'),(430,200)))
            self.state_labels.append((self.create_label('X   {}'.format(self.game_info['lives'])),(380,280)))
            self.player_image = tools.get_image(setup.GRAPHICS['mario_bros'], 178, 32, 12, 16, (0, 0, 0), C.BG_MULTI)
        elif self.state=='game_over':
            self.state_labels.append((self.create_label('GAME OVER'),(280,300)))
        elif self.state=='game_complete':
            self.state_labels.append((self.create_label('YOU WIN!'),(280,250)))
            self.state_labels.append((self.create_label('CONGRATULATIONS!'),(200,300)))
            score_count = self.game_info.get('score', 0)
            self.state_labels.append((self.create_label('YOUR SCORE: {:06d}'.format(score_count)),(200,350)))
            self.state_labels.append((self.create_label('PRESS ANY TO MENU'),(200,450)))
    def create_info_labels(self):
        self.info_labels=[]
        self.info_labels.append((self.create_label('MARIO'), (75, 30)))
        self.info_labels.append((self.create_label('WORLD'), (450, 30)))
        self.info_labels.append((self.create_label('TIME'), (625, 30)))
        score_count=self.game_info['score']
        self.info_labels.append((self.create_label('{:06d}'.format(score_count)), (75, 55)))
        # 初始化金币计数
        coin_count = self.game_info['coin']
        self.info_labels.append((self.create_label('x{:02d}'.format(coin_count)), (300, 55)))
        # 显示当前关卡编号
        level_num = self.game_info.get('level_num', 1)
        self.info_labels.append((self.create_label(f'1 - {level_num}'), (480, 55)))

    def create_label(self,label,size=40,width_scale=1.25,height_scale=1):
        '''传入文字和大小并渲染成文字'''
        font=pygame.font.SysFont(C.FONT,size)
        label_image=font.render(label,1,(255,255,255))
        rect=label_image.get_rect()
        label_image=pygame.transform.scale(label_image,(int(rect.width*width_scale),int(rect.height*height_scale)))
        return label_image
    def update(self):
        '''实时更新分数和金币'''
        self.flash_coin.update()
        
        # 更新金币计数标签
        coin_count = self.game_info.get('coin', 0)
        # 更新分数标签
        score_count = self.game_info.get('score', 0)
        
        for i, (label, pos) in enumerate(self.info_labels):
            if pos == (300, 55):  # 金币标签的位置
                self.info_labels[i] = (self.create_label('x{:02d}'.format(coin_count)), pos)
            elif pos == (75, 55):  # 分数标签的位置
                self.info_labels[i] = (self.create_label('{:06d}'.format(score_count)), pos)

    def draw(self,surface):
        '''传入图层，在图层上放文字'''
        for label in self.state_labels:
            surface.blit(label[0],label[1])
        for label in self.info_labels:
            surface.blit(label[0],label[1])
        surface.blit(self.flash_coin.image,self.flash_coin.rect)

        if self.state=='load_screen':
            surface.blit(self.player_image,(300,270))
