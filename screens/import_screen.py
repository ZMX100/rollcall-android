#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
导入文件界面 - 支持多种导入方式
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
from kivy.uix.filechooser import FileChooserListView
from kivy.graphics import Color, Rectangle, Line
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.metrics import dp, sp
from kivy.properties import StringProperty, ListProperty
from kivy.app import App

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import hex_to_rgba, COLORS
from utils import replace_emoji


class ImportScreen(Screen):
    """导入文件界面 - 支持多种导入方式"""

    imported_names = ListProperty([])

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
            text='📁 导入文件',
            font_size=sp(24),
            font_name='SimHei',
            bold=True,
            color=hex_to_rgba(COLORS['accent_red']),
            pos_hint={'center_x': 0.5, 'center_y': 0.92}
        )
        layout.add_widget(title)

        # 主内容区域 - 使用ScrollView添加滚动条
        scroll_view = ScrollView(
            size_hint=(0.8, 0.75),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            bar_width=dp(8),
            bar_color=hex_to_rgba(COLORS['accent_red']),
            bar_inactive_color=hex_to_rgba(COLORS['bg_light']),
            effect_cls='ScrollEffect',
            scroll_type=['bars', 'content']
        )

        content = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            padding=dp(10)
        )
        content.bind(minimum_height=content.setter('height'))

        # 方法1: 从Excel文件导入
        method1_box = self.create_method_box(
            '方法一',
            '从Excel文件导入 (.xlsx/.xls)',
            '选择Excel文件，自动读取第一列人名',
            '#00d9ff'
        )
        btn_file = Button(
            text='📂 选择Excel文件',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_blue']),
            color=hex_to_rgba(COLORS['bg_dark']),
            size_hint_y=None,
            height=dp(45)
        )
        btn_file.bind(on_press=self.show_file_chooser)
        method1_box.add_widget(btn_file)
        content.add_widget(method1_box)

        # 方法2: 从CSV文件导入
        method2_box = self.create_method_box(
            '方法二',
            '从CSV文件导入',
            '选择CSV格式文件导入人名',
            '#00ff88'
        )
        btn_csv = Button(
            text='📄 选择CSV文件',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_green']),
            color=hex_to_rgba(COLORS['bg_dark']),
            size_hint_y=None,
            height=dp(45)
        )
        btn_csv.bind(on_press=self.show_csv_chooser)
        method2_box.add_widget(btn_csv)
        content.add_widget(method2_box)

        # 方法3: 从文本文件导入
        method3_box = self.create_method_box(
            '方法三',
            '从文本文件导入 (.txt)',
            '每行一个人名，自动解析',
            '#ffd700'
        )
        btn_txt = Button(
            text='📝 选择文本文件',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_yellow']),
            color=hex_to_rgba(COLORS['bg_dark']),
            size_hint_y=None,
            height=dp(45)
        )
        btn_txt.bind(on_press=self.show_txt_chooser)
        method3_box.add_widget(btn_txt)
        content.add_widget(method3_box)

        # 方法4: 粘贴文本导入
        method4_box = self.create_method_box(
            '方法四',
            '粘贴文本导入',
            '直接粘贴人名列表，用逗号或换行分隔',
            '#9b59b6'
        )
        btn_paste = Button(
            text='📋 粘贴文本',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_purple']),
            color=hex_to_rgba(COLORS['white']),
            size_hint_y=None,
            height=dp(45)
        )
        btn_paste.bind(on_press=self.show_paste_dialog)
        method4_box.add_widget(btn_paste)
        content.add_widget(method4_box)

        # 方法5: 从已有点名器导入
        method5_box = self.create_method_box(
            '方法五',
            '从已有点名器导入',
            '选择之前创建的点名器导入人名',
            '#e94560'
        )
        btn_existing = Button(
            text='📋 选择已有点名器',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_red']),
            color=hex_to_rgba(COLORS['white']),
            size_hint_y=None,
            height=dp(45)
        )
        btn_existing.bind(on_press=self.show_existing_rollcall)
        method5_box.add_widget(btn_existing)
        content.add_widget(method5_box)

        scroll_view.add_widget(content)
        layout.add_widget(scroll_view)

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
            pos_hint={'center_x': 0.5, 'y': 0.05}
        )
        btn_back.bind(on_press=self.go_back)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def create_method_box(self, method_num, title, desc, color_hex):
        """创建方法说明框"""
        box = BoxLayout(
            orientation='vertical',
            spacing=dp(6),
            size_hint_y=None,
            height=dp(120),
            padding=[dp(10), dp(5), dp(10), dp(8)]
        )

        with box.canvas.before:
            Color(*hex_to_rgba(color_hex, 0.3))
            Rectangle(pos=box.pos, size=box.size)
            Color(*hex_to_rgba(color_hex))
            Line(rectangle=(box.x, box.y, box.width, box.height), width=dp(2))

        box.bind(pos=self.update_box_bg, size=self.update_box_bg)
        box.color_hex = color_hex

        lbl_num = Label(
            text=method_num,
            font_size=sp(12),
            font_name='SimHei',
            color=hex_to_rgba(color_hex),
            size_hint_y=None,
            height=dp(20),
            halign='left'
        )
        lbl_num.bind(size=lbl_num.setter('text_size'))
        box.add_widget(lbl_num)

        lbl_title = Label(
            text=title,
            font_size=sp(16),
            font_name='SimHei',
            bold=True,
            color=hex_to_rgba(COLORS['text_light']),
            size_hint_y=None,
            height=dp(25),
            halign='left'
        )
        lbl_title.bind(size=lbl_title.setter('text_size'))
        box.add_widget(lbl_title)

        lbl_desc = Label(
            text=desc,
            font_size=sp(12),
            font_name='SimHei',
            color=hex_to_rgba(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(20),
            halign='left'
        )
        lbl_desc.bind(size=lbl_desc.setter('text_size'))
        box.add_widget(lbl_desc)

        return box

    def update_box_bg(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*hex_to_rgba(instance.color_hex, 0.3))
            Rectangle(pos=instance.pos, size=instance.size)
            Color(*hex_to_rgba(instance.color_hex))
            Line(rectangle=(instance.x, instance.y, instance.width, instance.height), width=dp(2))

    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def show_file_chooser(self, instance):
        """显示Excel文件选择器"""
        content = BoxLayout(orientation='vertical', spacing=dp(10))

        filechooser = FileChooserListView(
            path=os.path.expanduser('~'),
            filters=['*.xlsx', '*.xls'],
            size_hint_y=0.8
        )
        content.add_widget(filechooser)

        btn_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        btn_select = Button(
            text='选择',
            font_size=sp(14),
            font_name='SimHei',
            background_color=hex_to_rgba(COLORS['accent_green'])
        )

        btn_cancel = Button(
            text='取消',
            font_size=sp(14),
            font_name='SimHei',
            background_color=hex_to_rgba(COLORS['accent_red'])
        )

        btn_box.add_widget(btn_select)
        btn_box.add_widget(btn_cancel)
        content.add_widget(btn_box)

        popup = Popup(
            title='选择Excel文件',
            content=content,
            size_hint=(0.9, 0.7),
            auto_dismiss=False
        )

        def on_select(btn):
            if filechooser.selection:
                self.import_from_excel(filechooser.selection[0])
                popup.dismiss()

        btn_select.bind(on_press=on_select)
        btn_cancel.bind(on_press=popup.dismiss)
        popup.open()

    def show_csv_chooser(self, instance):
        """显示CSV文件选择器"""
        content = BoxLayout(orientation='vertical', spacing=dp(10))

        filechooser = FileChooserListView(
            path=os.path.expanduser('~'),
            filters=['*.csv'],
            size_hint_y=0.8
        )
        content.add_widget(filechooser)

        btn_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        btn_select = Button(
            text='选择',
            font_size=sp(14),
            font_name='SimHei',
            background_color=hex_to_rgba(COLORS['accent_green'])
        )

        btn_cancel = Button(
            text='取消',
            font_size=sp(14),
            font_name='SimHei',
            background_color=hex_to_rgba(COLORS['accent_red'])
        )

        btn_box.add_widget(btn_select)
        btn_box.add_widget(btn_cancel)
        content.add_widget(btn_box)

        popup = Popup(
            title='选择CSV文件',
            content=content,
            size_hint=(0.9, 0.7),
            auto_dismiss=False
        )

        def on_select(btn):
            if filechooser.selection:
                self.import_from_csv(filechooser.selection[0])
                popup.dismiss()

        btn_select.bind(on_press=on_select)
        btn_cancel.bind(on_press=popup.dismiss)
        popup.open()

    def show_txt_chooser(self, instance):
        """显示文本文件选择器"""
        content = BoxLayout(orientation='vertical', spacing=dp(10))

        filechooser = FileChooserListView(
            path=os.path.expanduser('~'),
            filters=['*.txt'],
            size_hint_y=0.8
        )
        content.add_widget(filechooser)

        btn_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        btn_select = Button(
            text='选择',
            font_size=sp(14),
            font_name='SimHei',
            background_color=hex_to_rgba(COLORS['accent_green'])
        )

        btn_cancel = Button(
            text='取消',
            font_size=sp(14),
            font_name='SimHei',
            background_color=hex_to_rgba(COLORS['accent_red'])
        )

        btn_box.add_widget(btn_select)
        btn_box.add_widget(btn_cancel)
        content.add_widget(btn_box)

        popup = Popup(
            title='选择文本文件',
            content=content,
            size_hint=(0.9, 0.7),
            auto_dismiss=False
        )

        def on_select(btn):
            if filechooser.selection:
                self.import_from_txt(filechooser.selection[0])
                popup.dismiss()

        btn_select.bind(on_press=on_select)
        btn_cancel.bind(on_press=popup.dismiss)
        popup.open()

    def show_paste_dialog(self, instance):
        """显示粘贴文本对话框"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        lbl_hint = Label(
            text='请粘贴人名列表（用逗号、空格或换行分隔）',
            font_size=sp(14),
            font_name='SimHei',
            color=hex_to_rgba(COLORS['text_light']),
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(lbl_hint)

        text_input = TextInput(
            multiline=True,
            font_size=sp(14),
            font_name='SimHei',
            background_color=hex_to_rgba(COLORS['bg_light']),
            foreground_color=hex_to_rgba(COLORS['text_light']),
            cursor_color=hex_to_rgba(COLORS['accent_green']),
            size_hint_y=0.7
        )
        content.add_widget(text_input)

        btn_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        btn_confirm = Button(
            text='确认导入',
            font_size=sp(14),
            font_name='SimHei',
            background_color=hex_to_rgba(COLORS['accent_green'])
        )

        btn_cancel = Button(
            text='取消',
            font_size=sp(14),
            font_name='SimHei',
            background_color=hex_to_rgba(COLORS['accent_red'])
        )

        btn_box.add_widget(btn_confirm)
        btn_box.add_widget(btn_cancel)
        content.add_widget(btn_box)

        popup = Popup(
            title='粘贴文本导入',
            content=content,
            size_hint=(0.9, 0.5),
            auto_dismiss=False
        )

        def on_confirm(btn):
            text = text_input.text.strip()
            if text:
                self.import_from_text(text)
                popup.dismiss()

        btn_confirm.bind(on_press=on_confirm)
        btn_cancel.bind(on_press=popup.dismiss)
        popup.open()

    def show_existing_rollcall(self, instance):
        """显示已有点名器列表"""
        # 跳转到列表界面
        self.manager.current = 'list'

    def import_from_excel(self, filepath):
        """从Excel文件导入"""
        try:
            import openpyxl
            wb = openpyxl.load_workbook(filepath)
            sheet = wb.active
            names = []
            for row in sheet.iter_rows(min_row=1, max_col=1, values_only=True):
                if row[0] and str(row[0]).strip():
                    names.append(str(row[0]).strip())
            wb.close()
            self.process_imported_names(names, f'Excel文件: {os.path.basename(filepath)}')
        except Exception as e:
            self.show_error(f'导入Excel失败: {str(e)}')

    def import_from_csv(self, filepath):
        """从CSV文件导入"""
        try:
            import csv
            names = []
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and row[0].strip():
                        names.append(row[0].strip())
            self.process_imported_names(names, f'CSV文件: {os.path.basename(filepath)}')
        except Exception as e:
            self.show_error(f'导入CSV失败: {str(e)}')

    def import_from_txt(self, filepath):
        """从文本文件导入"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            names = [name.strip() for name in content.split('\n') if name.strip()]
            self.process_imported_names(names, f'文本文件: {os.path.basename(filepath)}')
        except Exception as e:
            self.show_error(f'导入文本失败: {str(e)}')

    def import_from_text(self, text):
        """从粘贴的文本导入"""
        import re
        # 支持逗号、空格、换行分隔
        names = [name.strip() for name in re.split(r'[,，\s\n]+', text) if name.strip()]
        self.process_imported_names(names, '粘贴文本')

    def process_imported_names(self, names, source):
        """处理导入的人名"""
        if not names:
            self.show_error('未找到有效的人名！')
            return

        # 存储到App的数据中
        app = App.get_running_app()
        app.imported_names = names
        app.import_source = source

        # 显示成功信息并跳转到爆率修改界面
        self.show_success(f'成功导入 {len(names)} 个人名！', lambda: setattr(self.manager, 'current', 'rate'))

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
            size_hint=(0.7, 0.3),
            auto_dismiss=False
        )
        btn.bind(on_press=popup.dismiss)
        popup.open()

    def show_success(self, message, callback):
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
            size_hint=(0.7, 0.3),
            auto_dismiss=False
        )

        def on_dismiss(btn):
            popup.dismiss()
            callback()

        btn.bind(on_press=on_dismiss)
        popup.open()

    def go_back(self, instance):
        """返回主界面"""
        self.manager.current = 'main'
