#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
已有点名器列表界面
"""

import os
import json
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.metrics import dp, sp
from kivy.properties import ListProperty, DictProperty

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import hex_to_rgba, COLORS
from utils import replace_emoji


class ListScreen(Screen):
    """已有点名器列表界面"""

    rollcall_list = ListProperty([])
    rollcall_data = DictProperty({})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_dir = self.get_data_dir()
        self.build_ui()

    def get_data_dir(self):
        """获取数据目录"""
        # Android存储路径
        if os.path.exists('/sdcard'):
            data_dir = '/sdcard/RollCall'
        else:
            data_dir = os.path.join(os.path.expanduser('~'), '.rollcall')

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # 确保索引文件存在
        index_file = os.path.join(data_dir, 'index.json')
        if not os.path.exists(index_file):
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump([], f)

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
            text='✨ 已有点名器 ✨',
            font_size=sp(24),
            font_name='SimHei',
            bold=True,
            color=hex_to_rgba(COLORS['accent_red']),
            pos_hint={'center_x': 0.5, 'center_y': 0.92}
        )
        layout.add_widget(title)

        # 列表区域
        list_container = BoxLayout(
            orientation='vertical',
            size_hint=(0.95, 0.7),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        with list_container.canvas.before:
            Color(*hex_to_rgba(COLORS['bg_medium']))
            self.list_bg = Rectangle(pos=list_container.pos, size=list_container.size)
            Color(*hex_to_rgba(COLORS['accent_red']))
            Line(rectangle=(list_container.x, list_container.y, list_container.width, list_container.height), width=dp(2))

        list_container.bind(pos=self.update_list_bg, size=self.update_list_bg)

        # 列表标题
        header = BoxLayout(size_hint_y=None, height=dp(40), padding=dp(5))

        lbl_name = Label(
            text='点名器名称',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            color=hex_to_rgba(COLORS['accent_yellow']),
            size_hint_x=0.4
        )

        lbl_count = Label(
            text='人数',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            color=hex_to_rgba(COLORS['accent_yellow']),
            size_hint_x=0.15
        )

        lbl_repeat = Label(
            text='可重复',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            color=hex_to_rgba(COLORS['accent_yellow']),
            size_hint_x=0.15
        )

        lbl_action = Label(
            text='操作',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            color=hex_to_rgba(COLORS['accent_yellow']),
            size_hint_x=0.3
        )

        header.add_widget(lbl_name)
        header.add_widget(lbl_count)
        header.add_widget(lbl_repeat)
        header.add_widget(lbl_action)
        list_container.add_widget(header)

        # 分隔线
        sep = Widget(size_hint_y=None, height=dp(2))
        with sep.canvas:
            Color(*hex_to_rgba(COLORS['accent_red']))
            Rectangle(pos=sep.pos, size=sep.size)
        sep.bind(pos=self.update_sep, size=self.update_sep)
        list_container.add_widget(sep)

        # 滚动列表
        self.scroll = ScrollView()
        self.list_layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None, padding=dp(5))
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        self.scroll.add_widget(self.list_layout)
        list_container.add_widget(self.scroll)

        layout.add_widget(list_container)

        # 返回按钮
        btn_back = Button(
            text='↩ 返回',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_blue']),
            color=hex_to_rgba(COLORS['white']),
            size_hint=(None, None),
            size=(dp(120), dp(45)),
            pos_hint={'center_x': 0.5, 'y': 0.05}
        )
        btn_back.bind(on_press=self.go_back)
        layout.add_widget(btn_back)

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

    def update_sep(self, instance, value):
        instance.canvas.clear()
        with instance.canvas:
            Color(*hex_to_rgba(COLORS['accent_red']))
            Rectangle(pos=instance.pos, size=instance.size)

    def on_enter(self):
        """进入界面时加载数据"""
        self.load_rollcall_list()

    def load_rollcall_list(self):
        """加载点名器列表"""
        self.rollcall_list = []
        self.rollcall_data = {}

        try:
            index_file = os.path.join(self.data_dir, 'index.json')
            with open(index_file, 'r', encoding='utf-8') as f:
                self.rollcall_list = json.load(f)

            # 加载每个点名器的数据
            for item in self.rollcall_list:
                data_file = os.path.join(self.data_dir, f"{item['id']}.json")
                if os.path.exists(data_file):
                    with open(data_file, 'r', encoding='utf-8') as f:
                        self.rollcall_data[item['id']] = json.load(f)

        except Exception as e:
            print(f'加载点名器列表失败: {e}')

        self.refresh_list()

    def refresh_list(self):
        """刷新列表显示"""
        self.list_layout.clear_widgets()

        if not self.rollcall_list:
            # 显示空状态
            empty_label = Label(
                text='📝 您还没有点名器！\n\n请先创建一个新的点名器',
                font_size=sp(16),
                font_name='SimHei',
                color=hex_to_rgba(COLORS['text_gray']),
                size_hint_y=None,
                height=dp(150)
            )
            self.list_layout.add_widget(empty_label)
            return

        for item in self.rollcall_list:
            row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))

            data = self.rollcall_data.get(item['id'], {})
            names = data.get('names', [])
            allow_repeat = data.get('allow_repeat', False)

            # 名称
            lbl_name = Label(
                text=item['name'],
                font_size=sp(14),
                font_name='SimHei',
                color=hex_to_rgba(COLORS['text_light']),
                size_hint_x=0.4,
                halign='left'
            )
            lbl_name.bind(size=lbl_name.setter('text_size'))
            row.add_widget(lbl_name)

            # 人数
            lbl_count = Label(
                text=str(len(names)),
                font_size=sp(14),
                font_name='SimHei',
                color=hex_to_rgba(COLORS['accent_green']),
                size_hint_x=0.15
            )
            row.add_widget(lbl_count)

            # 可重复
            lbl_repeat = Label(
                text='🔄' if allow_repeat else '🚫',
                font_size=sp(16),
                color=hex_to_rgba(COLORS['accent_blue'] if allow_repeat else COLORS['text_gray']),
                size_hint_x=0.15
            )
            row.add_widget(lbl_repeat)

            # 操作按钮
            action_box = BoxLayout(spacing=dp(3), size_hint_x=0.3)

            btn_run = Button(
                text='▶',
                font_size=sp(12),
                background_color=hex_to_rgba(COLORS['accent_green']),
                size_hint_x=0.33
            )
            btn_run.bind(on_press=lambda x, id=item['id']: self.run_rollcall(id))

            btn_edit = Button(
                text='✏️',
                font_size=sp(12),
                background_color=hex_to_rgba(COLORS['accent_yellow']),
                size_hint_x=0.33
            )
            btn_edit.bind(on_press=lambda x, id=item['id']: self.edit_rollcall(id))

            btn_delete = Button(
                text='🗑️',
                font_size=sp(12),
                background_color=hex_to_rgba(COLORS['accent_red']),
                size_hint_x=0.33
            )
            btn_delete.bind(on_press=lambda x, id=item['id']: self.delete_rollcall(id))

            action_box.add_widget(btn_run)
            action_box.add_widget(btn_edit)
            action_box.add_widget(btn_delete)
            row.add_widget(action_box)

            self.list_layout.add_widget(row)

    def run_rollcall(self, rollcall_id):
        """运行点名器"""
        data = self.rollcall_data.get(rollcall_id, {})
        if not data:
            self.show_error('点名器数据不存在！')
            return

        # 设置当前点名器数据
        app = self.manager.parent
        app.current_rollcall_names = data.get('names', [])
        app.current_rollcall_title = data.get('name', '点名器')
        app.current_allow_repeat = data.get('allow_repeat', False)

        # 跳转到点名界面
        self.manager.current = 'rollcall'

    def edit_rollcall(self, rollcall_id):
        """编辑点名器"""
        data = self.rollcall_data.get(rollcall_id, {})
        if not data:
            self.show_error('点名器数据不存在！')
            return

        # 设置编辑数据
        app = self.manager.parent
        app.editing_rollcall_id = rollcall_id
        app.editing_rollcall_data = data

        # 跳转到编辑界面
        self.manager.current = 'edit'

    def delete_rollcall(self, rollcall_id):
        """删除点名器"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        lbl = Label(
            text='确定要删除这个点名器吗？\n此操作不可恢复！',
            font_size=sp(14),
            font_name='SimHei',
            color=hex_to_rgba(COLORS['text_light'])
        )
        content.add_widget(lbl)

        btn_box = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(50))

        btn_yes = Button(
            text='删除',
            font_size=sp(14),
            font_name='SimHei',
            background_color=hex_to_rgba(COLORS['accent_red'])
        )

        btn_no = Button(
            text='取消',
            font_size=sp(14),
            font_name='SimHei',
            background_color=hex_to_rgba(COLORS['accent_blue'])
        )

        btn_box.add_widget(btn_yes)
        btn_box.add_widget(btn_no)
        content.add_widget(btn_box)

        popup = Popup(
            title='确认删除',
            content=content,
            size_hint=(0.8, 0.3),
            auto_dismiss=False
        )

        def on_yes(btn):
            self.do_delete(rollcall_id)
            popup.dismiss()

        btn_yes.bind(on_press=on_yes)
        btn_no.bind(on_press=popup.dismiss)
        popup.open()

    def do_delete(self, rollcall_id):
        """执行删除"""
        try:
            # 删除数据文件
            data_file = os.path.join(self.data_dir, f"{rollcall_id}.json")
            if os.path.exists(data_file):
                os.remove(data_file)

            # 更新索引
            self.rollcall_list = [item for item in self.rollcall_list if item['id'] != rollcall_id]

            index_file = os.path.join(self.data_dir, 'index.json')
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(self.rollcall_list, f, ensure_ascii=False, indent=2)

            # 刷新列表
            self.load_rollcall_list()
            self.show_success('删除成功！')

        except Exception as e:
            self.show_error(f'删除失败: {str(e)}')

    def go_back(self, instance):
        """返回主界面"""
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
