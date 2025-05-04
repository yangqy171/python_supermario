#音效系统
import pygame
import os
from . import constants as C

class Sound:
    """音效管理类，负责加载和播放游戏中的音效和音乐"""
    def __init__(self):
        """初始化音效系统"""
        self.sound_dir = os.path.join('resources', 'sound')
        self.music_dir = os.path.join('resources', 'music')
        
        self.sound_dict = {}  # 存储音效
        self.music_dict = {}  # 存储音乐
        
        # 加载所有音效和音乐
        self.load_sounds()
        self.load_music()
        
        # 设置音量
        self.set_volumes()
        
        # 当前播放的背景音乐
        self.current_music = None
    
    def load_sounds(self):
        """加载所有音效文件"""
        for sound_file in os.listdir(self.sound_dir):
            name, ext = os.path.splitext(sound_file)
            if ext.lower() in ('.wav', '.ogg'):
                self.sound_dict[name] = pygame.mixer.Sound(os.path.join(self.sound_dir, sound_file))
    
    def load_music(self):
        """加载所有音乐文件"""
        for music_file in os.listdir(self.music_dir):
            name, ext = os.path.splitext(music_file)
            if ext.lower() in ('.wav', '.ogg'):
                self.music_dict[name] = os.path.join(self.music_dir, music_file)
    
    def set_volumes(self):
        """设置音效和音乐的音量"""
        for sound in self.sound_dict.values():
            sound.set_volume(0.3)
    
    def play_sound(self, key):
        """播放指定的音效
        Args:
            key: 音效的名称
        """
        if key in self.sound_dict:
            self.sound_dict[key].play()
    
    def stop_sound(self, key):
        """停止指定的音效
        Args:
            key: 音效的名称
        """
        if key in self.sound_dict:
            self.sound_dict[key].stop()
    
    def play_music(self, key):
        """播放指定的背景音乐
        Args:
            key: 音乐的名称
        """
        if key in self.music_dict and (self.current_music != key or not pygame.mixer.music.get_busy()):
            pygame.mixer.music.load(self.music_dict[key])
            pygame.mixer.music.play(-1)  # -1表示循环播放
            self.current_music = key
    
    def stop_music(self):
        """停止当前播放的背景音乐"""
        pygame.mixer.music.stop()
        self.current_music = None
    
    def pause_music(self):
        """暂停当前播放的背景音乐"""
        pygame.mixer.music.pause()
    
    def unpause_music(self):
        """恢复播放暂停的背景音乐"""
        pygame.mixer.music.unpause()
    
    def fadeout_music(self, time=500):
        """淡出当前播放的背景音乐
        Args:
            time: 淡出时间(毫秒)
        """
        pygame.mixer.music.fadeout(time)
        self.current_music = None