import pygame
from.. import tools,setup
from.. import constants as C
from. import coin
def create_powerup(centerx,centery,powerup_type):
    if powerup_type==1:
        return Coin()
    elif powerup_type==4:
        return Fireflower(centerx,centery)
    elif powerup_type==3:
        return Mushroom(centerx,centery)

class Powerup(pygame.sprite.Sprite):
    def __init__(self,centerx,centery,frame_rects):
        pygame.sprite.Sprite.__init__(self)
        self.frames=[]
        self.frame_index=0
        for frame_rect in frame_rects:
            self.frames.append(tools.get_image(setup.GRAPHICS['item_objects'],*frame_rect,(0,0,0),2.5))
        self.image=self.frames[self.frame_index]
        self.rect=self.image.get_rect()
        self.rect.centerx=centerx
        self.rect.centery=centery

        self.x_vel=0
        self.direction=1
        self.y_vel=-1
        self.gravity=1
        self.max_y_vel=8
        self.original_y=centery-self.rect.height/2

    def update_position(self, level):
        self.rect.x += self.x_vel
        self.check_x_collisions(level)
        self.rect.y += self.y_vel
        self.check_y_collisions(level)

        if self.rect.x<0 or self.rect.y>C.SCREEN_H:
            self.kill()

    def check_x_collisions(self, level):
        sprite = pygame.sprite.spritecollideany(self, level.ground_item_group)
        if sprite:
            if self.direction:
                self.direction = 0
                self.rect.right = sprite.rect.left
            else:
                self.direction = 1
                self.rect.left = sprite.rect.right
            self.x_vel *= -1


    def check_y_collisions(self, level):
        check_group = pygame.sprite.Group(level.ground_item_group, level.brick_group, level.box_group)
        sprite = pygame.sprite.spritecollideany(self, check_group)
        if sprite:
            if self.rect.top < sprite.rect.top:
                self.rect.bottom = sprite.rect.top
                self.y_vel = 0
                self.state = 'walk'
        level.check_will_fall(self)
class Mushroom(Powerup):
    def __init__(self,centerx,centery):
        Powerup.__init__(self,centerx,centery,[(0,0,16,16)])
        self.x_vel=2
        self.state='grow'
        self.name='mushroom'

    def update(self,level):
        if self.state=='grow':
            self.rect.y+=self.y_vel
            if self.rect.bottom<self.original_y:
                self.state='walk'
        elif self.state=='walk':
            pass
        elif self.state=='fall':
            if self.y_vel<self.max_y_vel:
                self.y_vel+=self.gravity
        if self.state!='grow':
            self.update_position(level)

class Fireflower(Powerup):
    def __init__(self,centerx,centery):
        frame_rects=[(0,32,16,16),(16,32,16,16),(32,32,16,16),(48,32,16,16)]
        Powerup.__init__(self,centerx,centery,frame_rects)
        self.x_vel=2
        self.state='grow'
        self.name='fireflower'
        self.timer=0

    def update(self,level):
        if self.state=='grow':
            self.rect.y+=self.y_vel
            if self.rect.bottom<self.original_y:
                self.state='rest'
        self.current_time=pygame.time.get_ticks()
        if self.timer==0:
            self.timer=self.current_time
        if self.current_time-self.timer>30:
            self.frame_index=(self.frame_index+1)%4
            self.image=self.frames[self.frame_index]
            self.timer=self.current_time
class Coin(coin.FlashingCoin):
    def __init__(self):
        super().__init__()

class LifeMushroom(Powerup):
    pass
class Star(Powerup):
    pass