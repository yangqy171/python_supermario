#工具与游戏主控
import pygame
import random
import os
class Game:
    def __init__(self,state_dict,start_state):
        self.screen=pygame.display.get_surface()
        self.clock=pygame.time.Clock()
        self.keys=pygame.key.get_pressed()
        self.state_dict=state_dict
        self.state=self.state_dict[start_state]

    def update(self):
        if self.state.finished:
            game_info=self.state.game_info
            next_state=self.state.next
            self.state.finished=False
            self.state=self.state_dict[next_state]
            self.state.start(game_info)
        self.state.update(self.screen,self.keys)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.display.quit()
                    quit()
                elif event.type==pygame.KEYDOWN:
                    self.keys=pygame.key.get_pressed()
                elif event.type==pygame.KEYUP:
                    self.keys=pygame.key.get_pressed()
            self.update()
            pygame.display.update()
            self.clock.tick(60)

def load_graphics(path,accept=('.jpg','.png','.bmp','gif')):
    '''加载图片，存在字典里'''
    graphics={}
    for pic in os.listdir(path):
        name,ext=os.path.splitext(pic)
        if ext.lower() in accept:
            img=pygame.image.load(os.path.join(path,pic))
            if img.get_alpha():
                img=img.convert_alpha()#对于透明层转化格式
            else:
                img=img.convert()
            graphics[name]=img
    return graphics

def get_image(sheet,x,y,width,height,colorkey,scale):
    '''sheet:图片，colorkey:抠图背景色，scale:放大倍数'''
    image=pygame.Surface((width,height))#创建一个和方框一样大的空图层
    image.blit(sheet,(0,0),(x,y,width,height))#图层上画图，(0，0)表示画图位置，而(x,y,width,height)表示取出对应图区域
    image.set_colorkey(colorkey)
    image=pygame.transform.scale(image,(int(width*scale),int(height*scale)))
    return image
