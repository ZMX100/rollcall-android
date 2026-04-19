#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
点名界面 - 与原版桌面版一模一样
复刻所有视觉效果和动画
"""

import os
import random
import math
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.utils import get_color_from_hex
from kivy.metrics import dp, sp
from kivy.properties import ListProperty, StringProperty, BooleanProperty, NumericProperty

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import hex_to_rgba, COLORS
from utils import replace_emoji


class Particle:
    """粒子类"""
    def __init__(self, x, y, canvas):
        self.x = x
        self.y = y
        self.canvas = canvas
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(8, 18)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = random.choice([
            COLORS['accent_red'],
            COLORS['accent_green'],
            COLORS['accent_yellow'],
            COLORS['accent_blue'],
            '#ff6b6b', '#ff9ff3', '#ffeaa7'
        ])
        self.size = random.randint(3, 10)
        self.life = 1.0
        self.graphics = None

    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.vy -= 0.3  # 重力
        self.life -= 0.015
        return self.life > 0


class Star:
    """星星装饰类"""
    def __init__(self, x, y, size, canvas):
        self.x = x
        self.y = y
        self.size = size
        self.canvas = canvas
        self.graphics = None
        self.twinkle_timer = random.random() * 2

    def update(self, dt):
        self.twinkle_timer += dt
        return True


class RollCallScreen(Screen):
    """点名界面 - 复刻原版效果"""

    names = ListProperty([])
    rollcall_name = StringProperty('')
    allow_repeat = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.picked_names = []
        self.animation_running = False
        self.particles = []
        self.stars = []
        self.list_window = None
        self.build_ui()
        Clock.schedule_interval(self.animate_stars, 0.1)

    def build_ui(self):
        """构建UI - 完全复刻原版布局"""
        self.main_layout = FloatLayout()

        # 背景画布 - 用于绘制装饰
        self.decor_canvas = Widget()
        self.main_layout.add_widget(self.decor_canvas)

        # 绘制背景
        with self.decor_canvas.canvas:
            Color(*hex_to_rgba(COLORS['bg_dark']))
            self.bg_rect = Rectangle(pos=(0, 0), size=Window.size)

        # 绑定窗口大小变化
        Window.bind(on_resize=self.on_window_resize)
        self.decor_canvas.bind(pos=self.update_decor, size=self.update_decor)

        # 绘制星星装饰
        self.draw_stars()

        # 绘制边角装饰
        self.draw_corner_decorations()

        # 主框架 - 使用AnchorLayout居中
        anchor = AnchorLayout(anchor_x='center', anchor_y='center')

        # 外层框架
        self.outer_frame = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(20),
            size_hint=(0.95, 0.85)
        )

        with self.outer_frame.canvas.before:
            Color(*hex_to_rgba(COLORS['bg_medium']))
            self.outer_bg = Rectangle(pos=self.outer_frame.pos, size=self.outer_frame.size)
            Color(*hex_to_rgba(COLORS['accent_red'], 0.5))
            Line(rectangle=(self.outer_frame.x, self.outer_frame.y,
                           self.outer_frame.width, self.outer_frame.height), width=dp(3))

        self.outer_frame.bind(pos=self.update_outer, size=self.update_outer)

        # 内层框架
        inner_frame = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(15)
        )

        with inner_frame.canvas.before:
            Color(*hex_to_rgba(COLORS['bg_light']))
            self.inner_bg = Rectangle(pos=inner_frame.pos, size=inner_frame.size)
            Color(*hex_to_rgba(COLORS['accent_blue'], 0.3))
            Line(rectangle=(inner_frame.x, inner_frame.y,
                           inner_frame.width, inner_frame.height), width=dp(2))

        inner_frame.bind(pos=self.update_inner, size=self.update_inner)

        # 标题区域
        title_box = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            spacing=dp(10)
        )

        # 左侧星星
        star_left = Label(
            text='⭐',
            font_size=sp(28),
            color=hex_to_rgba(COLORS['accent_yellow']),
            size_hint_x=None,
            width=dp(50)
        )
        title_box.add_widget(star_left)

        # 标题
        self.title_label = Label(
            text=f'✨ {self.rollcall_name or "幸运点名器"} ✨',
            font_size=sp(28),
            font_name='SimHei',
            bold=True,
            color=hex_to_rgba(COLORS['accent_red'])
        )
        title_box.add_widget(self.title_label)

        # 右侧星星
        star_right = Label(
            text='⭐',
            font_size=sp(28),
            color=hex_to_rgba(COLORS['accent_yellow']),
            size_hint_x=None,
            width=dp(50)
        )
        title_box.add_widget(star_right)

        inner_frame.add_widget(title_box)

        # 分隔线1
        sep1 = Widget(size_hint_y=None, height=dp(3))
        with sep1.canvas:
            Color(*hex_to_rgba(COLORS['accent_red']))
            Rectangle(pos=sep1.pos, size=sep1.size)
        sep1.bind(pos=self.update_sep1, size=self.update_sep1)
        inner_frame.add_widget(sep1)

        # 显示区域 - 最重要的部分
        display_frame = AnchorLayout(
            anchor_x='center',
            anchor_y='center',
            size_hint_y=0.4
        )

        with display_frame.canvas.before:
            Color(*hex_to_rgba(COLORS['bg_light']))
            self.display_bg = Rectangle(pos=display_frame.pos, size=display_frame.size)
            Color(*hex_to_rgba(COLORS['accent_red'], 0.5))
            Line(rectangle=(display_frame.x, display_frame.y,
                           display_frame.width, display_frame.height), width=dp(4))

        display_frame.bind(pos=self.update_display, size=self.update_display)

        # 名字显示标签
        self.name_display = Label(
            text='准备就绪',
            font_size=sp(50),
            font_name='SimHei',
            bold=True,
            color=hex_to_rgba(COLORS['accent_green'])
        )

        # 内边框装饰
        with self.name_display.canvas.before:
            Color(*hex_to_rgba(COLORS['bg_medium']))
            self.name_bg = Rectangle(pos=self.name_display.pos, size=self.name_display.size)

        self.name_display.bind(pos=self.update_name_bg, size=self.update_name_bg)

        display_frame.add_widget(self.name_display)
        inner_frame.add_widget(display_frame)

        # 分隔线2
        sep2 = Widget(size_hint_y=None, height=dp(3))
        with sep2.canvas:
            Color(*hex_to_rgba(COLORS['accent_red']))
            Rectangle(pos=sep2.pos, size=sep2.size)
        sep2.bind(pos=self.update_sep2, size=self.update_sep2)
        inner_frame.add_widget(sep2)

        # 按钮区域 - 使用2列布局适应竖屏
        button_box = GridLayout(
            cols=2,
            spacing=dp(8),
            size_hint_y=None,
            height=dp(180),
            padding=dp(5)
        )

        # 开始点名按钮 - 最大最显眼
        self.roll_button = Button(
            text='🎯\n开始点名',
            font_size=sp(20),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_red']),
            color=hex_to_rgba(COLORS['white'])
        )
        self.roll_button.bind(on_press=self.roll_name)
        button_box.add_widget(self.roll_button)

        # 重置按钮
        if not self.allow_repeat:
            self.reset_button = Button(
                text='🔄\n重置',
                font_size=sp(14),
                font_name='SimHei',
                bold=True,
                background_color=hex_to_rgba(COLORS['text_gray']),
                color=hex_to_rgba(COLORS['white'])
            )
            self.reset_button.bind(on_press=self.reset_display)
            button_box.add_widget(self.reset_button)

        # 名单按钮
        self.list_button = Button(
            text='📋\n名单',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_yellow']),
            color=hex_to_rgba(COLORS['bg_dark'])
        )
        self.list_button.bind(on_press=self.show_name_list)
        button_box.add_widget(self.list_button)

        # 全屏按钮
        self.fullscreen_button = Button(
            text='⛶\n全屏',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba(COLORS['accent_blue']),
            color=hex_to_rgba(COLORS['bg_dark'])
        )
        self.fullscreen_button.bind(on_press=self.toggle_fullscreen)
        button_box.add_widget(self.fullscreen_button)

        # 退出按钮
        self.exit_button = Button(
            text='❌\n退出',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba('#e74c3c'),
            color=hex_to_rgba(COLORS['white'])
        )
        self.exit_button.bind(on_press=self.exit_app)
        button_box.add_widget(self.exit_button)

        # 返回按钮
        self.back_button = Button(
            text='↩\n返回',
            font_size=sp(14),
            font_name='SimHei',
            bold=True,
            background_color=hex_to_rgba('#17a2b8'),
            color=hex_to_rgba(COLORS['white'])
        )
        self.back_button.bind(on_press=self.back_to_list)
        button_box.add_widget(self.back_button)

        inner_frame.add_widget(button_box)

        # 底部提示文字
        footer = Label(
            text='按屏幕任意位置快速点名 | 点击名单查看详情',
            font_size=sp(12),
            font_name='SimHei',
            color=hex_to_rgba(COLORS['text_gray']),
            size_hint_y=None,
            height=dp(25)
        )
        inner_frame.add_widget(footer)

        self.outer_frame.add_widget(inner_frame)
        anchor.add_widget(self.outer_frame)
        self.main_layout.add_widget(anchor)

        # 添加点击事件 - 点击屏幕任意位置开始点名
        self.main_layout.bind(on_touch_down=self.on_screen_touch)

        self.add_widget(self.main_layout)

    # 更新画布方法
    def update_decor(self, instance, value):
        self.bg_rect.pos = (0, 0)
        self.bg_rect.size = Window.size

    def update_outer(self, instance, value):
        self.outer_bg.pos = instance.pos
        self.outer_bg.size = instance.size
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*hex_to_rgba(COLORS['bg_medium']))
            Rectangle(pos=instance.pos, size=instance.size)
            Color(*hex_to_rgba(COLORS['accent_red'], 0.5))
            Line(rectangle=(instance.x, instance.y, instance.width, instance.height), width=dp(3))

    def update_inner(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*hex_to_rgba(COLORS['bg_light']))
            Rectangle(pos=instance.pos, size=instance.size)
            Color(*hex_to_rgba(COLORS['accent_blue'], 0.3))
            Line(rectangle=(instance.x, instance.y, instance.width, instance.height), width=dp(2))

    def update_sep1(self, instance, value):
        instance.canvas.clear()
        with instance.canvas:
            Color(*hex_to_rgba(COLORS['accent_red']))
            Rectangle(pos=instance.pos, size=instance.size)

    def update_sep2(self, instance, value):
        instance.canvas.clear()
        with instance.canvas:
            Color(*hex_to_rgba(COLORS['accent_red']))
            Rectangle(pos=instance.pos, size=instance.size)

    def update_display(self, instance, value):
        self.display_bg.pos = instance.pos
        self.display_bg.size = instance.size
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*hex_to_rgba(COLORS['bg_light']))
            Rectangle(pos=instance.pos, size=instance.size)
            Color(*hex_to_rgba(COLORS['accent_red'], 0.5))
            Line(rectangle=(instance.x, instance.y, instance.width, instance.height), width=dp(4))

    def update_name_bg(self, instance, value):
        self.name_bg.pos = instance.pos
        self.name_bg.size = instance.size

    def draw_stars(self):
        """绘制星星装饰"""
        self.star_graphics = []
        star_positions = [
            (0.1, 0.85, 4), (0.3, 0.9, 3), (0.7, 0.88, 5), (0.9, 0.85, 4),
            (0.15, 0.6, 3), (0.85, 0.65, 4), (0.2, 0.35, 5), (0.8, 0.3, 3),
            (0.1, 0.1, 4), (0.9, 0.15, 5), (0.4, 0.05, 3), (0.6, 0.08, 4)
        ]

        for x, y, size in star_positions:
            star = Widget()
            with star.canvas:
                Color(*hex_to_rgba(COLORS['accent_yellow']))
                Ellipse(pos=(x * Window.width, y * Window.height), size=(dp(size*3), dp(size*3)))
            self.star_graphics.append((star, x, y, size))
            self.decor_canvas.add_widget(star)

    def draw_corner_decorations(self):
        """绘制边角装饰"""
        self.corner_graphics = []
        corner_size = dp(50)
        line_width = dp(3)
        colors = [COLORS['accent_red'], COLORS['accent_green'],
                  COLORS['accent_yellow'], COLORS['accent_blue']]

        corners = [
            (0.02, 0.98, [(0, -corner_size/2), (0, 0), (corner_size/2, 0)]),  # 左上
            (0.98, 0.98, [(0, -corner_size/2), (0, 0), (-corner_size/2, 0)]),  # 右上
            (0.02, 0.02, [(0, corner_size/2), (0, 0), (corner_size/2, 0)]),   # 左下
            (0.98, 0.02, [(0, corner_size/2), (0, 0), (-corner_size/2, 0)])    # 右下
        ]

        for i, (cx, cy, points) in enumerate(corners):
            corner = Widget()
            abs_points = [
                (cx * Window.width + points[0][0], cy * Window.height + points[0][1]),
                (cx * Window.width + points[1][0], cy * Window.height + points[1][1]),
                (cx * Window.width + points[2][0], cy * Window.height + points[2][1])
            ]
            with corner.canvas:
                Color(*hex_to_rgba(colors[i]))
                Line(points=[abs_points[0][0], abs_points[0][1],
                            abs_points[1][0], abs_points[1][1],
                            abs_points[2][0], abs_points[2][1]],
                     width=line_width)
            self.corner_graphics.append((corner, cx, cy, points, colors[i]))
            self.decor_canvas.add_widget(corner)

    def animate_stars(self, dt):
        """星星闪烁动画"""
        for star, x, y, size in self.star_graphics:
            if random.random() < 0.1:  # 10%概率闪烁
                color = random.choice([
                    COLORS['accent_yellow'],
                    '#ffed4a', '#fff59d', COLORS['white']
                ])
                star.canvas.clear()
                with star.canvas:
                    Color(*hex_to_rgba(color))
                    Ellipse(pos=(x * Window.width, y * Window.height),
                           size=(dp(size*3), dp(size*3)))
        return True

    def on_window_resize(self, window, width, height):
        """窗口大小变化时更新"""
        self.bg_rect.size = (width, height)
        # 重新绘制星星和边角
        for star, x, y, size in self.star_graphics:
            star.canvas.clear()
            with star.canvas:
                Color(*hex_to_rgba(COLORS['accent_yellow']))
                Ellipse(pos=(x * width, y * height), size=(dp(size*3), dp(size*3)))

    def on_screen_touch(self, instance, touch):
        """屏幕触摸事件"""
        if self.collide_point(*touch.pos) and not self.animation_running:
            if touch.y > dp(100):  # 避免点击底部按钮区域
                self.roll_name(None)

    def on_enter(self):
        """进入界面时加载数据"""
        app = self.manager.parent
        if hasattr(app, 'current_rollcall_names'):
            self.names = app.current_rollcall_names
        if hasattr(app, 'current_rollcall_title'):
            self.rollcall_name = app.current_rollcall_title
        if hasattr(app, 'current_allow_repeat'):
            self.allow_repeat = app.current_allow_repeat

        # 更新标题
        self.title_label.text = f'✨ {self.rollcall_name or "幸运点名器"} ✨'

    def roll_name(self, instance):
        """随机点名"""
        if self.animation_running or not self.names:
            return

        # 计算可点名的人
        name_total_count = {}
        name_picked_count = {}

        for name in self.names:
            name_total_count[name] = name_total_count.get(name, 0) + 1
        for name in self.picked_names:
            name_picked_count[name] = name_picked_count.get(name, 0) + 1

        available_names = []
        for name in name_total_count:
            total = name_total_count[name]
            picked = name_picked_count.get(name, 0)
            remaining = total - picked
            available_names.extend([name] * remaining)

        if not available_names:
            self.show_message('提示', '所有人都已达到指定的出现次数！\n请点击重置按钮重新开始。')
            return

        selected_name = random.choice(available_names)
        if not self.allow_repeat:
            self.picked_names.append(selected_name)

        self.animate_name(selected_name)

    def animate_name(self, final_name):
        """名字切换动画"""
        self.animation_running = True
        colors = [COLORS['accent_red'], COLORS['accent_yellow'],
                  COLORS['accent_purple'], COLORS['accent_blue']]
        scroll_count = 12
        current = [0]

        def scroll_step():
            if current[0] < scroll_count:
                temp_name = random.choice(self.names)
                color = colors[current[0] % len(colors)]
                self.name_display.text = temp_name
                self.name_display.color = hex_to_rgba(color)
                current[0] += 1
                Clock.schedule_once(lambda dt: scroll_step(), 0.08 + current[0] * 0.02)
            else:
                # 动画结束
                self.name_display.text = final_name
                self.name_display.color = hex_to_rgba(COLORS['accent_green'])

                # 背景变绿效果
                self.flash_green()

                # 创建粒子效果
                self.create_particle_effect()

                # 恢复状态
                Clock.schedule_once(lambda dt: self.end_animation(), 1.5)

        scroll_step()

    def flash_green(self):
        """绿色闪烁效果"""
        original_bg = self.name_bg.color if hasattr(self.name_bg, 'color') else hex_to_rgba(COLORS['bg_medium'])

        with self.name_display.canvas.before:
            Color(*hex_to_rgba(COLORS['accent_green']))
            self.name_bg = Rectangle(pos=self.name_display.pos, size=self.name_display.size)

        self.name_display.color = hex_to_rgba(COLORS['white'])

        def restore():
            self.name_display.canvas.before.clear()
            with self.name_display.canvas.before:
                Color(*hex_to_rgba(COLORS['bg_medium']))
                self.name_bg = Rectangle(pos=self.name_display.pos, size=self.name_display.size)
            self.name_display.color = hex_to_rgba(COLORS['accent_green'])

        Clock.schedule_once(lambda dt: restore(), 0.3)

    def create_particle_effect(self):
        """创建粒子爆炸效果"""
        center_x = Window.width / 2
        center_y = Window.height / 2

        for _ in range(80):
            p = Particle(center_x, center_y, self.decor_canvas.canvas)
            self.particles.append(p)

        Clock.schedule_interval(self.update_particles, 0.03)

    def update_particles(self, dt):
        """更新粒子"""
        if not self.particles:
            return False

        self.decor_canvas.canvas.clear()

        # 重绘背景
        with self.decor_canvas.canvas:
            Color(*hex_to_rgba(COLORS['bg_dark']))
            Rectangle(pos=(0, 0), size=Window.size)

        # 重绘星星
        for star, x, y, size in self.star_graphics:
            with self.decor_canvas.canvas:
                Color(*hex_to_rgba(COLORS['accent_yellow']))
                Ellipse(pos=(x * Window.width, y * Window.height),
                       size=(dp(size*3), dp(size*3)))

        # 重绘边角
        for corner, cx, cy, points, color in self.corner_graphics:
            abs_points = [
                (cx * Window.width + points[0][0], cy * Window.height + points[0][1]),
                (cx * Window.width + points[1][0], cy * Window.height + points[1][1]),
                (cx * Window.width + points[2][0], cy * Window.height + points[2][1])
            ]
            with self.decor_canvas.canvas:
                Color(*hex_to_rgba(color))
                Line(points=[abs_points[0][0], abs_points[0][1],
                            abs_points[1][0], abs_points[1][1],
                            abs_points[2][0], abs_points[2][1]],
                     width=dp(3))

        # 绘制粒子
        alive_particles = []
        for p in self.particles:
            if p.update(dt):
                with self.decor_canvas.canvas:
                    Color(*hex_to_rgba(p.color))
                    Ellipse(pos=(p.x - p.size/2, p.y - p.size/2),
                           size=(p.size, p.size))
                alive_particles.append(p)

        self.particles = alive_particles
        return len(self.particles) > 0

    def end_animation(self):
        """结束动画"""
        self.animation_running = False
        self.update_list_window()

    def reset_display(self, instance):
        """重置显示"""
        if not self.animation_running:
            self.name_display.text = '准备就绪'
            self.name_display.color = hex_to_rgba(COLORS['accent_green'])
            self.picked_names = []
            self.show_message('重置成功', '已重置所有点名记录！')
            self.update_list_window()

    def show_name_list(self, instance):
        """显示人名列表"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        # 标题
        title_text = f'📋 点名名单 ({len(self.picked_names)}/{len(self.names)})' if not self.allow_repeat else '📋 点名名单'
        title = Label(
            text=title_text,
            font_size=sp(18),
            font_name='SimHei',
            bold=True,
            color=hex_to_rgba(COLORS['accent_red']),
            size_hint_y=None,
            height=dp(35)
        )
        content.add_widget(title)

        # 列表
        scroll = ScrollView()
        list_layout = BoxLayout(orientation='vertical', spacing=dp(3), size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))

        if self.allow_repeat:
            # 可重复模式 - 显示所有人名
            for name in self.names:
                row = BoxLayout(size_hint_y=None, height=dp(35))
                lbl = Label(
                    text=f'  {name}',
                    font_size=sp(14),
                    font_name='SimHei',
                    color=hex_to_rgba(COLORS['text_light']),
                    halign='left'
                )
                lbl.bind(size=lbl.setter('text_size'))
                row.add_widget(lbl)
                list_layout.add_widget(row)
        else:
            # 不可重复模式 - 显示剩余次数
            name_total_count = {}
            name_picked_count = {}

            for name in self.names:
                name_total_count[name] = name_total_count.get(name, 0) + 1
            for name in self.picked_names:
                name_picked_count[name] = name_picked_count.get(name, 0) + 1

            unique_names = list(name_total_count.keys())
            for name in unique_names:
                total = name_total_count[name]
                picked = name_picked_count.get(name, 0)
                remaining = total - picked

                row = BoxLayout(size_hint_y=None, height=dp(35))

                if remaining > 0:
                    lbl = Label(
                        text=f'  {name} (剩余: {remaining}次)',
                        font_size=sp(14),
                        font_name='SimHei',
                        color=hex_to_rgba(COLORS['text_light']),
                        halign='left'
                    )
                else:
                    lbl = Label(
                        text=f'✓ {name} (已点完)',
                        font_size=sp(14),
                        font_name='SimHei',
                        color=hex_to_rgba(COLORS['accent_green']),
                        halign='left'
                    )

                lbl.bind(size=lbl.setter('text_size'))
                row.add_widget(lbl)
                list_layout.add_widget(row)

        scroll.add_widget(list_layout)
        content.add_widget(scroll)

        # 关闭按钮
        btn_close = Button(
            text='关闭',
            font_size=sp(14),
            font_name='SimHei',
            size_hint_y=None,
            height=dp(45),
            background_color=hex_to_rgba(COLORS['accent_blue'])
        )
        content.add_widget(btn_close)

        self.list_popup = Popup(
            title='点名名单',
            content=content,
            size_hint=(0.85, 0.7),
            auto_dismiss=False
        )
        btn_close.bind(on_press=self.list_popup.dismiss)
        self.list_popup.open()

    def update_list_window(self):
        """更新名单窗口"""
        if hasattr(self, 'list_popup') and self.list_popup:
            self.list_popup.dismiss()
            self.show_name_list(None)

    def toggle_fullscreen(self, instance):
        """切换全屏"""
        # 在移动端全屏模式有限
        pass

    def exit_app(self, instance):
        """退出应用"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        lbl = Label(
            text='确定要退出点名器吗？',
            font_size=sp(16),
            font_name='SimHei',
            color=hex_to_rgba(COLORS['text_light'])
        )
        content.add_widget(lbl)

        btn_box = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(50))

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
            background_color=hex_to_rgba(COLORS['accent_blue'])
        )

        btn_box.add_widget(btn_yes)
        btn_box.add_widget(btn_no)
        content.add_widget(btn_box)

        popup = Popup(
            title='确认退出',
            content=content,
            size_hint=(0.8, 0.3),
            auto_dismiss=False
        )

        def on_yes(btn):
            popup.dismiss()
            self.manager.current = 'main'

        btn_yes.bind(on_press=on_yes)
        btn_no.bind(on_press=popup.dismiss)
        popup.open()

    def back_to_list(self, instance):
        """返回列表"""
        self.manager.current = 'list'

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
            size_hint=(0.8, 0.3),
            auto_dismiss=False
        )
        btn.bind(on_press=popup.dismiss)
        popup.open()
