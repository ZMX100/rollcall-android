#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手动输入界面
"""

import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, Line
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.metrics import dp, sp
from kivy.properties import ListProperty
from kivy.app import App

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import hex_to_rgba, COLORS
from utils import replace_emoji


class InputScreen(Screen):
    """手动输入界面"""

    names_list = ListProperty([])

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
            text='✏️ 手动输入人名',
            font_size=sp(24),
            font_name='SimHei',
            bold=True,
            color=hex_to_rgba(COLORS['accent_red']),
            pos_hint={'center_x': 0.5, 'center_y': 0.95}
        )
        layout.add_widget(title)

        # 主内容区域
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint=(0.9, 0.75),
            pos_hint={'center_x': 0.5, 'center_y': 0.48}
        )

        # "请输入名字："单独在方框上方
        lbl_hint = Label(
            text='请输入名字：',
            font_size=sp(14),
            font_name='SimHei',
            color=hex_to_rgba(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(20),
            halign='left'
        )
        lbl_hint.bind(size=lbl_hint.setter('text_size'))
        content.add_widget(lbl_hint)

        # 输入框区域（方框）
        input_box = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(110),
            padding=[dp(15), dp(18), dp(15), dp(10)]
        )

        with input_box.canvas.before:
            Color(*hex_to_rgba(COLORS['bg_medium']))
            self.input_bg = Rectangle(pos=input_box.pos, size=input_box.size)
            Color(*hex_to_rgba(COLORS['accent_red']))
            Line(rectangle=(input_box.x, input_box.y, input_box.width, input_box.height), width=dp(2))

        input_box.bind(pos=self.update_input_bg, size=self.update_input_bg)

        self.name_input = TextInput(
            multiline=False,
            font_size=sp(16),
            font_name='SimHei',
            background_color=hex_to_rgba(COLORS['bg_light']),
            foreground_color=hex_to_rgba(COLORS['text_light']),
            cursor_color=hex_to_rgba(COLORS['accent_green']),
            size_hint_y=None,
            height=dp(45),
            hint_text='输入人名后按回车或点击添加'
        )
        self.name_input.bind(on_text_validate=self.add_name)
        input_box.add_widget(self.name_input)

        # 按钮行
        btn_row = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(45))

        btn_add = Button(
            text='➕ 添加',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_blue']),
            color=hex_to_rgba(COLORS['bg_dark'])
        )
        btn_add.bind(on_press=self.add_name)

        btn_row.add_widget(btn_add)
        input_box.add_widget(btn_row)

        content.add_widget(input_box)

        # 已添加人名列表 - 使用滚动条显示
        list_box = BoxLayout(
            orientation='vertical',
            size_hint_y=0.5,
            padding=dp(5)
        )

        lbl_list_title = Label(
            text='📋 已添加的人名列表',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            color=hex_to_rgba(COLORS['accent_red']),
            size_hint_y=None,
            height=dp(25)
        )
        list_box.add_widget(lbl_list_title)

        # 滚动列表
        scroll_list = ScrollView(
            bar_width=dp(6),
            bar_color=hex_to_rgba(COLORS['accent_red'])
        )

        self.names_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None
        )
        self.names_layout.bind(minimum_height=self.names_layout.setter('height'))

        scroll_list.add_widget(self.names_layout)
        list_box.add_widget(scroll_list)

        content.add_widget(list_box)

        # 统计信息
        self.stats_label = Label(
            text='已添加：0 人',
            font_size=sp(14),
            font_name='SimHei',
            color=hex_to_rgba(COLORS['accent_green']),
            size_hint_y=None,
            height=dp(25)
        )
        content.add_widget(self.stats_label)

        # 快捷输入提示
        hint_box = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None,
            height=dp(80),
            padding=dp(10)
        )

        with hint_box.canvas.before:
            Color(*hex_to_rgba(COLORS['bg_light'], 0.5))
            self.hint_bg = Rectangle(pos=hint_box.pos, size=hint_box.size)

        hint_box.bind(pos=self.update_hint_bg, size=self.update_hint_bg)

        lbl_hint_title = Label(
            text='💡 快捷输入提示',
            font_size=sp(12),
            font_name='SimHei',
            bold=True,
            color=hex_to_rgba(COLORS['accent_yellow']),
            size_hint_y=None,
            height=dp(20),
            halign='left'
        )
        lbl_hint_title.bind(size=lbl_hint_title.setter('text_size'))
        hint_box.add_widget(lbl_hint_title)

        lbl_hint_text = Label(
            text='• 输入人名后按回车键快速添加\n• 可以连续输入多个人名',
            font_size=sp(11),
            font_name='SimHei',
            color=hex_to_rgba(COLORS['text_gray']),
            halign='left'
        )
        lbl_hint_text.bind(size=lbl_hint_text.setter('text_size'))
        hint_box.add_widget(lbl_hint_text)

        content.add_widget(hint_box)

        layout.add_widget(content)

        # 底部按钮
        bottom_box = BoxLayout(
            spacing=dp(15),
            size_hint=(None, None),
            size=(dp(280), dp(50)),
            pos_hint={'center_x': 0.5, 'y': 0.02}
        )

        btn_confirm = Button(
            text='✅ 确定',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_green']),
            color=hex_to_rgba(COLORS['bg_dark'])
        )
        btn_confirm.bind(on_press=self.confirm_input)

        btn_back = Button(
            text='↩ 返回',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_red']),
            color=hex_to_rgba(COLORS['white'])
        )
        btn_back.bind(on_press=self.go_back)

        bottom_box.add_widget(btn_confirm)
        bottom_box.add_widget(btn_back)
        layout.add_widget(bottom_box)

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

    def update_hint_bg(self, instance, value):
        self.hint_bg.pos = instance.pos
        self.hint_bg.size = instance.size

    def add_name(self, instance):
        """添加人名"""
        name = self.name_input.text.strip()
        if name:
            self.names_list.append(name)
            self.name_input.text = ''
            self.update_stats()
            self.update_names_list()
            self.name_input.focus = True
        else:
            self.show_error('人名不能为空！')

    def update_stats(self):
        """更新统计信息"""
        from collections import Counter
        counter = Counter(self.names_list)
        unique_count = len(counter)
        total_count = len(self.names_list)
        if unique_count != total_count:
            self.stats_label.text = f'已添加：{total_count} 人（{unique_count} 个不同人名）'
        else:
            self.stats_label.text = f'已添加：{total_count} 人'

    def update_names_list(self):
        """更新已添加人名列表显示 - 合并相同人名"""
        from collections import Counter
        self.names_layout.clear_widgets()

        counter = Counter(self.names_list)
        # 按首次出现顺序排列
        seen = set()
        ordered_names = []
        for name in self.names_list:
            if name not in seen:
                seen.add(name)
                ordered_names.append(name)

        for i, name in enumerate(ordered_names):
            count = counter[name]
            row = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(35),
                spacing=dp(5)
            )

            lbl_num = Label(
                text=f'{i+1}.',
                font_size=sp(14),
                font_name='SimHei',
                color=hex_to_rgba(COLORS['text_gray']),
                size_hint_x=None,
                width=dp(30)
            )

            display_text = f'{name} (×{count})' if count > 1 else name
            lbl_name = Button(
                text=display_text,
                font_size=sp(14),
                font_name='SimHei',
                background_color=hex_to_rgba(COLORS['bg_light']),
                color=hex_to_rgba(COLORS['text_light']),
                halign='left',
                valign='middle'
            )
            lbl_name.bind(size=lbl_name.setter('text_size'))
            if count > 1:
                lbl_name.bind(on_press=lambda x, n=name, c=count: self.edit_name_count(n, c))

            btn_delete = Button(
                text='❌',
                font_size=sp(12),
                size_hint_x=None,
                width=dp(40),
                background_color=hex_to_rgba(COLORS['accent_red'])
            )
            btn_delete.bind(on_press=lambda x, n=name: self.delete_name_by_name(n))

            row.add_widget(lbl_num)
            row.add_widget(lbl_name)
            row.add_widget(btn_delete)
            self.names_layout.add_widget(row)

    def edit_name_count(self, name, current_count):
        """修改重复人名的出现次数"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        lbl = Label(
            text=f'修改 "{name}" 的出现次数',
            font_size=sp(16),
            font_name='SimHei',
            color=hex_to_rgba(COLORS['text_light'])
        )
        content.add_widget(lbl)

        count_input = TextInput(
            text=str(current_count),
            font_size=sp(20),
            font_name='SimHei',
            background_color=hex_to_rgba(COLORS['bg_light']),
            foreground_color=hex_to_rgba(COLORS['text_light']),
            cursor_color=hex_to_rgba(COLORS['accent_green']),
            halign='center',
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            input_filter='int'
        )
        content.add_widget(count_input)

        btn_box = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(45))

        btn_confirm = Button(
            text='确定',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_green'])
        )

        btn_cancel = Button(
            text='取消',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_red'])
        )

        btn_box.add_widget(btn_confirm)
        btn_box.add_widget(btn_cancel)
        content.add_widget(btn_box)

        popup = Popup(
            title='修改出现次数',
            content=content,
            size_hint=(0.8, 0.3),
            auto_dismiss=False
        )

        def on_confirm(btn):
            try:
                new_count = int(count_input.text)
                if new_count < 1:
                    new_count = 1
                # 更新 names_list：将该人名的数量调整为 new_count
                self.names_list = [n for n in self.names_list if n != name] + [name] * new_count
                self.update_stats()
                self.update_names_list()
                popup.dismiss()
            except ValueError:
                count_input.text = str(current_count)

        btn_confirm.bind(on_press=on_confirm)
        btn_cancel.bind(on_press=popup.dismiss)
        popup.open()

    def delete_name_by_name(self, name):
        """删除指定人名的所有出现"""
        self.names_list = [n for n in self.names_list if n != name]
        self.update_stats()
        self.update_names_list()

    def confirm_input(self, instance):
        """确认输入"""
        if not self.names_list:
            self.show_error('请至少添加一个人名！')
            return

        # 存储到App的数据中
        app = App.get_running_app()
        app.imported_names = self.names_list.copy()
        app.import_source = '手动输入'

        # 跳转到爆率修改界面
        self.manager.current = 'rate'

    def go_back(self, instance):
        """返回主界面"""
        if self.names_list:
            # 有数据时提示
            self.show_confirm_back()
        else:
            self.names_list = []
            self.manager.current = 'main'

    def show_confirm_back(self):
        """显示确认返回对话框"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        lbl = Label(
            text='您正在进行退出操作，\n我们将不会保存您的进度',
            font_size=sp(14),
            font_name='SimHei',
            color=hex_to_rgba(COLORS['text_light'])
        )
        content.add_widget(lbl)

        btn_box = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(50))

        btn_exit = Button(
            text='❌ 仍要退出',
            font_size=sp(14),
            font_name='SimHei',
            background_color=hex_to_rgba(COLORS['accent_red'])
        )

        btn_cancel = Button(
            text='✅ 取消',
            font_size=sp(14),
            font_name='SimHei',
            background_color=hex_to_rgba(COLORS['accent_green'])
        )

        btn_box.add_widget(btn_exit)
        btn_box.add_widget(btn_cancel)
        content.add_widget(btn_box)

        popup = Popup(
            title='提示',
            content=content,
            size_hint=(0.8, 0.3),
            auto_dismiss=False
        )

        def on_exit(btn):
            self.names_list = []
            popup.dismiss()
            self.manager.current = 'main'

        btn_exit.bind(on_press=on_exit)
        btn_cancel.bind(on_press=popup.dismiss)
        popup.open()

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

    def on_enter(self):
        """进入界面时重置"""
        self.names_list = []
        self.name_input.text = ''
        self.update_stats()
