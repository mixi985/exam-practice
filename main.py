"""
刷题软件 - 手机版 (Kivy)
主入口文件
"""
import os
import sys

# 设置运行时目录
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window

# 设置手机竖屏比例
Window.size = (360, 640)

from config import PRIMARY_COLOR, SUCCESS_COLOR, ERROR_COLOR
from database import QuestionDB


# ============================================================
# 首页
# ============================================================
class HomeScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self._build()

    def _build(self):
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.graphics import Color, RoundedRectangle
        from kivy.uix.widget import Widget

        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)
        layout.canvas.before.clear()
        with layout.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=layout.pos, size=layout.size)
        self.bind(size=self._update_rect, pos=self._update_rect)
        self._rect = layout

        # 顶部标题
        title = Label(
            text="刷题软件",
            font_size="22sp",
            color=(0.2, 0.3, 0.4, 1),
            size_hint_y=None,
            height=50
        )
        layout.add_widget(title)

        # 统计信息
        stats = self.app.db.get_stats()
        stats_text = (
            f"题库总数：{stats['total']} 题\n"
            f"已答对：{stats['correct']} 题\n"
            f"已答错：{stats['wrong']} 题"
        )
        stats_label = Label(
            text=stats_text,
            font_size="14sp",
            color=(0.3, 0.4, 0.5, 1),
            size_hint_y=None,
            height=80,
            halign="center"
        )
        layout.add_widget(stats_label)

        # 功能按钮
        def make_btn(text, color, callback):
            btn = Button(
                text=text,
                font_size="16sp",
                size_hint_y=None,
                height=55,
                background_normal="",
                background_color=color,
                color=(1, 1, 1, 1)
            )
            btn.bind(on_release=callback)
            return btn

        layout.add_widget(make_btn("开始刷题", (0.36, 0.62, 0.89, 1), lambda _: self.go_practice("random")))
        layout.add_widget(make_btn("顺序刷题", (0.34, 0.62, 0.85, 1), lambda _: self.go_practice("sequence")))
        layout.add_widget(make_btn("错题本", (0.93, 0.44, 0.39, 1), self.go_wrong))
        layout.add_widget(make_btn("题库管理", (0.35, 0.57, 0.74, 1), self.go_manage))

        # 底部信息
        info = Label(
            text="v1.0 · 本地离线运行",
            font_size="12sp",
            color=(0.5, 0.55, 0.6, 1),
            size_hint_y=None,
            height=30
        )
        layout.add_widget(Widget())
        layout.add_widget(info)

        self.add_widget(layout)

    def _update_rect(self, instance, value):
        if hasattr(instance, "canvas") and instance.canvas.before:
            pass

    def go_practice(self, mode):
        self.app.current_mode = mode
        self.app.screen_manager.current = "practice"

    def go_wrong(self, _):
        self.app.screen_manager.current = "wrong"

    def go_manage(self, _):
        self.app.screen_manager.current = "manage"


