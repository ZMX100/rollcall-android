#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
爆率修改界面
"""

import os
from collections import Counter
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
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
from kivy.properties import ListProperty, DictProperty, StringProperty

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import hex_to_rgba, COLORS
from utils import replace_emoji


class RateScreen(Screen):
    """爆率修改界面"""

    names = ListProperty([])
    name_counts = DictProperty({})
    unique_names = ListProperty([])

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
            text='✨ 爆率修改器 ✨',
            font_size=sp(24),
            font_name='SimHei',
            bold=True,
            color=hex_to_rgba(COLORS['accent_red']),
            pos_hint={'center_x': 0.5, 'center_y': 0.94}
        )
        layout.add_widget(title)

        # 主内容区域 - 左右布局
        content = BoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint=(0.95, 0.78),
            pos_hint={'center_x': 0.5, 'center_y': 0.48}
        )

        # 左侧 - 人名列表
        left_box = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_x=0.6
        )

        list_title = Label(
            text='📋 人名列表',
            font_size=sp(16),
            font_name='SimHei',
            bold=True,
            color=hex_to_rgba(COLORS['accent_red']),
            size_hint_y=None,
            height=dp(30)
        )
        left_box.add_widget(list_title)

        # 列表容器
        list_container = BoxLayout(orientation='vertical')
        with list_container.canvas.before:
            Color(*hex_to_rgba(COLORS['bg_medium']))
            self.list_bg = Rectangle(pos=list_container.pos, size=list_container.size)
            Color(*hex_to_rgba(COLORS['accent_red']))
            Line(rectangle=(list_container.x, list_container.y, list_container.width, list_container.height), width=dp(2))
        list_container.bind(pos=self.update_list_bg, size=self.update_list_bg)

        self.scroll = ScrollView()
        self.list_layout = BoxLayout(orientation='vertical', spacing=dp(2), size_hint_y=None, padding=dp(5))
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        self.scroll.add_widget(self.list_layout)
        list_container.add_widget(self.scroll)
        left_box.add_widget(list_container)

        content.add_widget(left_box)

        # 右侧 - 控制面板
        right_box = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_x=0.4
        )

        control_title = Label(
            text='⚙️ 控制面板',
            font_size=sp(16),
            font_name='SimHei',
            bold=True,
            color=hex_to_rgba(COLORS['accent_red']),
            size_hint_y=None,
            height=dp(30)
        )
        right_box.add_widget(control_title)

        # 控制面板容器
        control_container = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(10)
        )
        with control_container.canvas.before:
            Color(*hex_to_rgba(COLORS['bg_medium']))
            self.control_bg = Rectangle(pos=control_container.pos, size=control_container.size)
            Color(*hex_to_rgba(COLORS['accent_blue']))
            Line(rectangle=(control_container.x, control_container.y, control_container.width, control_container.height), width=dp(2))
        control_container.bind(pos=self.update_control_bg, size=self.update_control_bg)

        # 选中的人名显示
        lbl_selected = Label(
            text='选中的人名：',
            font_size=sp(12),
            font_name='SimHei',
            color=hex_to_rgba(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(20),
            halign='left'
        )
        lbl_selected.bind(size=lbl_selected.setter('text_size'))
        control_container.add_widget(lbl_selected)

        self.selected_name_label = Label(
            text='请选择一个人名',
            font_size=sp(16),
            font_name='SimHei',
            bold=True,
            color=hex_to_rgba(COLORS['accent_green']),
            size_hint_y=None,
            height=dp(40)
        )
        with self.selected_name_label.canvas.before:
            Color(*hex_to_rgba(COLORS['bg_light']))
            self.selected_bg = Rectangle(pos=self.selected_name_label.pos, size=self.selected_name_label.size)
        self.selected_name_label.bind(pos=self.update_selected_bg, size=self.update_selected_bg)
        control_container.add_widget(self.selected_name_label)

        # 出现次数
        lbl_count = Label(
            text='出现次数：',
            font_size=sp(12),
            font_name='SimHei',
            color=hex_to_rgba(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(20),
            halign='left'
        )
        lbl_count.bind(size=lbl_count.setter('text_size'))
        control_container.add_widget(lbl_count)

        self.count_input = TextInput(
            text='0',
            multiline=False,
            font_size=sp(20),
            font_name='SimHei',
            background_color=hex_to_rgba(COLORS['bg_light']),
            foreground_color=hex_to_rgba(COLORS['text_light']),
            cursor_color=hex_to_rgba(COLORS['accent_green']),
            size_hint_y=None,
            height=dp(45),
            halign='center'
        )
        control_container.add_widget(self.count_input)

        # 增减按钮
        btn_row = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(45))

        btn_inc = Button(
            text='▲ 增加',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_blue']),
            color=hex_to_rgba(COLORS['bg_dark'])
        )
        btn_inc.bind(on_press=self.increment_count)

        btn_dec = Button(
            text='▼ 减少',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_blue']),
            color=hex_to_rgba(COLORS['bg_dark'])
        )
        btn_dec.bind(on_press=self.decrement_count)

        btn_row.add_widget(btn_inc)
        btn_row.add_widget(btn_dec)
        control_container.add_widget(btn_row)

        # 确定修改按钮
        btn_confirm = Button(
            text='✅ 确定修改',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_green']),
            color=hex_to_rgba(COLORS['white']),
            size_hint_y=None,
            height=dp(45)
        )
        btn_confirm.bind(on_press=self.confirm_change)
        control_container.add_widget(btn_confirm)

        # 可重复点名选项
        repeat_box = BoxLayout(spacing=dp(5), size_hint_y=None, height=dp(40))

        self.repeat_checkbox = CheckBox(
            size_hint_x=None,
            width=dp(30),
            color=hex_to_rgba(COLORS['accent_blue'])
        )

        lbl_repeat = Label(
            text='🔄 可重复点名',
            font_size=sp(12),
            font_name='SimHei',
            color=hex_to_rgba(COLORS['accent_blue'])
        )

        repeat_box.add_widget(self.repeat_checkbox)
        repeat_box.add_widget(lbl_repeat)
        control_container.add_widget(repeat_box)

        right_box.add_widget(control_container)
        content.add_widget(right_box)

        layout.add_widget(content)

        # 底部按钮
        bottom_box = BoxLayout(
            spacing=dp(10),
            size_hint=(None, None),
            size=(dp(360), dp(50)),
            pos_hint={'center_x': 0.5, 'y': 0.02}
        )

        btn_generate = Button(
            text='✅ 生成',
            font_size=sp(16),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_green']),
            color=hex_to_rgba(COLORS['bg_dark'])
        )
        btn_generate.bind(on_press=self.generate_rollcall)

        btn_reset = Button(
            text='🔄 恢复',
            font_size=sp(16),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_yellow']),
            color=hex_to_rgba(COLORS['bg_dark'])
        )
        btn_reset.bind(on_press=self.reset_counts)

        btn_back = Button(
            text='↩ 返回',
            font_size=sp(16),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_red']),
            color=hex_to_rgba(COLORS['white'])
        )
        btn_back.bind(on_press=self.go_back)

        bottom_box.add_widget(btn_generate)
        bottom_box.add_widget(btn_reset)
        bottom_box.add_widget(btn_back)
        layout.add_widget(bottom_box)

        self.add_widget(layout)

    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def update_list_bg(self, instance, value):
        self.list_bg.pos = instance.pos
        self.list_bg.size = instance.size
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*hex_to_rgba(COLORS['bg_medium']))
            Rectangle(pos=instance.pos, size=instance.size)
            Color(*hex_to_rgba(COLORS['accent_red']))
            Line(rectangle=(instance.x, instance.y, instance.width, instance.height), width=dp(2))

    def update_control_bg(self, instance, value):
        self.control_bg.pos = instance.pos
        self.control_bg.size = instance.size
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*hex_to_rgba(COLORS['bg_medium']))
            Rectangle(pos=instance.pos, size=instance.size)
            Color(*hex_to_rgba(COLORS['accent_blue']))
            Line(rectangle=(instance.x, instance.y, instance.width, instance.height), width=dp(2))

    def update_selected_bg(self, instance, value):
        self.selected_bg.pos = instance.pos
        self.selected_bg.size = instance.size

    def on_enter(self):
        """进入界面时加载数据"""
        app = self.manager.parent
        if hasattr(app, 'imported_names'):
            self.names = app.imported_names
            # 统计人名出现次数
            counter = Counter(self.names)
            self.unique_names = list(counter.keys())
            self.name_counts = dict(counter)
            self.refresh_list()

    def refresh_list(self):
        """刷新列表显示"""
        self.list_layout.clear_widgets()
        self.list_buttons = []

        for i, name in enumerate(self.unique_names):
            count = self.name_counts.get(name, 1)

            row = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(5))

            btn = Button(
                text=f'{i+1}. {name} (出现次数: {count})',
                font_size=sp(13),
                font_name='SimHei',
                background_color=hex_to_rgba(COLORS['bg_light']),
                color=hex_to_rgba(COLORS['text_light']),
                halign='left'
            )
            btn.bind(on_press=lambda x, idx=i: self.select_name(idx))
            btn.name_index = i
            self.list_buttons.append(btn)

            row.add_widget(btn)
            self.list_layout.add_widget(row)

    def select_name(self, index):
        """选择人名"""
        self.selected_index = index
        name = self.unique_names[index]
        count = self.name_counts.get(name, 1)

        self.selected_name_label.text = name
        self.count_input.text = str(count)

        # 高亮选中的按钮
        for i, btn in enumerate(self.list_buttons):
            if i == index:
                btn.background_color = hex_to_rgba(COLORS['accent_red'])
            else:
                btn.background_color = hex_to_rgba(COLORS['bg_light'])

    def increment_count(self, instance):
        """增加次数"""
        if not hasattr(self, 'selected_index'):
            self.show_error('请先选择一个人名！')
            return

        try:
            current = int(self.count_input.text)
            new_count = current + 1
            self.count_input.text = str(new_count)

            name = self.unique_names[self.selected_index]
            self.name_counts[name] = new_count
            self.refresh_list()
            self.select_name(self.selected_index)
        except ValueError:
            pass

    def decrement_count(self, instance):
        """减少次数"""
        if not hasattr(self, 'selected_index'):
            self.show_error('请先选择一个人名！')
            return

        try:
            current = int(self.count_input.text)
            if current > 0:
                new_count = current - 1
                self.count_input.text = str(new_count)

                name = self.unique_names[self.selected_index]
                self.name_counts[name] = new_count
                self.refresh_list()
                self.select_name(self.selected_index)
        except ValueError:
            pass

    def confirm_change(self, instance):
        """确认修改"""
        if not hasattr(self, 'selected_index'):
            self.show_error('请先选择一个人名！')
            return

        try:
            new_count = int(self.count_input.text)
            if new_count < 0:
                self.show_error('次数不能为负数！')
                return

            name = self.unique_names[self.selected_index]
            self.name_counts[name] = new_count
            self.refresh_list()
            self.select_name(self.selected_index)
            self.show_success(f'已更新 "{name}" 的出现次数为 {new_count}')
        except ValueError:
            self.show_error('请输入有效的数字！')

    def reset_counts(self, instance):
        """恢复默认（所有人为1次）"""
        for name in self.unique_names:
            self.name_counts[name] = 1
        self.refresh_list()
        if hasattr(self, 'selected_index'):
            self.select_name(self.selected_index)
        self.show_success('已恢复默认设置！')

    def generate_rollcall(self, instance):
        """生成点名器"""
        if not self.unique_names:
            self.show_error('没有人名数据！')
            return

        # 检查是否所有次数都为0
        total = sum(self.name_counts.values())
        if total == 0:
            self.show_error('至少要有一个人名的出现次数大于0！')
            return

        # 生成扩展的人名列表（根据次数）
        expanded_names = []
        for name in self.unique_names:
            count = self.name_counts.get(name, 1)
            expanded_names.extend([name] * count)

        # 存储数据并跳转到命名界面
        app = self.manager.parent
        app.expanded_names = expanded_names
        app.unique_names = self.unique_names.copy()
        app.name_counts = self.name_counts.copy()
        app.allow_repeat = self.repeat_checkbox.active

        self.manager.current = 'name'

    def go_back(self, instance):
        """返回"""
        self.manager.current = 'main'

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
            size_hint=(0.7, 0.25),
            auto_dismiss=False
        )
        btn.bind(on_press=popup.dismiss)
        popup.open()

    def show_success(self, message):
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
            size_hint=(0.7, 0.25),
            auto_dismiss=False
        )
        btn.bind(on_press=popup.dismiss)
        popup.open()
