#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
编辑界面 - 编辑已有点名器
复刻原版桌面版的编辑功能
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
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.checkbox import CheckBox
from kivy.graphics import Color, Rectangle, Line
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.metrics import dp, sp
from kivy.properties import ListProperty, StringProperty, NumericProperty, BooleanProperty
from kivy.app import App

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import hex_to_rgba, COLORS


class EditScreen(Screen):
    """编辑点名器界面"""

    rollcall_id = StringProperty('')
    rollcall_data = dict()
    names_list = ListProperty([])
    name_counts = ListProperty([])
    selected_index = NumericProperty(-1)

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
            text='✏️ 编辑点名器',
            font_size=sp(24),
            font_name='SimHei',
            bold=True,
            color=hex_to_rgba(COLORS['accent_red']),
            pos_hint={'center_x': 0.5, 'center_y': 0.95}
        )
        layout.add_widget(title)

        # 点名器名称区域
        name_box = BoxLayout(
            orientation='horizontal',
            size_hint=(0.9, None),
            height=dp(50),
            pos_hint={'center_x': 0.5, 'center_y': 0.88}
        )

        lbl_name = Label(
            text='名称：',
            font_size=sp(16),
            font_name='SimHei',
            color=hex_to_rgba(COLORS['text_light']),
            size_hint_x=0.2
        )
        name_box.add_widget(lbl_name)

        self.name_input = TextInput(
            font_size=sp(16),
            font_name='SimHei',
            background_color=hex_to_rgba(COLORS['bg_light']),
            foreground_color=hex_to_rgba(COLORS['text_light']),
            cursor_color=hex_to_rgba(COLORS['accent_green']),
            size_hint_x=0.8,
            multiline=False
        )
        name_box.add_widget(self.name_input)

        layout.add_widget(name_box)

        # 主内容区域 - 左右分栏
        content = BoxLayout(
            orientation='horizontal',
            size_hint=(0.95, 0.65),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        # 左侧 - 人名列表
        left_box = BoxLayout(
            orientation='vertical',
            size_hint_x=0.6,
            padding=dp(5)
        )

        lbl_list = Label(
            text='📋 人名列表',
            font_size=sp(18),
            font_name='SimHei',
            bold=True,
            color=hex_to_rgba(COLORS['accent_red']),
            size_hint_y=None,
            height=dp(30)
        )
        left_box.add_widget(lbl_list)

        # 人名列表 - 使用ScrollView
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
        left_box.add_widget(scroll_list)

        content.add_widget(left_box)

        # 右侧 - 控制面板
        right_box = BoxLayout(
            orientation='vertical',
            size_hint_x=0.4,
            spacing=dp(15),
            padding=dp(10)
        )

        lbl_control = Label(
            text='⚙️ 控制面板',
            font_size=sp(18),
            font_name='SimHei',
            bold=True,
            color=hex_to_rgba(COLORS['accent_red']),
            size_hint_y=None,
            height=dp(30)
        )
        right_box.add_widget(lbl_control)

        # 选中的人名显示
        lbl_selected = Label(
            text='选中的人名：',
            font_size=sp(14),
            font_name='SimHei',
            color=hex_to_rgba(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(25)
        )
        right_box.add_widget(lbl_selected)

        self.selected_name_label = Label(
            text='请选择一个人名',
            font_size=sp(16),
            font_name='SimHei',
            bold=True,
            color=hex_to_rgba(COLORS['accent_green']),
            size_hint_y=None,
            height=dp(40)
        )
        right_box.add_widget(self.selected_name_label)

        # 出现次数
        lbl_count = Label(
            text='出现次数：',
            font_size=sp(14),
            font_name='SimHei',
            color=hex_to_rgba(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(25)
        )
        right_box.add_widget(lbl_count)

        # 次数输入和操作按钮
        count_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(5)
        )

        btn_minus = Button(
            text='➖',
            font_size=sp(20),
            background_color=hex_to_rgba(COLORS['accent_red']),
            size_hint_x=0.25
        )
        btn_minus.bind(on_press=self.decrease_count)
        count_box.add_widget(btn_minus)

        self.count_input = TextInput(
            text='0',
            font_size=sp(20),
            font_name='SimHei',
            background_color=hex_to_rgba(COLORS['bg_light']),
            foreground_color=hex_to_rgba(COLORS['text_light']),
            cursor_color=hex_to_rgba(COLORS['accent_green']),
            halign='center',
            size_hint_x=0.5,
            multiline=False
        )
        count_box.add_widget(self.count_input)

        btn_plus = Button(
            text='➕',
            font_size=sp(20),
            background_color=hex_to_rgba(COLORS['accent_green']),
            size_hint_x=0.25
        )
        btn_plus.bind(on_press=self.increase_count)
        count_box.add_widget(btn_plus)

        right_box.add_widget(count_box)

        # 操作按钮
        btn_confirm = Button(
            text='✅ 确定修改',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_green']),
            color=hex_to_rgba(COLORS['bg_dark']),
            size_hint_y=None,
            height=dp(45)
        )
        btn_confirm.bind(on_press=self.confirm_change)
        right_box.add_widget(btn_confirm)

        btn_delete = Button(
            text='🗑️ 删除人名',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_red']),
            color=hex_to_rgba(COLORS['white']),
            size_hint_y=None,
            height=dp(45)
        )
        btn_delete.bind(on_press=self.delete_name)
        right_box.add_widget(btn_delete)

        # 添加人名区域
        add_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(100),
            spacing=dp(5)
        )

        lbl_add = Label(
            text='添加人名：',
            font_size=sp(14),
            font_name='SimHei',
            color=hex_to_rgba(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(25)
        )
        add_box.add_widget(lbl_add)

        self.add_input = TextInput(
            font_size=sp(14),
            font_name='SimHei',
            background_color=hex_to_rgba(COLORS['bg_light']),
            foreground_color=hex_to_rgba(COLORS['text_light']),
            cursor_color=hex_to_rgba(COLORS['accent_green']),
            hint_text='输入人名',
            size_hint_y=None,
            height=dp(40),
            multiline=False
        )
        add_box.add_widget(self.add_input)

        btn_add = Button(
            text='➕ 添加',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_blue']),
            color=hex_to_rgba(COLORS['bg_dark']),
            size_hint_y=None,
            height=dp(40)
        )
        btn_add.bind(on_press=self.add_name)
        add_box.add_widget(btn_add)

        right_box.add_widget(add_box)

        # 可重复点名选项
        repeat_box = BoxLayout(
            spacing=dp(5),
            size_hint_y=None,
            height=dp(35)
        )

        self.repeat_checkbox = CheckBox(
            size_hint_x=None,
            width=dp(30),
            color=hex_to_rgba(COLORS['accent_blue'])
        )

        lbl_repeat = Label(
            text='🔄 可重复点名',
            font_size=sp(14),
            font_name='SimHei',
            color=hex_to_rgba(COLORS['accent_blue'])
        )

        repeat_box.add_widget(self.repeat_checkbox)
        repeat_box.add_widget(lbl_repeat)
        right_box.add_widget(repeat_box)

        # 空白填充
        right_box.add_widget(Widget())

        content.add_widget(right_box)

        layout.add_widget(content)

        # 底部按钮
        btn_box = BoxLayout(
            orientation='horizontal',
            size_hint=(0.9, None),
            height=dp(50),
            spacing=dp(20),
            pos_hint={'center_x': 0.5, 'y': 0.05}
        )

        btn_save = Button(
            text='💾 保存修改',
            font_size=sp(16),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_green']),
            color=hex_to_rgba(COLORS['bg_dark']),
            size_hint_x=0.5
        )
        btn_save.bind(on_press=self.save_changes)
        btn_box.add_widget(btn_save)

        btn_cancel = Button(
            text='↩ 返回',
            font_size=sp(16),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_red']),
            color=hex_to_rgba(COLORS['white']),
            size_hint_x=0.5
        )
        btn_cancel.bind(on_press=self.go_back)
        btn_box.add_widget(btn_cancel)

        layout.add_widget(btn_box)

        self.add_widget(layout)

    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def get_data_dir(self):
        """获取数据目录 - 与ListScreen/NameScreen保持一致"""
        if os.path.exists('/sdcard'):
            data_dir = '/sdcard/RollCall'
        else:
            data_dir = os.path.join(os.path.expanduser('~'), '.rollcall')

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        return data_dir

    def on_enter(self):
        """进入界面时加载数据"""
        app = App.get_running_app()
        if app.editing_rollcall_data:
            self.rollcall_data = app.editing_rollcall_data
            self.load_data()

    def load_data(self):
        """加载点名器数据"""
        # 设置名称
        self.name_input.text = self.rollcall_data.get('name', '')

        # 加载人名和次数
        names = self.rollcall_data.get('names', [])
        counts = self.rollcall_data.get('name_counts', [])

        # 如果没有人名次数，默认为1
        if not counts:
            counts = [1] * len(names)

        self.names_list = names
        self.name_counts = counts

        # 加载可重复点名状态
        self.repeat_checkbox.active = self.rollcall_data.get('allow_repeat', False)

        # 更新列表显示
        self.update_names_list()

    def update_names_list(self):
        """更新人名列表显示 - 合并相同人名"""
        from collections import Counter
        self.names_layout.clear_widgets()

        # 统计每个人名的出现次数
        counter = Counter(self.names_list)
        # 按首次出现顺序排列
        seen = set()
        ordered = []
        for name in self.names_list:
            if name not in seen:
                seen.add(name)
                ordered.append(name)

        # 保存合并后的数据供选中/修改使用
        self._merged_names = ordered
        self._merged_counts = [counter[n] for n in ordered]

        for i, name in enumerate(ordered):
            count = counter[name]
            btn = Button(
                text=f'{i+1}. {name} (出现{count}次)',
                font_size=sp(14),
                font_name='SimHei',
                background_color=hex_to_rgba(COLORS['bg_light']),
                color=hex_to_rgba(COLORS['text_light']),
                size_hint_y=None,
                height=dp(40)
            )
            btn.bind(on_press=lambda x, idx=i: self.select_name(idx))
            self.names_layout.add_widget(btn)

    def select_name(self, index):
        """选择人名"""
        self.selected_index = index
        name = self._merged_names[index]
        count = self._merged_counts[index]

        self.selected_name_label.text = name
        self.count_input.text = str(count)

    def increase_count(self, instance):
        """增加次数"""
        if self.selected_index < 0:
            self.show_error('请先选择一个人名！')
            return

        try:
            current = int(self.count_input.text)
            self.count_input.text = str(current + 1)
        except:
            self.count_input.text = '1'

    def decrease_count(self, instance):
        """减少次数"""
        if self.selected_index < 0:
            self.show_error('请先选择一个人名！')
            return

        try:
            current = int(self.count_input.text)
            if current > 1:
                self.count_input.text = str(current - 1)
        except:
            self.count_input.text = '1'

    def confirm_change(self, instance):
        """确认修改次数"""
        if self.selected_index < 0:
            self.show_error('请先选择一个人名！')
            return

        try:
            new_count = int(self.count_input.text)
            if new_count < 1:
                new_count = 1

            name = self._merged_names[self.selected_index]
            # 更新展开列表：移除该人名所有出现，再添加 new_count 个
            self.names_list = [n for n in self.names_list if n != name] + [name] * new_count
            self.name_counts = [1] * len(self.names_list)
            self.update_names_list()
            self.show_success('修改成功！')
        except:
            self.show_error('请输入有效的数字！')

    def delete_name(self, instance):
        """删除人名"""
        if self.selected_index < 0:
            self.show_error('请先选择一个人名！')
            return

        name = self._merged_names[self.selected_index]

        # 显示确认对话框
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        lbl = Label(
            text=f'确定要删除 "{name}" 吗？',
            font_size=sp(14),
            font_name='SimHei',
            color=hex_to_rgba(COLORS['text_light'])
        )
        content.add_widget(lbl)

        btn_box = BoxLayout(spacing=dp(10))

        btn_yes = Button(
            text='确定',
            font_size=sp(14),
            font_name='SimHei',
            background_color=hex_to_rgba(COLORS['accent_red'])
        )

        btn_no = Button(
            text='取消',
            font_size=sp(14),
            font_name='SimHei',
            background_color=hex_to_rgba(COLORS['bg_light'])
        )

        btn_box.add_widget(btn_yes)
        btn_box.add_widget(btn_no)
        content.add_widget(btn_box)

        popup = Popup(
            title='确认删除',
            content=content,
            size_hint=(0.8, 0.25),
            auto_dismiss=False
        )

        def on_confirm(btn):
            self.names_list = [n for n in self.names_list if n != name]
            self.name_counts = [1] * len(self.names_list)
            self.selected_index = -1
            self.selected_name_label.text = '请选择一个人名'
            self.count_input.text = '0'
            self.update_names_list()
            popup.dismiss()
            self.show_success('删除成功！')

        btn_yes.bind(on_press=on_confirm)
        btn_no.bind(on_press=popup.dismiss)
        popup.open()

    def add_name(self, instance):
        """添加人名"""
        name = self.add_input.text.strip()
        if not name:
            self.show_error('请输入人名！')
            return

        self.names_list.append(name)
        self.name_counts.append(1)
        self.add_input.text = ''
        self.update_names_list()
        self.show_success('添加成功！')

    def save_changes(self, instance):
        """保存修改"""
        if not self.names_list:
            self.show_error('人名列表不能为空！')
            return

        # 更新数据
        self.rollcall_data['name'] = self.name_input.text
        self.rollcall_data['names'] = self.names_list
        self.rollcall_data['name_counts'] = self.name_counts
        self.rollcall_data['allow_repeat'] = self.repeat_checkbox.active

        # 保存到文件
        app = App.get_running_app()
        rollcall_id = app.editing_rollcall_id
        data_dir = self.get_data_dir()
        filepath = os.path.join(data_dir, f'{rollcall_id}.json')

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.rollcall_data, f, ensure_ascii=False, indent=2)

            # 更新索引文件中的名称（如果修改了名称）
            index_file = os.path.join(data_dir, 'index.json')
            if os.path.exists(index_file):
                with open(index_file, 'r', encoding='utf-8') as f:
                    index = json.load(f)

                for item in index:
                    if item['id'] == rollcall_id:
                        item['name'] = self.name_input.text
                        break

                with open(index_file, 'w', encoding='utf-8') as f:
                    json.dump(index, f, ensure_ascii=False, indent=2)

            self.show_success('保存成功！', self.go_back)
        except Exception as e:
            self.show_error(f'保存失败：{str(e)}')

    def go_back(self, instance=None):
        """返回列表界面"""
        self.manager.current = 'list'

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

    def show_success(self, message, callback=None):
        """显示成功信息"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        lbl = Label(
            text=message,
            font_size=sp(16),
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

        def on_dismiss(btn):
            popup.dismiss()
            if callback:
                callback()

        btn.bind(on_press=on_dismiss)
        popup.open()