# ============================================================
# 刷题页
# ============================================================
class PracticeScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.questions = []
        self.index = 0
        self._build_ui()

    def on_pre_enter(self):
        self._load_questions()

    def _load_questions(self):
        mode = self.app.current_mode
        if mode == "random":
            self.questions = self.app.db.get_random_questions(50)
        else:
            self.questions = self.app.db.get_all_questions()
        self.index = 0
        self._show_question()

    def _build_ui(self):
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.scrollview import ScrollView

        self.root_layout = BoxLayout(orientation="vertical", padding=15, spacing=10)

        # 顶部导航栏
        nav = BoxLayout(orientation="horizontal", size_hint_y=None, height=45, spacing=8)
        back_btn = Button(text="← 返回", font_size="14sp", size_hint_x=None, width=80,
                         background_normal="", background_color=(0.36, 0.62, 0.89, 1))
        back_btn.bind(on_release=self.go_back)
        self.progress_label = Label(text="0 / 0", font_size="13sp",
                                    color=(0.3, 0.4, 0.5, 1))
        nav.add_widget(back_btn)
        nav.add_widget(self.progress_label)
        self.root_layout.add_widget(nav)

        # 内容滚动区域
        self.content = BoxLayout(orientation="vertical", size_hint_y=None, spacing=12)
        self.content.bind(minimum_height=self.content.setter("height"))

        self.question_label = Label(text="加载中...", font_size="16sp",
                                    color=(0.15, 0.2, 0.3, 1),
                                    size_hint_y=None, valign="top",
                                    text_size=(330, None), halign="left")
        self.question_label.bind(texture_size=self._set_q_height)
        self.content.add_widget(self.question_label)

        self.option_buttons = []
        for i in range(4):
            btn = Button(text="", font_size="14sp", size_hint_y=None, height=50,
                        background_normal="", background_color=(0.9, 0.92, 0.95, 1),
                        color=(0.2, 0.3, 0.4, 1))
            self.option_buttons.append(btn)
            self.content.add_widget(btn)

        self.result_label = Label(text="", font_size="14sp", size_hint_y=None,
                                  height=50, color=(0.3, 0.4, 0.5, 1))
        self.content.add_widget(self.result_label)

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.content)
        self.root_layout.add_widget(scroll)

        self.add_widget(self.root_layout)

    def _set_q_height(self, instance, value):
        instance.height = value[1] + 10

    def _show_question(self):
        if not self.questions:
            self.question_label.text = "暂无题目，请先导入题库"
            for btn in self.option_buttons:
                btn.text = ""
            return
        if self.index >= len(self.questions):
            self.question_label.text = f"已完成全部 {len(self.questions)} 道题目！"
            for btn in self.option_buttons:
                btn.text = ""
            self.result_label.text = ""
            return

        q = self.questions[self.index]
        self.progress_label.text = f"{self.index + 1} / {len(self.questions)}"
        self.question_label.text = q["question_text"]
        self.result_label.text = ""

        options = q.get("options", [])
        letters = ["A", "B", "C", "D"]
        for i, btn in enumerate(self.option_buttons):
            if i < len(options):
                btn.text = f"{letters[i]}. {options[i]}"
                btn.background_color = (0.9, 0.92, 0.95, 1)
                btn.color = (0.2, 0.3, 0.4, 1)
                btn.disabled = False
                btn.unbind(on_release=self._check_answer)
                btn.bind(on_release=self._check_answer)
            else:
                btn.text = ""
                btn.disabled = True

    def _check_answer(self, btn):
        if not self.questions:
            return
        q = self.questions[self.index]
        correct = q.get("correct_answer", "A").upper()
        selected = btn.text[0] if btn.text else ""

        for i, b in enumerate(self.option_buttons):
            letter = ["A", "B", "C", "D"][i]
            if letter == correct:
                b.background_color = (0.35, 0.74, 0.55, 1)
                b.color = (1, 1, 1, 1)
            elif letter == selected and selected != correct:
                b.background_color = (0.93, 0.44, 0.39, 1)
                b.color = (1, 1, 1, 1)

        if selected == correct:
            self.result_label.text = "✓ 回答正确！"
            self.result_label.color = (0.35, 0.74, 0.55, 1)
        else:
            self.result_label.text = f"✗ 正确答案：{correct}"
            self.result_label.color = (0.93, 0.44, 0.39, 1)

        # 禁用按钮后，显示下一题按钮
        for b in self.option_buttons:
            b.unbind(on_release=self._check_answer)
            if b.text:
                b.bind(on_release=self._next_question)

    def _next_question(self, *_):
        self.index += 1
        self._show_question()

    def go_back(self, _):
        self.app.screen_manager.current = "home"


