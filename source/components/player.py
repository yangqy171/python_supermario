import pygame

from . import powerup
from .. import constants as C
from.. import setup,tools
import json
import os
class Player(pygame.sprite.Sprite):
    def __init__(self,name):
        pygame.sprite.Sprite.__init__(self)
        self.name=name
        self.load_data()
        self.setup_states()
        self.setup_timers()
        self.load_images()
        self.setup_velocities()


    def load_data(self):
        '''载入数据'''
        file_name=self.name+'.json'
        file_path=os.path.join('source/data/player',file_name)
        with open(file_path) as f:
            self.player_data=json.load(f)
    def setup_states(self):
        '''设置状态'''
        self.face_right=True
        self.state='stand'
        self.dead=False
        self.big=False
        self.can_jump=True
        self.hurt_immune=False
        self.fire=False
        self.can_shoot=True
        self.flag_sliding_complete=False  # 添加旗杆滑动完成标志

    def setup_timers(self):
        '''创建一系列计时器'''
        self.walking_timer=0
        self.transition_timer=0
        self.death_timer=0
        self.hurt_immune_timer=0

    def setup_velocities(self):
        '''设置速率'''
        speed=self.player_data['speed']
        self.x_vel=0
        self.y_vel=0

        self.max_walk_vel=speed['max_walk_speed']
        self.max_run_vel=speed['max_run_speed']
        self.max_y_vel=speed['max_y_velocity']
        self.jump_vel=speed['jump_velocity']
        self.walk_accel=speed['walk_accel']
        self.run_accel=speed['run_accel']
        self.turn_accel=speed['turn_accel']
        self.anti_gravity=C.ANTI_GRAVITY


        self.gravity = C.GRAVITY

        self.max_x_vel=self.max_walk_vel
        self.x_accel=self.walk_accel



    def load_images(self):
        '''载入主角各种帧造型'''
        sheet=setup.GRAPHICS['mario_bros']
        frame_rects = self.player_data['image_frames']

        self.right_small_normal_frames=[]
        self.right_big_normal_frames=[]
        self.right_big_fire_frames=[]
        self.left_small_normal_frames=[]
        self.left_big_normal_frames=[]
        self.left_big_fire_frames=[]

        self.small_normal_frames=[self.right_small_normal_frames,self.left_small_normal_frames]
        self.big_normal_frames=[self.right_big_normal_frames,self.left_big_normal_frames]
        self.big_fire_frames=[self.right_big_fire_frames,self.left_big_fire_frames]

        self.all_frames=[
            self.right_small_normal_frames,
            self.left_small_normal_frames,
            self.right_big_normal_frames,
            self.left_big_normal_frames,
            self.right_big_fire_frames,
            self.left_big_fire_frames
        ]
        self.right_frames=self.right_small_normal_frames
        self.left_frames=self.left_small_normal_frames


        for group,group_frame_rects in frame_rects.items():
            for frame_rect in group_frame_rects:
                right_image=tools.get_image(sheet,frame_rect['x'],
                                            frame_rect['y'],
                                            frame_rect['width'],
                                            frame_rect['height'],(0,0,0),C.PLAYER_MULTI)
                left_image=pygame.transform.flip(right_image,True,False)
                if group=='right_small_normal':
                    self.right_small_normal_frames.append(right_image)
                    self.left_small_normal_frames.append(left_image)
                if group=='right_big_normal':
                    self.right_big_normal_frames.append(right_image)
                    self.left_big_normal_frames.append(left_image)
                if group=='right_big_fire':
                    self.right_big_fire_frames.append(right_image)
                    self.left_big_fire_frames.append(left_image)

        self.frame_index=0
        self.frames = self.right_frames
        self.image=self.frames[self.frame_index]
        self.rect=self.image.get_rect()

    def update(self,keys,level):
        '''更新'''
        self.current_time=pygame.time.get_ticks()
        self.handle_states(keys,level)
        self.is_hurt_immune()

    def handle_states(self,keys,level):
        self.can_jump_or_not(keys)
        self.can_shoot_or_not(keys)
        if self.state=='small2big':
            self.small2big(keys)
        elif self.state=='big2small':
            self.big2small(keys)
        elif self.state=='big2fire':
            self.big2fire(keys)
        elif self.state=='flagpole':
            self.flagpole()
        elif self.state=='walk_auto':
            self.walk_auto()
        elif self.state=='stand':
            self.stand(keys,level)
        elif self.state=='walk':
            self.walk(keys,level)
        elif self.state=='jump':
            self.jump(keys,level)
        elif self.state=='fall':
            self.fall(keys,level)
        elif self.state=='die':
            self.die(keys)
        elif self.state=='small2big':
            self.small2big(keys)
        elif self.state=='big2small':
            self.big2small(keys)
        elif self.state=='big2fire':
            self.big2fire(keys)
        elif self.state=='flagpole':
            self.flagpole()
        elif self.state=='walk_auto':
            self.walk_auto()
            pass
    
        if self.face_right:
            self.image=self.right_frames[self.frame_index]
        else:
            self.image=self.left_frames[self.frame_index]

    def can_shoot_or_not(self,keys):
        if not keys[pygame.K_s]:
            self.can_shoot=True
    def can_jump_or_not(self,keys):
        '''是否可以跳跃'''
        if not keys[pygame.K_UP]:
            self.can_jump=True
    def stand(self,keys,level):
        '''站着'''
        self.y_vel=0
        self.x_vel=0
        self.frame_index=0
        if keys[pygame.K_RIGHT]:
            self.state='walk'
            self.face_right=True
        elif keys[pygame.K_LEFT]:
            self.state='walk'
            self.face_right=False
        elif keys[pygame.K_UP] and self.can_jump:
            self.state='jump'
            self.y_vel=self.jump_vel
        elif keys[pygame.K_s]:
            if self.fire and self.can_shoot:
                self.shoot_fireball(level)

    def walk(self,keys,level):
        '''走'''
        if keys[pygame.K_s]:
            self.max_x_vel=self.max_run_vel
            self.x_accel=self.run_accel
        else:
            self.max_x_vel=self.max_walk_vel
            self.x_accel=self.walk_accel
        if keys[pygame.K_UP] and self.can_jump:
            self.state='jump'
            self.y_vel=self.jump_vel
        if self.current_time-self.walking_timer>self.calc_frame_duration():
            if self.frame_index<3:
                self.frame_index+=1
            else:
                self.frame_index=1
            self.walking_timer=self.current_time
        if keys[pygame.K_RIGHT]:
            self.face_right=True
            if self.x_vel<0:
                self.x_frame_index=5
                self.x_accel=self.turn_accel
            self.x_vel=self.calc_vel(self.x_vel,self.x_accel,self.max_x_vel,True)
        elif keys[pygame.K_LEFT]:
            self.face_right=False
            if self.x_vel>0:
                self.x_frame_index=5
                self.x_accel=self.turn_accel
            self.x_vel=self.calc_vel(self.x_vel,self.x_accel,self.max_x_vel,False)
        elif keys[pygame.K_s]:
            if self.fire and self.can_shoot:
                self.shoot_fireball(level)
        else:
            if self.face_right:
                self.x_vel-=self.x_accel
                if self.x_vel<0:
                    self.x_vel=0
                    self.state='stand'
            else:
                self.x_vel+=self.x_accel
                if self.x_vel>0:
                    self.x_vel=0
                    self.state='stand'




    def jump(self,keys,level):
        '''跳跃'''
        self.frame_index=4
        self.y_vel+=self.anti_gravity
        self.can_jump=False

        if self.y_vel>=0:
            self.state='fall'
        if keys[pygame.K_RIGHT]:
            self.face_right=True
            self.x_vel=self.calc_vel(self.x_vel,self.x_accel,self.max_x_vel,True)
        elif keys[pygame.K_LEFT]:
            self.face_right=False
            self.x_vel=self.calc_vel(self.x_vel,self.x_accel,self.max_x_vel,False)
        elif keys[pygame.K_s]:
            if self.fire and self.can_shoot:
                self.shoot_fireball(level)

        if not keys[pygame.K_UP]:
            self.state='fall'
        
        # 播放跳跃音效
        if self.big:
            setup.SOUND.play_sound('big_jump')
        else:
            pass
            setup.SOUND.play_sound('small_jump')

    def fall(self,keys,level):
         self.y_vel=self.calc_vel(self.y_vel,self.gravity,self.max_y_vel)
        #TODO workaround,will move to level for collision detection
         if keys[pygame.K_RIGHT]:
             self.face_right = True
             self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, True)
         elif keys[pygame.K_LEFT]:
             self.face_right = False
             self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, False)
         elif keys[pygame.K_s]:
            if self.fire and self.can_shoot:
                self.shoot_fireball(level)
    def die(self,keys):
        self.rect.y+=self.y_vel
        self.y_vel+=self.anti_gravity

    def go_die(self):
        self.dead=True
        self.y_vel=self.jump_vel
        self.state='die'
        self.frame_index=6
        self.death_timer=self.current_time
        # 播放死亡音效(只播放一次)
        setup.SOUND.stop_music()
        setup.SOUND.play_sound('death')
        
    def restart(self):
        '''restart after player is dead or go to next level'''
        if self.dead:
            self.dead = False
            self.big = False
            self.fire = False
            self.set_player_image(self.small_normal_frames, 0)
            self.right_frames = self.small_normal_frames[0]
            self.left_frames = self.small_normal_frames[1]
            # 复活时重新播放背景音乐
            setup.SOUND.play_music('main_theme', loop=True)
        self.state = 'stand'

    def small2big(self,keys):
        frame_dur=100
        sizes=[1,0,1,0,1,2,0,1,2,0,2]
        frames_and_idx=[(self.small_normal_frames,0),(self.small_normal_frames,7),(self.big_normal_frames,0)]
        if self.transition_timer==0:
            self.big=True
            self.transition_timer=self.current_time
            self.changing_idx=0
            # 播放变大音效
            setup.SOUND.play_sound('powerup')
        elif self.current_time-self.transition_timer>frame_dur:
                self.transition_timer=self.current_time
                frames,idx=frames_and_idx[sizes[self.changing_idx]]
                self.change_player_image(frames,idx)
                self.changing_idx+=1
                if self.changing_idx==len(sizes):
                    self.transition_timer=0
                    self.state='walk'
                    self.right_frames=self.right_big_normal_frames
                    self.left_frames=self.left_big_normal_frames
    def big2small(self,keys):
        frame_dur=100
        sizes=[2,1,0,1,0,1,0,1,0,1,0]
        frames_and_idx=[(self.small_normal_frames,8),(self.big_normal_frames,8),(self.big_normal_frames,8)]
        if self.transition_timer==0:
            self.big=False
            self.fire=False
            self.transition_timer=self.current_time
            self.changing_idx=0
            setup.SOUND.play_sound('powerup')
        elif self.current_time-self.transition_timer>frame_dur:
                self.transition_timer=self.current_time
                frames,idx=frames_and_idx[sizes[self.changing_idx]]
                self.change_player_image(frames,idx)
                self.changing_idx+=1
                if self.changing_idx==len(sizes):
                    self.transition_timer=0
                    self.state='walk'
                    self.right_frames=self.right_small_normal_frames
                    self.left_frames=self.left_small_normal_frames
    def big2fire(self,keys):
        frame_dur=100
        sizes=[0,1,0,1,0,1,0,1,0,1,0]
        frames_and_idx=[(self.big_fire_frames,3),(self.big_normal_frames,3)]
        if self.transition_timer==0:
            self.fire=True
            self.transition_timer=self.current_time
            self.changing_idx=0
            setup.SOUND.play_sound('powerup')
        elif self.current_time-self.transition_timer>frame_dur:
                self.transition_timer=self.current_time
                frames,idx=frames_and_idx[sizes[self.changing_idx]]
                self.change_player_image(frames,idx)
                self.changing_idx+=1
                if self.changing_idx==len(sizes):
                    self.transition_timer=0
                    self.state='walk'
                    self.right_frames=self.right_big_fire_frames
                    self.left_frames=self.left_big_fire_frames
    def change_player_image(self,frames,idx):
        self.frame_index=idx
        if self.face_right:
            self.right_frames=frames[0]
            self.image=self.right_frames[self.frame_index]
        else:
            self.left_frames=frames[1]
            self.image=self.left_frames[self.frame_index]
        last_frame_bottom=self.rect.bottom
        last_frame_centerx=self.rect.centerx
        self.rect=self.image.get_rect()
        self.rect.bottom=last_frame_bottom
        self.rect.centerx=last_frame_centerx


    def calc_vel(self,vel,accel,max_vel,is_positive=True):
        if is_positive:
            return min(vel+accel,max_vel)
        else:
            return max(vel-accel,-max_vel)
    def calc_frame_duration(self):
        '''计算帧持续时间'''
        duration=-60/self.max_run_vel*abs(self.x_vel)+80
        return duration
    def is_hurt_immune(self):
        '''是否免疫伤害'''
        if self.hurt_immune:
            if self.hurt_immune_timer==0:
                self.hurt_immune_timer=self.current_time
                self.blank_image=pygame.Surface((1,1))
            elif self.current_time-self.hurt_immune_timer<2000:
                if(self.current_time-self.hurt_immune_timer)%100<50:
                    self.image=self.blank_image
            else:
                self.hurt_immune=False
                self.hurt_immune_timer=0
    def shoot_fireball(self,level):
        self.frame_index=6
        fireball=powerup.Fireball(self.rect.centerx,self.rect.centery,self.face_right)
        level.power_up_group.add(fireball)
        self.can_shoot=False

    def flagpole(self):
        """旗杆状态处理"""
        self.frame_index = 10  # 使用合适的帧索引，表示抓住旗杆的姿势
        self.x_vel = 0
        
        # 让玩家沿着旗杆下滑
        if self.rect.bottom < 493:  # 到达地面前继续下滑
            self.y_vel = 5
        else:
            self.y_vel = 0
            self.rect.bottom = 493  # 确保玩家站在地面上
            # 完成旗杆下滑后，切换到自动行走状态
            if not self.flag_sliding_complete:
                self.flag_sliding_complete = True
                self.state = 'walk_auto'
                self.x_vel = 3  # 向右自动行走
        
        # 确保玩家面向右侧
        self.face_right = True

    def walk_auto(self):
        """自动行走状态处理"""
        # 自动行走动画
        if self.current_time - self.walking_timer > self.calc_frame_duration():
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 1
            self.walking_timer = self.current_time
