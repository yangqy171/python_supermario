#主菜单
import pygame
from .. import setup
from .. import tools
from .. import constants as C
from ..components import info
import os
import json
class MainMenu:
    def __init__(self):
        game_info={
            'score':0,
            'coin':0,
            'lives':3,
            'player_state':'small',
            'level_num':1,
        }
        self.start(game_info)
    def start(self,game_info):
        self.game_info=game_info
        self.setup_background()
        self.setup_player()
        self.setup_cursor()
        self.info=info.Info('main_menu',self.game_info)
        self.finished=False
        self.next='load_screen'
        # 播放主菜单背景音乐
        setup.SOUND.play_music('main_theme')

    def setup_background(self):
        self.background=setup.GRAPHICS['level_1']
        self.background_rect=self.background.get_rect()
        self.background=pygame.transform.scale(self.background,(int(self.background_rect.width*C.BG_MULTI),int(self.background_rect.height*C.BG_MULTI)))
        self.view_port=setup.SCREEN.get_rect()
        self.caption=tools.get_image(setup.GRAPHICS['title_screen'],1,60,176,88,(255,0,220),C.BG_MULTI)
    def setup_player(self):
        self.player_image=tools.get_image(setup.GRAPHICS['mario_bros'],178,32,12,16,(0,0,0),C.PLAYER_MULTI)

    def update_cursor(self,keys):
        if keys[pygame.K_UP]:
            self.cursor.state='1P'
            self.cursor.rect.y=360
        elif keys[pygame.K_DOWN]:
            self.cursor.state='2P'
            self.cursor.rect.y=405
        elif keys[pygame.K_RETURN]:
            if self.cursor.state=='1P':
                self.reset_game_info()
                self.finished=True
            elif self.cursor.state=='2P':
                self.load_game_info() # 修改为加载游戏信息
                self.finished=True

    def setup_cursor(self):
        self.cursor=pygame.sprite.Sprite()
        self.cursor.image=tools.get_image(setup.GRAPHICS['item_objects'],24,160,8,8,(0,0,0),C.PLAYER_MULTI)
        rect=self.cursor.image.get_rect()
        rect.x,rect.y=(220,360)
        self.cursor.rect=rect
        self.cursor.state='1P'#状态机



    def update(self,surface,keys):
        self.update_cursor(keys)

        surface.blit(self.background,self.view_port)
        surface.blit(self.caption,(170,100))
        surface.blit(self.player_image,(110,490))
        surface.blit(self.cursor.image, self.cursor.rect)

        self.info.update()
        self.info.draw(surface)

    def load_game_info(self):
        """从Info.json加载游戏信息."""
        try:
            info_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'Info.json')
            if os.path.exists(info_path):
                with open(info_path, 'r') as f:
                    data = json.load(f)
                    # 从加载的数据更新game_info，保留topscore
                    self.game_info['score'] = data.get('score', 0)
                    self.game_info['coin'] = data.get('coin', 0)
                    self.game_info['lives'] = data.get('lives', 3)
                    self.game_info['player_state'] = data.get('player_state', 'small')
                    self.game_info['level_num'] = data.get('level_num', 1)
                    # topscore 通常在info组件中处理，这里确保game_info本身不直接覆盖它，除非特定逻辑需要
                    # self.game_info['topscore'] = data.get('topscore', 0) # 通常topscore不应由此处重置
                    print(f"成功从Info.json加载游戏状态: {self.game_info}")
            else:
                print("Info.json 文件未找到，使用默认游戏状态。")
                self.reset_game_info() # 如果文件不存在，则使用默认值
        except Exception as e:
            print(f"从Info.json加载游戏状态失败: {e}，使用默认游戏状态。")
            self.reset_game_info() # 出错则使用默认值
    def reset_game_info(self):
        self.game_info.update(
            {
                'score':0,
                'coin':0,
                'lives':3,
                'player_state':'small',
                'level_num':1           }
        )
