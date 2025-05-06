import pygame
from.. import tools,setup
from.. import constants as C
def create_powerup(centerx,centery,powerup_type):
    if powerup_type==1:
        #return Coin(centerx,centery)
        pass
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

class LifeMushroom(Powerup):
    pass
class Star(Powerup):
    pass
# class Coin(Powerup):
#     def __init__(self,centerx,centery):
#         frame_rects=[(52, 113, 8, 14), (4, 113, 8, 14),
#                         (20, 113, 8, 14), (36, 113, 8, 14)]
#         Powerup.__init__(self,centerx,centery,frame_rects)
#         self.x_vel=2
#         self.state='grow'
#         self.name='coin'
#         self.timer=0
#
#     def update(self,level):
#         if self.state=='grow':
#             self.rect.y+=self.y_vel
#             if self.rect.bottom<self.original_y:
#                 self.state='rest'
#         self.current_time=pygame.time.get_ticks()
#         if self.timer==0:
#             self.timer=self.current_time
#         if self.current_time-self.timer>150:
#             self.frame_index=(self.frame_index+1)%4
#             self.image=self.frames[self.frame_index]
#             self.timer=self.current_time
class Fireball(Powerup):
    def __init__(self,centerx,centery,direction):
        frame_rects=[(96,144,8,8),(104,144,8,8),(96,152,8,8),(104,152,8,8),#旋转
                     (112,144,16,16),(112,160,16,16),(112,176,16,16)]#爆炸
        Powerup.__init__(self,centerx,centery,frame_rects)
        self.name='fireball'
        self.state='fly'
        self.direction=direction
        self.x_vel=10 if self.direction else -10
        self.y_vel=10
        self.gravity=1
        self.timer=0
    def update(self,level):
        self.current_time=pygame.time.get_ticks()
        if self.state=='fly':
            self.y_vel+=self.gravity
            if self.current_time-self.timer>200:
                self.frame_index=(self.frame_index+1)%4
                self.timer=self.current_time
                self.image=self.frames[self.frame_index]
            self.update_position(level)
        elif self.state=='boom':
            if self.current_time-self.timer>50:
                if self.frame_index<6:
                    self.frame_index+=1
                    self.timer=self.current_time
                    self.image=self.frames[self.frame_index]
                else:
                    self.kill()
    def update_position(self, level):
        self.rect.x += self.x_vel
        self.check_x_collisions(level)
        self.rect.y += self.y_vel
        self.check_y_collisions(level)

        if self.rect.x<0 or self.rect.y>C.SCREEN_H:
            self.kill()

    def check_x_collisions(self, level):
        check_group=pygame.sprite.Group(level.ground_item_group,level.box_group,level.brick_group)
        sprite = pygame.sprite.spritecollideany(self, check_group)
        if sprite:
            self.frame_index=4
            self.state='boom'
            setup.SOUND.play_sound('fireball')
        if self.name=='fireball' and self.state=='fly':
            enemy = pygame.sprite.spritecollideany(self, level.enemy_group)
            if enemy:
                enemy.go_die(how='slided')
                level.enemy_group.remove(enemy)
                level.dying_group.add(enemy)
                self.frame_index = 4
                self.state = 'boom'
                setup.SOUND.play_sound('fireball')


    def check_y_collisions(self, level):
        check_group = pygame.sprite.Group(level.ground_item_group, level.brick_group, level.box_group)
        sprite = pygame.sprite.spritecollideany(self, check_group)
        if sprite:
            if self.rect.top < sprite.rect.top:
                self.rect.bottom = sprite.rect.top
                self.y_vel = -10