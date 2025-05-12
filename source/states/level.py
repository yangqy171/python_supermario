from ..components import info
import pygame
from .. import setup,tools
from.. import constants as C
from ..components import player,stuff,brick,box,enemy,info
import json,os

class Level:
    def start(self,game_info):
        self.game_info=game_info
        self.finished = False
        self.next = 'game_over'
        # 确保游戏信息中包含必要的数据
        if 'level_num' not in self.game_info:
            self.game_info['level_num'] = 1
        
        self.flag_pole_complete = False  # 标记是否完成旗杆滑动
        self.castle_timer = 0  # 城堡计时器
        
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
        self.active_enemy_groups = set() # 初始化已激活的敌人组集合

    def load_map_data(self):
        # 根据游戏信息中的关卡编号加载对应地图
        level_num = self.game_info.get('level_num', 1)
        file_name = f'level_{level_num}.json'
        
        # 尝试多个可能的路径
        paths_to_try = [
            # 1. 相对于当前脚本的路径
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'maps', file_name),
            # 2. 相对于项目根目录的路径
            os.path.join('SuperMario', 'source', 'data', 'maps', file_name),
            # 3. 相对于游戏目录的路径
            os.path.join('game', 'SuperMario', 'source', 'data', 'maps', file_name),
            # 4. 尝试使用PySuperMario的地图
            os.path.join('PySuperMario', 'source', 'data', 'maps', file_name)
        ]
        
        # 初始化默认地图数据
        self.map_data = {
            'image_name': 'level_1',
            'maps': [
                {'start_x': 0, 'end_x': 9086, 'player_x': 110, 'player_y': 538}
            ],
            'ground': [],
            'pipe': [],
            'step': [],
            'brick': [],
            'box': [],
            'enemy': [],
            'checkpoint': [],
            'flagpole': []
        }
        
        # 尝试加载地图数据
        for path in paths_to_try:
            print(f'尝试加载地图文件: {path}')
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        loaded_data = json.load(f)
                        print(f'成功加载地图数据，键: {list(loaded_data.keys())}')
                        
                        # 处理第三关特殊情况，如果缺少maps键但有其他必要数据
                        if 'maps' not in loaded_data and level_num == 3:
                            print(f'第三关缺少maps键，添加默认maps数据')
                            loaded_data['maps'] = [
                                {'start_x': 0, 'end_x': 7000, 'player_x': 110, 'player_y': 538}
                            ]
                            self.map_data = loaded_data
                            print(f'使用修正后的地图文件: {path}')
                            break
                        # 正常情况下检查maps键
                        elif 'maps' in loaded_data:
                            self.map_data = loaded_data
                            print(f'使用地图文件: {path}')
                            break
                        else:
                            print(f'地图文件缺少maps键: {path}')
                except Exception as e:
                    print(f'加载地图文件出错: {path}, 错误: {e}')
        
        # 确保所有必要的键都存在
        required_keys = ['maps', 'ground', 'pipe', 'step', 'brick', 'box', 'enemy', 'checkpoint', 'flagpole']
        for key in required_keys:
            if key not in self.map_data:
                print(f'地图数据缺少键: {key}，添加空列表')
                self.map_data[key] = []
                
        print(f'最终地图数据键: {list(self.map_data.keys())}')
        return self.map_data

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
        self.type3_pipe_sprites_group = pygame.sprite.Group() # New group for type 3 pipes
        self.type3_pipe_rects = []  # 记录type=3管道的rect信息
        for name in ['ground','pipe','step']:
            for item in self.map_data[name]:
                sprite = stuff.Item(item['x'],item['y'],item['width'],item['height'],name)
                self.ground_item_group.add(sprite)
                if name == 'pipe' and item.get('type') == 3:
                    self.type3_pipe_sprites_group.add(sprite)
                    self.type3_pipe_rects.append(pygame.Rect(item['x'], item['y'], item['width'], item['height']))
                
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
        self.flag = None  # 初始化旗子引用
        
        try:
            # 从地图数据中读取旗杆信息
            if 'flagpole' in self.map_data and self.map_data['flagpole']:
                for data in self.map_data['flagpole']:
                    try:
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
                        else:
                            print(f"未知的旗杆类型: {data['type']}")
                            continue
                        
                        self.flagpole_group.add(sprite)
                    except Exception as e:
                        print(f"创建旗杆部件时出错: {e}, 数据: {data}")
        except Exception as e:
            print(f"设置旗杆时出错: {e}")
            import traceback
            traceback.print_exc()
        
    def setup_enemies(self):
        self.dying_group=pygame.sprite.Group()
        self.shell_group=pygame.sprite.Group()
        self.enemy_group=pygame.sprite.Group()
        self.enemy_group_dict={}
        try:
            for enemy_group_data in self.map_data['enemy']:
                group=pygame.sprite.Group()
                for enemy_group_id,enemy_list in enemy_group_data.items():
                    for enemy_data in enemy_list:
                        try:
                            enemy_obj = enemy.create_enemy(enemy_data)
                            group.add(enemy_obj)
                            print(f"成功创建敌人: 类型={enemy_data['type']}")
                        except Exception as e:
                            print(f"创建敌人失败: {e}, 数据: {enemy_data}")
                    self.enemy_group_dict[enemy_group_id]=group
        except Exception as e:
            print(f"设置敌人时出错: {e}")
            import traceback
            traceback.print_exc()
    def setup_checkpoint(self):
        self.checkpoint_group=pygame.sprite.Group()
        for item in self.map_data['checkpoint']:
            x,y,w,h=item['x'],item['y'],item['width'],item['height']
            checkpoint_type=item['type']
            enemy_groupid=item.get('enemy_groupid')
            self.checkpoint_group.add(stuff.Checkpoint(x,y,w,h,checkpoint_type,enemy_groupid))

    def check_player_position(self):
        """检查玩家位置并在关卡末尾更新关卡编号"""
        if self.finished: # If already finished (e.g. by flagpole or previous call), do nothing
            return

        player_x = self.player.rect.x
        # player_y = self.player.rect.y # player_y is not used in this logic
        current_level_num = self.game_info['level_num']
        
        should_trigger_finish = False
        target_level = current_level_num + 1 # Default next level if general condition met

        # General condition: Reaching the defined end of the map
        if player_x >= self.end_x:
            should_trigger_finish = True
            print(f"关卡结束条件满足 (general, player_x: {player_x} >= end_x: {self.end_x}, current_level: {current_level_num})")

        # Specific condition for Level 2, if player reaches x=8184
        # Added based on the proposal to ensure transition for level 2 at this point.
        if current_level_num == 2 and player_x >= 8184: # Use if as the level 1 specific x-coordinate check is removed
            should_trigger_finish = True
            target_level = 3 # Explicitly set next level to 3 for this specific trigger
            print(f"关卡结束条件满足 (level 2 specific, player_x: {player_x} >= 8184)")
        if current_level_num == 3 and player_x >= 6926: # Use if as the level 1 specific x-coordinate check is removed
            should_trigger_finish = True
            target_level = 4 # Explicitly set next level to 3 for this specific trigger
            print(f"关卡结束条件满足 (level 3 specific, player_x: {player_x} >= 6199)")
        if current_level_num == 4 and player_x >= 6809: # Use if as the level 1 specific x-coordinate check is removed
            # 游戏通关，切换到通关界面
            self.finished = True
            self.next = 'game_complete'  # 切换到通关状态
            print(f"游戏通关！ (level 4 specific, player_x: {player_x} >= 6809)")
            
            # 更新最高分
            try:
                current_score = self.game_info.get('score', 0)
                info_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'Info.json')
                
                # 读取现有最高分
                if os.path.exists(info_path):
                    with open(info_path, 'r') as f:
                        data = json.load(f)
                        topscore = data.get('topscore', 0)
                else:
                    topscore = 0
                
                # 比较并更新
                if current_score > topscore:
                    data['topscore'] = current_score
                    with open(info_path, 'w') as f:
                        json.dump(data, f)
                    print(f'更新最高分: {current_score}')
            except Exception as e:
                print(f'更新最高分失败: {e}')
            

        if should_trigger_finish:
            # Ensure self.finished is checked before modifying game_info,
            # though the initial guard `if self.finished: return` should cover this.
            self.game_info['level_num'] = target_level
            self.finished = True
            self.next = 'load_screen'  # Ensure the game knows to load the next level
            # Note: The 'next' state after finishing a level (e.g., 'load_level', 'game_over')
            # is typically handled where self.finished is checked in the main game loop or state manager.
            # This method focuses on setting the 'finished' flag and updating 'level_num'.
            print(f"最终决定：切换到关卡 {self.game_info['level_num']}. Next state: {self.next}")

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
            self.check_player_position() # Added this line

        self.draw(surface)
    def is_frozen(self):
        # 检查玩家是否处于变身状态，此时游戏应该暂停其他更新
        frozen = self.player.state in ['small2big','big2small','big2fire','fire2small']
        return frozen


    def update_player_position(self):
        # 更新玩家位置的逻辑
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
            #print(f'Player position: x={self.player.rect.x}, y={self.player.rect.y}')

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
            if enemy.name=='Piranha':
                self.player.go_die()
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

        self.dying_group.draw(self.game_ground)
        self.shell_group.draw(self.game_ground)
        self.flagpole_group.draw(self.game_ground)
        self.enemy_group.draw(self.game_ground)
        # 用地图图片抠出type=3管道区域，覆盖在所有元素之上
        if hasattr(self, 'type3_pipe_rects'):
            for rect in self.type3_pipe_rects:
                pipe_img = self.background.subsurface(rect).copy()
                self.game_ground.blit(pipe_img, rect)
        # 绘制信息栏等
        surface.blit(self.game_ground, (0,0),self.game_window)
        self.info.draw(surface)
    def check_checkpoints(self):
        collided_checkpoints = pygame.sprite.spritecollide(self.player, self.checkpoint_group, False) # dokill=False, manual kill later

        for checkpoint in collided_checkpoints:
            group_id_attr = getattr(checkpoint, 'enemy_groupid', None) # Safely get enemy_groupid
            # Basic log for any checkpoint collision
            print(f"DEBUG: Player collided with checkpoint: type={checkpoint.checkpoint_type}, original enemy_groupid='{group_id_attr}' at pos ({checkpoint.rect.x}, {checkpoint.rect.y})")

            if checkpoint.checkpoint_type == 0:  # Assuming 0 is for activating enemies
                if group_id_attr is None:
                    print(f"DEBUG: Checkpoint (type 0) is missing 'enemy_groupid' attribute.")
                    checkpoint.kill() # Kill misconfigured checkpoint
                    continue

                group_id_str = str(group_id_attr)

                if group_id_str in self.active_enemy_groups:
                    print(f"DEBUG: Enemy group '{group_id_str}' already activated. Skipping.")
                elif group_id_str in self.enemy_group_dict:
                    enemy_sub_group = self.enemy_group_dict[group_id_str]
                    self.enemy_group.add(enemy_sub_group.sprites())  # Add individual sprites from the sub-group
                    self.active_enemy_groups.add(group_id_str) # Mark as activated
                    print(f"DEBUG: Activated enemy group ID '{group_id_str}'. Added {len(enemy_sub_group.sprites())} enemies to self.enemy_group.")
                    
                    # Detailed logging for each enemy in the activated group
                    for i, enemy_sprite in enumerate(enemy_sub_group.sprites()):
                        enemy_name = getattr(enemy_sprite, 'name', 'UnknownName')
                        # Try to get 'type' as well, as it might be more specific for piranhas
                        enemy_type_attr = getattr(enemy_sprite, 'type', 'UnknownType') 
                        print(f"DEBUG:   - Enemy {i+1}/{len(enemy_sub_group.sprites())}: Name='{enemy_name}', Type='{enemy_type_attr}', Pos=({enemy_sprite.rect.x},{enemy_sprite.rect.y})")
                        # Check name or type for 'piranha'
                        is_piranha = False
                        if 'piranha' in enemy_name.lower():
                            is_piranha = True
                        elif isinstance(enemy_type_attr, str) and 'piranha' in enemy_type_attr.lower():
                            is_piranha = True
                        
                        if is_piranha:
                            print(f"DEBUG:     >>>> Piranha plant '{enemy_name}' (Type: '{enemy_type_attr}') from group '{group_id_str}' is now in self.enemy_group.")
                else:
                    print(f"DEBUG: Error: Enemy group ID '{group_id_str}' (from checkpoint) not found in self.enemy_group_dict.")
                    print(f"DEBUG:   Available enemy_group_dict keys: {list(self.enemy_group_dict.keys())}")
            else:
                print(f"DEBUG: Checkpoint type is {checkpoint.checkpoint_type}, not an enemy activation checkpoint (type 0).")
            
            checkpoint.kill() # Kill the checkpoint after processing, as in original code
    def check_if_go_die(self):
        if self.player.rect.y>C.SCREEN_H:
            self.player.go_die()
            
    def check_flagpole_collisions(self):
        """检查玩家与旗杆的碰撞"""
        # 只有当玩家不处于死亡或变身状态时才检查
        if self.player.dead or self.is_frozen():
            return
            
        # 如果旗子已经到达底部，处理关卡完成逻辑
        if hasattr(self, 'flag') and self.flag is not None and self.flag.state == 'bottom':
            if not self.flag_pole_complete:
                # 设置旗杆完成标志
                self.flag_pole_complete = True
                # 设置城堡计时器
                self.castle_timer = self.current_time
                # 播放关卡完成音效
                setup.SOUND.play_music('flagpole')
                # 让玩家向右走向城堡
                self.player.state = 'walk_auto'
                self.player.hurt_immune = True # Make player immune during walk to castle
                self.player.x_vel = 1
                self.player.facing_right = True
            elif self.current_time - self.castle_timer > 3000:
                # 3秒后完成关卡
                self.finished = True
                self.update_game_info()
            return
            
        # 检查与旗杆组的碰撞
        flagpole_hit = pygame.sprite.spritecollideany(self.player, self.flagpole_group)
        if flagpole_hit:
            # 如果已经完成滑旗，不再切换状态
            if getattr(self.player, 'flag_sliding_complete', False):
                return
            elif self.player.state != 'flagpole':
                self.player.state = 'flagpole'
                self.player.hurt_immune = True # Make player immune during flagpole slide
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
                if self.flag is not None and self.flag.state == 'top':
                    self.flag.state = 'slide'
                    # 播放旗杆音效
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
                self.game_info['score'] = self.game_info.get('score', 0) + 100
                print(f'金币增加: 1, 当前总数: {self.game_info["coin"]}')
                print(f'Debug: game_info["coin"] = {self.game_info["coin"]}')
                # 播放金币音效
                setup.SOUND.play_sound('coin')

    def update_game_info(self):
        if self.flag_pole_complete:
            # 玩家通过旗杆完成关卡
            current_level = self.game_info.get('level_num', 1)
            next_level = current_level + 1
            self.game_info['level_num'] = next_level
            print(f'关卡完成！进入第{next_level}关')
            self.game_info['score'] += 1000  # 完成关卡奖励1000分
            
            # 即使玩家在自动走向城堡的过程中“死亡”（例如掉入坑中），
            # 这仍然算作关卡完成，不应扣减生命。
            # self.finished 标志已在 check_flagpole_collisions 中设置。
            self.next = 'load_screen'  # 设置状态以加载下一关
            setup.SOUND.stop_music()
            setup.SOUND.play_music('main_theme')
        elif self.player.dead:
            # 玩家正常死亡（非旗杆完成过程中的意外）
            self.game_info['lives'] -= 1
            if self.game_info['lives'] == 0:
                self.game_info['coin'] = 0
                self.game_info['score'] = 0
                self.next = 'game_over'
            else:
                self.next = 'load_screen'  # 重新加载当前关卡
        else:
            # 此情况理论上不应发生，因为 update_game_info 主要由 player.dead 
            # 或 flag_pole_complete (导致 self.finished) 触发。
            # 为安全起见，根据生命值设置下一个状态。
            if self.game_info.get('lives', 0) > 0:
                self.next = 'load_screen'
            else:
                self.next = 'game_over'

