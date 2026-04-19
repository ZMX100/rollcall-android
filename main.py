#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
一点天惊 - 智能点名程序 Android版本
基于Kivy框架开发
"""

import os
import sys
import json
import random
import math
from datetime import datetime

# 添加screens目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'screens'))

# 导入工具函数
from utils import replace_emoji, get_emoji_font, get_default_font, FONT_CONFIG

# Kivy imports
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, Line, Ellipse, Triangle
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import StringProperty, ListProperty, BooleanProperty, NumericProperty, ObjectProperty, DictProperty
from kivy.utils import get_color_from_hex
from kivy.metrics import dp, sp
from kivy.storage.jsonstore import JsonStore
from kivy.config import Config

# 设置强制竖屏
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'fullscreen', '0')

# 设置窗口大小（开发时模拟手机屏幕）
Window.clearcolor = get_color_from_hex('#1a1a2e')
Window.size = (400, 800)

# 字体配置 - 使用系统默认字体以支持emoji
# Windows: 使用 Segoe UI Emoji
# Android: 使用系统默认字体（Roboto）
# 如需自定义字体，取消下面的注释并放置字体文件到 fonts/ 目录
# FONT_PATH = os.path.join(os.path.dirname(__file__), 'fonts', 'NotoColorEmoji.ttf')
# if not os.path.exists(FONT_PATH):
FONT_PATH = 'SimHei'  # 使用系统默认中文字体

# 尝试使用支持emoji的字体（如果系统有）
import platform
SYSTEM = platform.system()
if SYSTEM == 'Windows':
    EMOJI_FONT = 'Segoe UI Emoji'
elif SYSTEM == 'Darwin':  # macOS
    EMOJI_FONT = 'Apple Color Emoji'
else:  # Linux/Android
    EMOJI_FONT = 'Noto Color Emoji'

# 颜色定义 - 与原版保持一致
COLORS = {
    'bg_dark': '#1a1a2e',
    'bg_medium': '#16213e',
    'bg_light': '#0f3460',
    'accent_red': '#e94560',
    'accent_green': '#00ff88',
    'accent_blue': '#00d9ff',
    'accent_yellow': '#ffd700',
    'accent_purple': '#9b59b6',
    'accent_orange': '#f39c12',
    'text_light': '#ecf0f1',
    'text_gray': '#6c757d',
    'white': '#ffffff',
}

def hex_to_rgba(hex_color, alpha=1.0):
    """将十六进制颜色转换为RGBA"""
    c = get_color_from_hex(hex_color)
    return (c[0], c[1], c[2], alpha)


class LoadingScreen(Screen):
    """加载界面 - 复刻原版的加载效果"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        Clock.schedule_once(self.start_loading, 0.5)

    def build_ui(self):
        # 使用BoxLayout作为根布局，更稳定的竖屏布局
        root = BoxLayout(orientation='vertical')

        # 背景
        with root.canvas.before:
            Color(*hex_to_rgba(COLORS['bg_dark']))
            self.bg_rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self.update_bg, size=self.update_bg)

        # 顶部空白
        root.add_widget(Widget(size_hint_y=0.1))

        # 中央圆形装饰和文字区域 - 使用FloatLayout让圆套住"点"字
        center_box = FloatLayout(size_hint_y=0.45)

        # 圆形装饰和"点"字容器
        self.circle_container = Widget()
        with self.circle_container.canvas:
            # 外圆
            Color(*hex_to_rgba(COLORS['accent_red']))
            self.circle_outer = Line(circle=(0, 0, 0), width=dp(3))
            # 内圆
            self.circle_inner = Line(circle=(0, 0, 0), width=dp(1))
        center_box.add_widget(self.circle_container)

        # 中央大字"点" - 放在圆的中心
        self.char_label = Label(
            text='点',
            font_size=sp(80),
            font_name=get_default_font(),
            color=hex_to_rgba(COLORS['accent_red']),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        center_box.add_widget(self.char_label)

        center_box.bind(pos=self.update_circle, size=self.update_circle)
        root.add_widget(center_box)

        # 标语区域
        slogan_box = BoxLayout(orientation='vertical', size_hint_y=0.15, spacing=dp(5))

        # 主标语
        self.main_slogan = Label(
            text='一点天惊，点亮人生',
            font_size=sp(18),
            font_name=get_default_font(),
            color=hex_to_rgba(COLORS['accent_red']),
            size_hint_y=0.5
        )
        slogan_box.add_widget(self.main_slogan)

        # 副标语
        self.sub_slogan = Label(
            text='一点天惊出品，智能点名程序',
            font_size=sp(12),
            font_name=get_default_font(),
            color=hex_to_rgba(COLORS['accent_red']),
            size_hint_y=0.5
        )
        slogan_box.add_widget(self.sub_slogan)

        root.add_widget(slogan_box)

        # 进度条区域 - 进度条在框内显示（很细，左右变窄）
        progress_box = BoxLayout(orientation='vertical', size_hint_y=0.03, padding=[dp(140), dp(1)])

        # 进度条背景框
        self.progress_bg = Widget()
        with self.progress_bg.canvas:
            # 背景框
            Color(*hex_to_rgba(COLORS['bg_light']))
            self.progress_bg_rect = Rectangle(pos=(0, 0), size=(0, 0))
            # 边框
            Color(*hex_to_rgba(COLORS['accent_red']))
            self.progress_border = Line(rectangle=(0, 0, 0, 0), width=dp(1))

        # 进度条填充
        with self.progress_bg.canvas:
            Color(*hex_to_rgba(COLORS['accent_red']))
            self.progress_fill_rect = Rectangle(pos=(0, 0), size=(0, 0))

        progress_box.add_widget(self.progress_bg)
        progress_box.bind(pos=self.update_progress, size=self.update_progress)

        root.add_widget(progress_box)

        # 加载文字
        self.loading_text = Label(
            text='初始化系统环境...',
            font_size=sp(12),
            font_name=get_default_font(),
            color=hex_to_rgba(COLORS['accent_green']),
            size_hint_y=0.08
        )
        root.add_widget(self.loading_text)

        # 底部空白
        root.add_widget(Widget(size_hint_y=0.05))

        self.add_widget(root)

        # 启动动画
        Clock.schedule_interval(self.animate_loading, 0.05)

    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def update_circle(self, instance, value):
        """更新圆形装饰位置和大小 - 让圆套住"点"字"""
        center_x = instance.center_x
        center_y = instance.center_y
        # 圆的大小要能够套住"点"字
        radius = min(instance.width, instance.height) * 0.35
        self.circle_outer.circle = (center_x, center_y, radius)
        self.circle_inner.circle = (center_x, center_y, radius * 0.85)

    def update_progress(self, instance, value):
        """更新进度条位置和大小 - 进度条在框内显示（变细）"""
        # 背景框
        self.progress_bg_rect.pos = (instance.x, instance.y)
        self.progress_bg_rect.size = (instance.width, instance.height)
        # 边框（细线）
        self.progress_border.rectangle = (instance.x, instance.y, instance.width, instance.height)
        # 填充条（在框内，留小边距）
        padding = dp(1)
        self.progress_fill_rect.pos = (instance.x + padding, instance.y + padding)
        # 进度条宽度根据进度计算
        if not hasattr(self, 'progress_value'):
            self.progress_value = 0
        max_width = instance.width - 2 * padding
        self.progress_fill_rect.size = (max_width * self.progress_value, instance.height - 2 * padding)

    def animate_loading(self, dt):
        """加载动画"""
        self.char_label.opacity = 0.8 + 0.2 * math.sin(Clock.get_time() * 3)
        return True

    def start_loading(self, dt):
        """开始加载过程"""
        self.steps = [
            "初始化系统环境...",
            "检测Python环境...",
            "配置Python路径...",
            "检测必要的库...",
            "检查字体支持...",
            "配置特殊符号...",
            "启动主程序..."
        ]
        self.current_step = 0
        self.progress_value = 0
        Clock.schedule_interval(self.update_progress_step, 0.4)

    def update_progress_step(self, dt):
        """更新进度"""
        if self.current_step >= len(self.steps):
            Clock.unschedule(self.update_progress_step)
            self.loading_complete()
            return False

        self.loading_text.text = self.steps[self.current_step]
        # 更新进度值
        self.progress_value = (self.current_step + 1) / len(self.steps)
        # 触发进度条重绘
        if hasattr(self, 'progress_bg'):
            self.update_progress(self.progress_bg.parent, None)
        self.current_step += 1
        return True

    def loading_complete(self):
        """加载完成，切换到主界面"""
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'main'), 0.5)


