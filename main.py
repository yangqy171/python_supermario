#游戏主要入口
import pygame
from source import tools,setup
from source.states import main_menu,load_screen,level,game_complete
def main():
    state_dict={'main_menu':main_menu.MainMenu(),
                'load_screen':load_screen.LoadScreen(),
                'level':level.Level(),
                'game_over':load_screen.GameOver(),
                'game_complete':game_complete.GameComplete()}
    game = tools.Game(state_dict,'main_menu')
    game.run()

if __name__=='__main__':
    main()