# ============================================================
# 错题本页
# ============================================================
class WrongScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self._build()

    def _build(self):
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.scrollview import ScrollView

        layout = BoxLayout(orientation="vertical", padding=15, spacing=10)

        nav = BoxLayout(orientation="horizontal", size_hint_y=None, height=45, spacing=8)
        back_btn = Button(text="← 返回", font_size="14sp", size_hint_x=None, width=80,
                         background_normal="", background_color=(0.36, 0.62, 0.89, 1))
        back_btn.bind(on_release=lambda _: self.app.screen_manager.current="home")
        title = Label(text="错题本", font_size="16sp", color=(0.2, 0.3, 0.4, 1))
        nav.add_widget(back_btn)
        nav.add_widget(title)
        layout.add_widget(nav)

        content = BoxLayout(orientation="vertical", size_hint_y=None, spacing=8)
        content.bind(minimum_height=content.setter("height"))

        self.info_label = Label(text="", font_size="13sp", color=(0.3, 0.4, 0.5, 1),
                               size_hint_y=None, height=30)
        content.add_widget(self.info_label)

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.content_area = content

        self.add_widget(layout)

    def on_pre_enter(self):
        self._refresh()

    def _refresh(self):
        for child in [c for c in self.content_area.children if c is not self.info_label]:
            self.content_area.remove_widget(child)

        from kivy.uix.label import Label
        wrong_count = len(self.app.db.get_wrong_questions())
        self.info_label.text = f"共 {wrong_count} 道错题"

        for q in self.app.db.get_wrong_questions()[:20]:
            item = Label(
                text=f"[b]Q:[/b] {q['question_text'][:40]}...\n正确答案：{q.get('correct_answer','A')}",
                font_size="13sp", color=(0.2, 0.3, 0.4, 1),
                size_hint_y=None, height=70, markup=True,
                text_size=(320, None), halign="left", valign="top"
            )
            item.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1] + 10))
            self.content_area.add_widget(item)