class MainScreen(Screen):
    """主界面"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))

        # 背景
        with layout.canvas.before:
            Color(*hex_to_rgba(COLORS['bg_dark']))
            self.bg_rect = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=self.update_bg, size=self.update_bg)

        # 顶部空白
        layout.add_widget(Widget(size_hint_y=0.15))

        # 标题
        title = Label(
            text='您希望如何导入人名？',
            font_size=sp(22),
            font_name=get_default_font(),
            bold=True,
            color=hex_to_rgba(COLORS['accent_red']),
            size_hint_y=None,
            height=dp(50)
        )
        layout.add_widget(title)

        # 中间空白
        layout.add_widget(Widget(size_hint_y=0.05))

        # 按钮容器
        btn_container = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint_y=None,
            height=dp(200)
        )

        # 导入文件按钮
        btn_import = Button(
            text='📁 导入文件',
            font_size=sp(16),
            font_name=get_emoji_font(),
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_blue']),
            color=hex_to_rgba(COLORS['bg_dark'])
        )
        btn_import.bind(on_press=lambda x: setattr(self.manager, 'current', 'import'))
        btn_container.add_widget(btn_import)

        # 手动输入按钮
        btn_input = Button(
            text='✏️ 手动输入',
            font_size=sp(16),
            font_name=get_emoji_font(),
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_yellow']),
            color=hex_to_rgba(COLORS['bg_dark'])
        )
        btn_input.bind(on_press=lambda x: setattr(self.manager, 'current', 'input'))
        btn_container.add_widget(btn_input)

        # 从已有点名器中选择按钮
        btn_list = Button(
            text='📋 从已有点名器中选择',
            font_size=sp(16),
            font_name=get_emoji_font(),
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_green']),
            color=hex_to_rgba(COLORS['bg_dark'])
        )
        btn_list.bind(on_press=lambda x: setattr(self.manager, 'current', 'list'))
        btn_container.add_widget(btn_list)

        layout.add_widget(btn_container)

        # 填充剩余空间
        layout.add_widget(Widget(size_hint_y=0.3))

        # 底部装饰线
        footer_line = Widget(size_hint_y=None, height=dp(2))
        with footer_line.canvas:
            Color(*hex_to_rgba(COLORS['accent_red']))
            Rectangle(pos=(0, 0), size=(Window.width * 0.5, dp(2)))
        layout.add_widget(footer_line)

        # 底部文字
        footer = Label(
            text='一点天惊出品 v6.0.0.0',
            font_size=sp(12),
            font_name=get_default_font(),
            color=hex_to_rgba(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(footer)

        self.add_widget(layout)

    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size


class RollCallApp(App):
    """主应用类"""

    # 应用数据属性
    imported_names = ListProperty([])
    import_source = StringProperty('')
    expanded_names = ListProperty([])
    unique_names = ListProperty([])
    name_counts = DictProperty({})
    allow_repeat = BooleanProperty(False)
    current_rollcall_names = ListProperty([])
    current_rollcall_title = StringProperty('')
    current_allow_repeat = BooleanProperty(False)
    editing_rollcall_id = StringProperty('')
    editing_rollcall_data = DictProperty({})

    def get_data_dir(self):
        """获取数据目录"""
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        return data_dir

    def build(self):
        # 设置窗口标题
        self.title = '一点天惊 - 智能点名程序'

        # 创建屏幕管理器
        sm = ScreenManager(transition=FadeTransition())

        # 添加各个屏幕
        sm.add_widget(LoadingScreen(name='loading'))
        sm.add_widget(MainScreen(name='main'))

        # 延迟导入其他屏幕（避免循环导入）
        try:
            from screens.import_screen import ImportScreen
            from screens.input_screen import InputScreen
            from screens.rate_screen import RateScreen
            from screens.name_screen import NameScreen
            from screens.list_screen import ListScreen
            from screens.rollcall_screen import RollCallScreen
            from screens.edit_screen import EditScreen

            sm.add_widget(ImportScreen(name='import'))
            sm.add_widget(InputScreen(name='input'))
            sm.add_widget(RateScreen(name='rate'))
            sm.add_widget(NameScreen(name='name'))
            sm.add_widget(ListScreen(name='list'))
            sm.add_widget(RollCallScreen(name='rollcall'))
            sm.add_widget(EditScreen(name='edit'))

        except ImportError as e:
            print(f'导入屏幕模块失败: {e}')

        return sm


if __name__ == '__main__':
    RollCallApp().run()
