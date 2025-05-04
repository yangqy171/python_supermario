import pygame

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