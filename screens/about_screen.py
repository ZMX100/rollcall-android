#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
关于界面
"""

import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.metrics import dp, sp

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import hex_to_rgba, COLORS
from utils import replace_emoji


class AboutScreen(Screen):
    """关于界面"""

    VERSION = "6.0.0.0"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        layout = FloatLayout()

        # 背景
        with layout.canvas.before:
            Color(*hex_to_rgba(COLORS['bg_dark']))
            self.bg_rect = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=self.update_bg, size=self.update_bg)

        # 标题
        title = Label(
            text='✨ 关于 ✨',
            font_size=sp(28),
            font_name='SimHei',
            bold=True,
            color=hex_to_rgba(COLORS['accent_red']),
            pos_hint={'center_x': 0.5, 'center_y': 0.9}
        )
        layout.add_widget(title)

        # 内容区域
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(20),
            size_hint=(0.9, 0.65),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        with content.canvas.before:
            Color(*hex_to_rgba(COLORS['bg_medium']))
            self.content_bg = Rectangle(pos=content.pos, size=content.size)
            Color(*hex_to_rgba(COLORS['accent_red'], 0.5))
            Line(rectangle=(content.x, content.y, content.width, content.height), width=dp(2))

        content.bind(pos=self.update_content_bg, size=self.update_content_bg)

        # 应用名称
        app_name = Label(
            text='点名器生成器',
            font_size=sp(24),
            font_name='SimHei',
            bold=True,
            color=hex_to_rgba(COLORS['accent_yellow']),
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(app_name)

        # 版本号
        version = Label(
            text=f'版本: v{self.VERSION}',
            font_size=sp(16),
            font_name='SimHei',
            color=hex_to_rgba(COLORS['accent_green']),
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(version)

        # 分隔线
        sep = Widget(size_hint_y=None, height=dp(2))
        with sep.canvas:
            Color(*hex_to_rgba(COLORS['accent_red']))
            Rectangle(pos=sep.pos, size=sep.size)
        sep.bind(pos=self.update_sep, size=self.update_sep)
        content.add_widget(sep)

        # 功能介绍
        features = Label(
            text='一个功能强大的点名器生成工具\n\n支持导入文件、手动输入、爆率修改等功能\n\n特别适用于课堂点名、抽奖活动等场景',
            font_size=sp(14),
            font_name='SimHei',
            color=hex_to_rgba(COLORS['text_light']),
            halign='center'
        )
        features.bind(size=features.setter('text_size'))
        content.add_widget(features)

        # 检查更新按钮
        btn_update = Button(
            text='🔄 检查更新',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_blue']),
            color=hex_to_rgba(COLORS['bg_dark']),
            size_hint_y=None,
            height=dp(45)
        )
        btn_update.bind(on_press=self.check_update)
        content.add_widget(btn_update)

        layout.add_widget(content)

        # 返回按钮
        btn_back = Button(
            text='关闭',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_red']),
            color=hex_to_rgba(COLORS['white']),
            size_hint=(None, None),
            size=(dp(120), dp(45)),
            pos_hint={'center_x': 0.5, 'y': 0.08}
        )
        btn_back.bind(on_press=self.go_back)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def update_content_bg(self, instance, value):
        self.content_bg.pos = instance.pos
        self.content_bg.size = instance.size
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*hex_to_rgba(COLORS['bg_medium']))
            Rectangle(pos=instance.pos, size=instance.size)
            Color(*hex_to_rgba(COLORS['accent_red'], 0.5))
            Line(rectangle=(instance.x, instance.y, instance.width, instance.height), width=dp(2))

    def update_sep(self, instance, value):
        instance.canvas.clear()
        with instance.canvas:
            Color(*hex_to_rgba(COLORS['accent_red']))
            Rectangle(pos=instance.pos, size=instance.size)

    def check_update(self, instance):
        """检查更新"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        lbl = Label(
            text='正在检查更新，请稍候...',
            font_size=sp(14),
            font_name='SimHei',
            color=hex_to_rgba(COLORS['accent_green'])
        )
        content.add_widget(lbl)

        popup = Popup(
            title='检查更新',
            content=content,
            size_hint=(0.7, 0.25),
            auto_dismiss=False
        )
        popup.open()

        # 模拟检查更新
        def show_result(dt):
            popup.dismiss()
            self.show_message('检查更新', f'当前已是最新版本！\n\n当前版本: v{self.VERSION}')

        Clock.schedule_once(show_result, 1.5)

    def go_back(self, instance):
        """返回"""
        self.manager.current = 'main'

    def show_message(self, title, message):
        """显示消息"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        lbl = Label(
            text=message,
            font_size=sp(14),
            font_name='SimHei',
            color=hex_to_rgba(COLORS['text_light'])
        )
        content.add_widget(lbl)

        btn = Button(
            text='确定',
            font_size=sp(14),
            font_name='SimHei',
            size_hint_y=None,
            height=dp(40),
            background_color=hex_to_rgba(COLORS['accent_blue'])
        )
        content.add_widget(btn)

        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.35),
            auto_dismiss=False
        )
        btn.bind(on_press=popup.dismiss)
        popup.open()