# ============================================================
# 题库管理页
# ============================================================
class ManageScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self._build()

    def _build(self):
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.textinput import TextInput
        from kivy.uix.scrollview import ScrollView

        layout = BoxLayout(orientation="vertical", padding=15, spacing=10)

        nav = BoxLayout(orientation="horizontal", size_hint_y=None, height=45, spacing=8)
        back_btn = Button(text="← 返回", font_size="14sp", size_hint_x=None, width=80,
                         background_normal="", background_color=(0.36, 0.62, 0.89, 1))
        back_btn.bind(on_release=lambda _: self.app.screen_manager.current="home")
        title = Label(text="题库管理", font_size="16sp", color=(0.2, 0.3, 0.4, 1))
        nav.add_widget(back_btn)
        nav.add_widget(title)
        layout.add_widget(nav)

        self.stats_label = Label(text="", font_size="14sp", color=(0.3, 0.4, 0.5, 1),
                                size_hint_y=None, height=40)
        layout.add_widget(self.stats_label)

        # 手动添加题目
        hint = Label(text="快速添加题目（格式：题干 | A选项 | B选项 | C选项 | D选项 | 答案）",
                    font_size="12sp", color=(0.4, 0.45, 0.5, 1),
                    size_hint_y=None, height=50, text_size=(330, None), halign="left")
        layout.add_widget(hint)

        self.ti = TextInput(hint_text="1+1等于几 | 1 | 2 | 3 | 4 | B", multiline=True,
                           size_hint_y=None, height=80, font_size="12sp")
        layout.add_widget(self.ti)

        add_btn = Button(text="添加到题库", font_size="14sp", size_hint_y=None, height=50,
                        background_normal="", background_color=(0.35, 0.74, 0.55, 1))
        add_btn.bind(on_release=self._add_question)
        layout.add_widget(add_btn)

        sample_btn = Button(text="加载示例题目", font_size="13sp", size_hint_y=None, height=45,
                           background_normal="", background_color=(0.34, 0.62, 0.85, 1))
        sample_btn.bind(on_release=self._load_samples)
        layout.add_widget(sample_btn)

        clear_btn = Button(text="清空题库", font_size="13sp", size_hint_y=None, height=45,
                          background_normal="", background_color=(0.93, 0.44, 0.39, 1))
        clear_btn.bind(on_release=self._clear_db)
        layout.add_widget(clear_btn)

        self.msg_label = Label(text="", font_size="12sp", color=(0.4, 0.5, 0.6, 1),
                              size_hint_y=None, height=30)
        layout.add_widget(self.msg_label)

        from kivy.uix.widget import Widget
        layout.add_widget(Widget())

        self.add_widget(layout)

    def on_pre_enter(self):
        self._refresh_stats()

    def _refresh_stats(self):
        stats = self.app.db.get_stats()
        self.stats_label.text = f"题库总数：{stats['total']} 题"

    def _add_question(self, _):
        text = self.ti.text.strip()
        if not text:
            self.msg_label.text = "请输入题目内容"
            return
        parts = [p.strip() for p in text.split("|")]
        if len(parts) < 6:
            self.msg_label.text = "格式错误，请用 | 分隔"
            return
        q_text, a, b, c, d, ans = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5].upper()
        if ans not in ["A", "B", "C", "D"]:
            self.msg_label.text = "答案必须是 A/B/C/D"
            return
        self.app.db.add_question(q_text, [a, b, c, d], ans, "", "默认")
        self.ti.text = ""
        self.msg_label.text = "✓ 添加成功"
        self._refresh_stats()

    def _load_samples(self, _):
        samples = [
            ("道路交通安全违法行为累积记分周期是多长时间？", ["6个月", "12个月", "18个月", "24个月"], "B"),
            ("驾驶机动车在道路上超车时，应当提前开启什么灯？", ["左转向灯", "右转向灯", "危险报警闪光灯", "近光灯"], "A"),
            ("机动车驾驶证的有效期分为几种？", ["6年、10年、长期", "3年、6年、10年", "5年、10年、长期", "6年、10年、20年"], "A"),
            ("红色圆形信号灯亮时，表示什么？", ["准许车辆通行", "禁止车辆通行", "警示车辆减速", "车辆准备通行"], "B"),
            ("驾驶机动车在高速公路上行驶，遇到雨雪雾尘天气时，能见度小于50米时，车速不得超过多少？", ["20公里/小时", "30公里/小时", "40公里/小时", "50公里/小时"], "A"),
            ("机动车在道路上发生故障难以移动时，应当在车后多少米处设置警告标志？", ["50米以内", "50-100米", "100-150米", "150米以外"], "D"),
            ("饮酒后驾驶机动车的，一次记多少分？", ["3分", "6分", "9分", "12分"], "D"),
            ("驾驶机动车在夜间会车时，应当在距对方来车多远距离改用近光灯？", ["50米", "100米", "150米", "200米"], "C"),
            ("机动车驾驶人初次申领机动车驾驶证后的多少个月为实习期？", ["3个月", "6个月", "12个月", "24个月"], "C"),
            ("在没有中心线的道路上，机动车遇相对方向来车时应该怎样行驶？", ["减速靠右行驶", "加速通过", "靠路中间行驶", "鸣喇叭通过"], "A"),
        ]
        count = 0
        for q, opts, ans in samples:
            self.app.db.add_question(q, opts, ans, "", "默认")
            count += 1
        self.msg_label.text = f"✓ 已加载 {count} 道示例题目"
        self._refresh_stats()

    def _clear_db(self, _):
        self.app.db.clear_all()
        self.msg_label.text = "题库已清空"
        self._refresh_stats()


# ============================================================
# 主应用
# ============================================================
class PracticeApp(App):
    title = "刷题软件"

    def build(self):
        self.db = QuestionDB(DATA_DIR)
        self.current_mode = "random"

        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(HomeScreen(self, name="home"))
        self.screen_manager.add_widget(PracticeScreen(self, name="practice"))
        self.screen_manager.add_widget(WrongScreen(self, name="wrong"))
        self.screen_manager.add_widget(ManageScreen(self, name="manage"))
        self.screen_manager.current = "home"

        return self.screen_manager


if __name__ == "__main__":
    PracticeApp().run()
