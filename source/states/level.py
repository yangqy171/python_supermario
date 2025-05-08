from ..components import info
import pygame
from .. import setup,tools
from.. import constants as C
from ..components import player,stuff,brick,box,enemy
import json,os

class Level:
    def start(self,game_info):
        self.game_info=game_info
        self.finished = False
        self.next = 'game_over'
        self.load_map_data()
        self.info = info.Info('level',self.game_info)
        self.setup_background()
        self.setup_start_position()
        self.setup_player()
        self.setup_ground_items()
        self.setup_static_coins()
        self.setup_bricks_and_boxes()
        self.setup_enemies()
        self.setup_checkpoint()
        self.setup_flagpole()  # 添加旗杆设置

    def load_map_data(self):
        file_name='level_1.json'
        file_path=os.path.join('source/data/maps',file_name)
        with open(file_path,'r') as f:
            self.map_data=json.load(f)

    def setup_background(self):
        '''game_window窗口矩形
           game_ground与地图等长的画布'''
        self.image_name=self.map_data['image_name']
        self.background=setup.GRAPHICS[self.image_name]
        rect=self.background.get_rect()
        self.background=pygame.transform.scale(self.background,(int(rect.width*C.BG_MULTI),int(rect.height*C.BG_MULTI)))
        self.background_rect=self.background.get_rect()
        self.game_window=setup.SCREEN.get_rect()
        self.game_ground=pygame.Surface((self.background_rect.width,self.background_rect.height))

    def setup_start_position(self):
        self.position=[]
        for data in self.map_data['maps']:
            self.position.append((data['start_x'],data['end_x'],data['player_x'],data['player_y']))
        self.start_x,self.end_x,self.player_x,self.player_y=self.position[0]
    def setup_player(self):
        self.player=player.Player('mario')
        self.player.rect.x=self.game_window.x+self.player_x#相对窗口位置
        self.player.rect.bottom=self.player_y

    def setup_ground_items(self):
        self.ground_item_group=pygame.sprite.Group()
        for name in ['ground','pipe','step']:
            for item in self.map_data[name]:
                self.ground_item_group.add(stuff.Item(item['x'],item['y'],item['width'],item['height'],name))
                
    def setup_static_coins(self):
        """设置地图中的静态金币"""
        from ..components.coin import StaticCoin
        self.static_coin_group = pygame.sprite.Group()
        if 'coin' in self.map_data:
            for coin_data in self.map_data['coin']:
                x, y = coin_data['x'], coin_data['y']
                self.static_coin_group.add(StaticCoin(x, y))

    def setup_bricks_and_boxes(self):
        self.brick_group=pygame.sprite.Group()
        self.box_group=pygame.sprite.Group()
        self.coin_group=pygame.sprite.Group()
        self.power_up_group=pygame.sprite.Group()
        if 'brick' in self.map_data:
            for brick_data in self.map_data['brick']:
                x,y=brick_data['x'],brick_data['y']
                brick_type=brick_data['type']
                if brick_type==0:
                    if 'brick_num' in brick_data:
                        #TODO batch bricks
                        pass
                    else:
                        self.brick_group.add(brick.Brick(x,y,brick_type,None))
                elif brick_type==1:
                    self.brick_group.add(brick.Brick(x,y,brick_type,self.coin_group))
                else:
                    self.brick_group.add(brick.Brick(x,y,brick_type,self.power_up_group))
        if 'box' in self.map_data:
            for box_data in self.map_data['box']:
                x,y=box_data['x'],box_data['y']
                box_type=box_data['type']
                if box_type==1:
                    self.box_group.add(box.Box(x,y,box_type,self.coin_group))
                else:
                    self.box_group.add(box.Box(x,y,box_type,self.power_up_group))
    def setup_flagpole(self):
        """设置旗杆和旗子，从JSON数据中读取"""
        self.flagpole_group = pygame.sprite.Group()
        
        # 从地图数据中读取旗杆信息
        if 'flagpole' in self.map_data:
            for data in self.map_data['flagpole']:
                # 根据type类型创建不同的旗杆部件
                if data['type'] == 0:  # 旗杆顶部
                    sprite = stuff.Flagpole(data['x'], data['y'], 10, 10, 'flagpole_top')
                    sprite.image.fill((100, 100, 100))  # 灰色旗杆顶部
                elif data['type'] == 1:  # 旗杆杆身
                    sprite = stuff.Flagpole(data['x'], data['y'], 10, 40, 'flagpole_pole')
                    sprite.image.fill((100, 100, 100))  # 灰色旗杆
                elif data['type'] == 2:  # 旗子
                    sprite = stuff.Flag(data['x'], data['y'])
                    self.flag = sprite  # 保存旗子引用，用于动画
                
                self.flagpole_group.add(sprite)
        
    def setup_enemies(self):
        self.dying_group=pygame.sprite.Group()
        self.shell_group=pygame.sprite.Group()
        self.enemy_group=pygame.sprite.Group()
        self.enemy_group_dict={}
        for enemy_group_data in self.map_data['enemy']:
            group=pygame.sprite.Group()
            for enemy_group_id,enemy_list in enemy_group_data.items():
                for enemy_data in enemy_list:
                    group.add(enemy.create_enemy(enemy_data))
                self.enemy_group_dict[enemy_group_id]=group
    def setup_checkpoint(self):
        self.checkpoint_group=pygame.sprite.Group()
        for item in self.map_data['checkpoint']:
            x,y,w,h=item['x'],item['y'],item['width'],item['height']
            checkpoint_type=item['type']
            enemy_groupid=item.get('enemy_groupid')
            self.checkpoint_group.add(stuff.Checkpoint(x,y,w,h,checkpoint_type,enemy_groupid))

    def update(self, surface,keys):
        self.current_time=pygame.time.get_ticks()
        self.player.update(keys,self)
        if self.player.dead:
            if self.current_time-self.player.death_timer>3000:
                self.finished=True
                self.update_game_info()
                setup.SOUND.play_music('main_theme')
        elif self.is_frozen():
            pass
        else:
            self.update_player_position()
            self.check_checkpoints()
            self.check_if_go_die()
            self.update_game_window()
            self.info.update()
            self.power_up_group.update(self)
            self.brick_group.update()
            self.box_group.update()
            self.enemy_group.update(self)
            self.dying_group.update(self)
            self.shell_group.update(self)
            self.coin_group.update()
            self.static_coin_group.update()
            self.flagpole_group.update()
            # 检查所有金币碰撞
            self.check_coin_collisions()
            # 检查旗杆碰撞
            self.check_flagpole_collisions()

        self.draw(surface)
    def is_frozen(self):
        # 检查玩家是否处于变身状态，此时游戏应该暂停其他更新
        frozen = self.player.state in ['small2big','big2small','big2fire','fire2small']
        return frozen


    def update_player_position(self):
        #x direction
        self.player.rect.x+=self.player.x_vel
        if self.player.rect.x<self.start_x:
            self.player.rect.x=self.start_x
        elif self.player.rect.right>self.end_x:
            self.player.rect.right=self.end_x
        self.check_x_collisions()
        #y direction
        if not self.player.dead:
            self.player.rect.y+=self.player.y_vel
            self.check_y_collisions()

    def check_x_collisions(self):
        check_group=pygame.sprite.Group(self.ground_item_group,self.brick_group,self.box_group)
        ground_item = pygame.sprite.spritecollideany(self.player, check_group)  # 返回与玛丽奥第一个碰撞的精灵
        if ground_item:
            self.adjust_player_x(ground_item)
        if self.player.hurt_immune:
            return
        enemy = pygame.sprite.spritecollideany(self.player, self.enemy_group)
        if enemy:
            if self.player.big:
                self.player.state='big2small'
                self.player.hurt_immune=True

            else:
                self.player.go_die()
        shell= pygame.sprite.spritecollideany(self.player, self.shell_group)
        if shell:
            if shell.state=='slide' and self.player.big:
                self.player.state='big2small'
                self.player.hurt_immune=True
            elif shell.state=='slide' and not self.player.big:
                self.player.go_die()
            else:
                if self.player.rect.x<shell.rect.x:
                    shell.x_vel=10
                    shell.rect.x+=40
                    shell.direction=1
                else:
                    shell.x_vel=-10
                    shell.rect.x-=40
                    shell.direction=0
                shell.state='slide'
                # 踢龟壳加40分
                self.game_info['score'] = self.game_info.get('score', 0) + 40
        powerup=pygame.sprite.spritecollideany(self.player,self.power_up_group)
        if powerup:
            if powerup.name=='fireball':
                pass
            elif powerup.name=='mushroom':
                self.player.state='small2big'
                powerup.kill()
            elif powerup.name=='fireflower':
                if not self.player.big:
                    self.player.state = 'small2big'
                    print('碰到fireflower: 设置状态为small2big')
                elif self.player.big and not self.player.fire:
                    # 确保在设置状态前重置transition_timer
                    self.player.transition_timer = 0
                    self.player.state = 'big2fire'
                    print('碰到fireflower: 设置状态为big2fire')
                powerup.kill()
                print(f'fireflower已移除，玩家状态: {self.player.state}, big={self.player.big}, fire={self.player.fire}')
    def check_y_collisions(self):
        ground_item=pygame.sprite.spritecollideany(self.player,self.ground_item_group)
        brick=pygame.sprite.spritecollideany(self.player,self.brick_group)
        box=pygame.sprite.spritecollideany(self.player,self.box_group)
        enemy=pygame.sprite.spritecollideany(self.player,self.enemy_group)
        if brick and box:
            to_brick=abs(self.player.rect.bottom-brick.rect.centerx)
            to_box=abs(self.player.rect.bottom-box.rect.centerx)
            if to_brick>to_box:
                brick=None
            else:
                box=None
        if ground_item:
            self.adjust_player_y(ground_item)
        elif brick:
            self.adjust_player_y(brick)
            # 播放砖块碰撞音效
            if self.player.y_vel < 0:
                setup.SOUND.play_sound('bump')
        elif box:
            self.adjust_player_y(box)
            # 播放宝箱碰撞音效
            if self.player.y_vel < 0:
                setup.SOUND.play_sound('bump')
        elif enemy:
            if self.player.hurt_immune:
                return
            self.enemy_group.remove(enemy)
            if enemy.name=='koopa':
                self.shell_group.add(enemy)
            else:
                self.dying_group.add(enemy)

            self.dying_group.add(enemy)
            if self.player.y_vel<0:
                how='bumped'
                # 顶死敌人加200分
                self.game_info['score'] = self.game_info.get('score', 0) + 200
            else:
                how='trampled'
                self.player.state='jump'
                self.player.rect.bottom=enemy.rect.top
                self.player.y_vel=self.player.jump_vel*0.8
                # 踩死敌人加100分
                self.game_info['score'] = self.game_info.get('score', 0) + 100
                # 播放踩踏敌人音效
                setup.SOUND.play_sound('stomp')
            enemy.go_die(how)
        self.check_will_fall(self.player)
        # 移除此处的powerup碰撞检测，统一在check_x_collisions中处理
        # 这样可以避免重复触发状态变化
        pass
    def adjust_player_x(self,sprite):
        if self.player.rect.x<sprite.rect.x:
            self.player.rect.right=sprite.rect.left
        else:
            self.player.rect.left=sprite.rect.right
        self.player.x_vel=0

    def adjust_player_y(self,sprite):
        if self.player.rect.bottom<sprite.rect.bottom:
            self.player.rect.bottom=sprite.rect.top
            self.player.y_vel = 0
            self.player.state='walk'
        else:
            self.player.rect.top=sprite.rect.bottom
            self.player.y_vel=7
            self.player.state='fall'
            self.is_enemy_on(sprite)

            if sprite.name=='box':
                if sprite.state=='rest':
                    sprite.go_bumped()
                    self.game_info['coin'] = self.game_info.get('coin', 0) + sprite.coin_num
                    if sprite.coin_num>0:
                        self.game_info['score'] = self.game_info.get('score', 0) + 100
                    print(sprite.coin_num)
            if sprite.name=='brick':
                if self.player.big and sprite.brick_type==0:
                    sprite.smashed(self.dying_group)
                else:
                    sprite.go_bumped()
                    self.game_info['coin'] = self.game_info.get('coin', 0) + sprite.coin_num
                    if sprite.coin_num>0:
                        self.game_info['score'] = self.game_info.get('score', 0) + 100
    def is_enemy_on(self,sprite):
        sprite.rect.y-=1
        enemy=pygame.sprite.spritecollideany(sprite,self.enemy_group)
        if enemy:
            self.enemy_group.remove(enemy)
            self.dying_group.add(enemy)
            if sprite.rect.centerx>enemy.rect.centerx:
                enemy.go_die('bumped',-1)
            else:
                enemy.go_die('bumped')
            # 顶砖块间接杀死敌人加200分
            self.game_info['score'] = self.game_info.get('score', 0) + 100
        sprite.rect.y+=1

    def check_will_fall(self,sprite):
        sprite.rect.y+=1
        check_group=pygame.sprite.Group(self.ground_item_group,self.brick_group,self.box_group)
        ground_item=pygame.sprite.spritecollideany(sprite,check_group)
        if not ground_item and sprite.state!='jump' and not self.is_frozen():
            sprite.state='fall'
        sprite.rect.y-=1


    def update_game_window(self):
        third=self.game_window.x+self.game_window.width/3
        if self.player.x_vel>0 and self.player.rect.centerx>third and self.game_window.right<self.end_x:
            self.game_window.x+=self.player.x_vel
            self.start_x=self.game_window.x

    def draw(self, surface):
        self.game_ground.blit(self.background,self.game_window,self.game_window)
        self.game_ground.blit(self.player.image,self.player.rect)
        self.power_up_group.draw(self.game_ground)
        self.coin_group.draw(self.game_ground)
        self.static_coin_group.draw(self.game_ground)
        self.brick_group.draw(self.game_ground)
        self.box_group.draw(self.game_ground)
        self.enemy_group.draw(self.game_ground)
        self.dying_group.draw(self.game_ground)
        self.shell_group.draw(self.game_ground)
        self.flagpole_group.draw(self.game_ground)
        

        surface.blit(self.game_ground, (0,0),self.game_window)
        self.info.draw(surface)
    def check_checkpoints(self):
        checkpoints = pygame.sprite.spritecollide(self.player, self.checkpoint_group, False)
        if checkpoints:
            for checkpoint in checkpoints:
                if checkpoint.checkpoint_type == 0:
                    self.enemy_group.add(self.enemy_group_dict[str(checkpoint.enemy_groupid)])
                checkpoint.kill()
    def check_if_go_die(self):
        if self.player.rect.y>C.SCREEN_H:
            self.player.go_die()
            
    def check_flagpole_collisions(self):
        """检查玩家与旗杆的碰撞"""
        # 只有当玩家不处于死亡或变身状态时才检查
        if self.player.dead or self.is_frozen():
            return
        # 检查与旗杆组的碰撞
        flagpole_hit = pygame.sprite.spritecollideany(self.player, self.flagpole_group)
        if flagpole_hit:
            # 如果玩家碰到了旗杆，设置玩家状态为旗杆状态
            #if self.player.state=='walk_auto':
                #return
            # 新增：如果已经完成滑旗，不再切换状态
            if getattr(self.player, 'flag_sliding_complete', False):
                return
            elif self.player.state != 'flagpole':
                self.player.state = 'flagpole'
                # 停止玩家移动
                self.player.x_vel = 0
                # 调整玩家位置到旗杆上
                self.player.rect.x = flagpole_hit.rect.x - 10
                
                # 根据玩家在旗杆上的高度计算得分
                # 旗杆顶部位置约为y=97，底部约为y=485
                flagpole_height = 485 - 97
                player_height = self.player.rect.y - 97
                # 计算得分：越高得分越多，最高100分，最低10分，在碰撞过程累积加分
                if player_height <= 0:  # 玩家在旗杆顶部或更高
                    score = 100
                else:
                    # 根据高度比例计算分数
                    height_ratio = player_height / flagpole_height
                    score = max(10, int(100 - height_ratio * 90))
                
                # 更新游戏分数
                self.game_info['score'] = self.game_info.get('score', 0) + score
                
                # 如果有旗子，开始旗子下滑动画
                if self.flag.state == 'top':
                    self.flag.state = 'slide'
                    # 尝试播放旗杆音效，如果不存在则播放其他音效
                    setup.SOUND.stop_music()
                    setup.SOUND.play_sound('one_up')


            
    def check_coin_collisions(self):
        """检查玩家与所有金币的碰撞"""
        # 检测与动态金币的碰撞
        coin_hits = pygame.sprite.spritecollide(self.player, self.coin_group, True)
        for coin in coin_hits:
            if coin.name == 'coin':
                self.game_info['coin'] = self.game_info.get('coin', 0) + 1
                print(f'金币增加: 1, 当前总数: {self.game_info["coin"]}')
                print(f'Debug: game_info["coin"] = {self.game_info["coin"]}')
                # 播放金币音效
                setup.SOUND.play_sound('coin')
                
        # 检测与静态金币的碰撞
        static_coin_hits = pygame.sprite.spritecollide(self.player, self.static_coin_group, True)
        for coin in static_coin_hits:
            if coin.name == 'coin':
                self.game_info['coin'] = self.game_info.get('coin', 0) + 1
                print(f'金币增加: 1, 当前总数: {self.game_info["coin"]}')
                print(f'Debug: game_info["coin"] = {self.game_info["coin"]}')
                # 播放金币音效
                setup.SOUND.play_sound('coin')

    def update_game_info(self):
        if self.player.dead:
            self.game_info['lives']-=1
            self.game_info['coin']=0
            self.game_info['score']=0
        if self.game_info['lives']==0:
            self.next='game_over'
        else:
            self.next='load_screen'

