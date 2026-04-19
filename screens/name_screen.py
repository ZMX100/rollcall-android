#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
命名界面 - 为点名器命名
"""

import os
import json
import uuid
from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.graphics import Color, Rectangle, Line
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.metrics import dp, sp

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import hex_to_rgba, COLORS
from utils import replace_emoji


class NameScreen(Screen):
    """命名界面"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_dir = self.get_data_dir()
        self.build_ui()

    def get_data_dir(self):
        """获取数据目录"""
        if os.path.exists('/sdcard'):
            data_dir = '/sdcard/RollCall'
        else:
            data_dir = os.path.join(os.path.expanduser('~'), '.rollcall')

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        return data_dir

    def build_ui(self):
        layout = FloatLayout()

        # 背景
        with layout.canvas.before:
            Color(*hex_to_rgba(COLORS['bg_dark']))
            self.bg_rect = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=self.update_bg, size=self.update_bg)

        # 标题
        title = Label(
            text='✨ 命名 ✨',
            font_size=sp(28),
            font_name='SimHei',
            bold=True,
            color=hex_to_rgba(COLORS['accent_red']),
            pos_hint={'center_x': 0.5, 'center_y': 0.85}
        )
        layout.add_widget(title)

        # 主内容区域
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(20),
            size_hint=(0.85, 0.5),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        # 输入框容器
        input_box = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(15)
        )

        with input_box.canvas.before:
            Color(*hex_to_rgba(COLORS['bg_medium']))
            self.input_bg = Rectangle(pos=input_box.pos, size=input_box.size)
            Color(*hex_to_rgba(COLORS['accent_red']))
            Line(rectangle=(input_box.x, input_box.y, input_box.width, input_box.height), width=dp(2))

        input_box.bind(pos=self.update_input_bg, size=self.update_input_bg)

        # 提示文字
        lbl_hint = Label(
            text='请为您的点名器命名：',
            font_size=sp(16),
            font_name='SimHei',
            color=hex_to_rgba(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        lbl_hint.bind(size=lbl_hint.setter('text_size'))
        input_box.add_widget(lbl_hint)

        # 名称输入框
        self.name_input = TextInput(
            multiline=False,
            font_size=sp(18),
            font_name='SimHei',
            background_color=hex_to_rgba(COLORS['bg_light']),
            foreground_color=hex_to_rgba(COLORS['text_light']),
            cursor_color=hex_to_rgba(COLORS['accent_green']),
            size_hint_y=None,
            height=dp(50),
            hint_text='输入点名器名称'
        )
        input_box.add_widget(self.name_input)

        # 统计信息
        self.stats_label = Label(
            text='',
            font_size=sp(14),
            font_name='SimHei',
            color=hex_to_rgba(COLORS['accent_green']),
            size_hint_y=None,
            height=dp(25)
        )
        input_box.add_widget(self.stats_label)

        content.add_widget(input_box)

        # 生成按钮
        btn_generate = Button(
            text='✨ 生成点名器',
            font_size=sp(18),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_green']),
            color=hex_to_rgba(COLORS['bg_dark']),
            size_hint_y=None,
            height=dp(55)
        )
        btn_generate.bind(on_press=self.generate_rollcall)
        content.add_widget(btn_generate)

        layout.add_widget(content)

        # 返回按钮
        btn_back = Button(
            text='↩ 返回',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_red']),
            color=hex_to_rgba(COLORS['white']),
            size_hint=(None, None),
            size=(dp(120), dp(45)),
            pos_hint={'center_x': 0.5, 'y': 0.1}
        )
        btn_back.bind(on_press=self.go_back)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def update_input_bg(self, instance, value):
        self.input_bg.pos = instance.pos
        self.input_bg.size = instance.size
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*hex_to_rgba(COLORS['bg_medium']))
            Rectangle(pos=instance.pos, size=instance.size)
            Color(*hex_to_rgba(COLORS['accent_red']))
            Line(rectangle=(instance.x, instance.y, instance.width, instance.height), width=dp(2))

    def on_enter(self):
        """进入界面时更新统计"""
        app = self.manager.parent
        if hasattr(app, 'unique_names'):
            count = len(app.unique_names)
            self.stats_label.text = f'共 {count} 个人名'

    def generate_rollcall(self, instance):
        """生成点名器"""
        name = self.name_input.text.strip()

        if not name:
            self.show_error('点名器名称不能为空！')
            return

        # 检查是否已存在
        index_file = os.path.join(self.data_dir, 'index.json')
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)

            for item in index:
                if item['name'] == name:
                    self.show_error(f'已存在同名点名器：{name}\n请使用不同的名称！')
                    return

        except Exception:
            index = []

        # 获取数据
        app = self.manager.parent
        if not hasattr(app, 'expanded_names') or not app.expanded_names:
            self.show_error('没有数据可保存！')
            return

        # 创建点名器数据
        rollcall_id = str(uuid.uuid4())[:8]
        data = {
            'id': rollcall_id,
            'name': name,
            'names': app.expanded_names,
            'unique_names': app.unique_names,
            'name_counts': app.name_counts,
            'allow_repeat': getattr(app, 'allow_repeat', False),
            'created_at': datetime.now().isoformat()
        }

        # 保存数据文件
        data_file = os.path.join(self.data_dir, f"{rollcall_id}.json")
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # 更新索引
        index.append({
            'id': rollcall_id,
            'name': name,
            'created_at': datetime.now().isoformat()
        })

        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

        # 显示成功信息
        self.show_success(
            f'生成成功！\n\n点名器 "{name}" 已创建\n可在【从已有点名器中选择】中运行',
            lambda: self.manager.current == 'list'
        )

    def go_back(self, instance):
        """返回"""
        self.manager.current = 'rate'

    def show_error(self, message):
        """显示错误信息"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        lbl = Label(
            text=message,
            font_size=sp(14),
            font_name='SimHei',
            color=hex_to_rgba(COLORS['accent_red'])
        )
        content.add_widget(lbl)

        btn = Button(
            text='确定',
            font_size=sp(14),
            font_name='SimHei',
            size_hint_y=None,
            height=dp(40),
            background_color=hex_to_rgba(COLORS['accent_red'])
        )
        content.add_widget(btn)

        popup = Popup(
            title='错误',
            content=content,
            size_hint=(0.8, 0.3),
            auto_dismiss=False
        )
        btn.bind(on_press=popup.dismiss)
        popup.open()

    def show_success(self, message, callback):
        """显示成功信息"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        lbl = Label(
            text=message,
            font_size=sp(14),
            font_name='SimHei',
            color=hex_to_rgba(COLORS['accent_green'])
        )
        content.add_widget(lbl)

        btn = Button(
            text='确定',
            font_size=sp(14),
            font_name='SimHei',
            size_hint_y=None,
            height=dp(40),
            background_color=hex_to_rgba(COLORS['accent_green'])
        )
        content.add_widget(btn)

        popup = Popup(
            title='成功',
            content=content,
            size_hint=(0.85, 0.35),
            auto_dismiss=False
        )

        def on_dismiss(btn):
            popup.dismiss()
            self.manager.current = 'list'

        btn.bind(on_press=on_dismiss)
        popup.open()
