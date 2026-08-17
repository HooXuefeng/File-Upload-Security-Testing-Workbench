#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import threading
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import Qt, Signal, QObject, QThread
from PySide6.QtGui import QAction, QColor, QFont, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QCheckBox, QPlainTextEdit,
    QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QStackedWidget,
    QFrame, QProgressBar, QHeaderView, QSplitter, QTabWidget, QListWidget,
    QListWidgetItem, QDialog, QDialogButtonBox, QFormLayout, QSpinBox, QDoubleSpinBox, QColorDialog
)

from uploadsentinel import (
    Scanner, RuleConfig, build_safe_cases, custom_case_from_text,
    save_json, save_csv, save_html, save_project, load_project,
    load_history, append_history, save_history, clear_history
)


DARK = {
    "bg":"#151817",
    "panel":"#1D211F",
    "panel2":"#242A27",
    "card":"#1D211F",
    "text":"#E8E4DA",
    "muted":"#9B9D94",
    "border":"#1D211F",
    "accent":"#9BAF95",
    "accent2":"#C2A48E",
    "green":"#9BAF95",
    "orange":"#C2A48E",
    "red":"#A77D72",
    "purple":"#8D8F9B",
    "review":"#7E8792",
    "entry":"#1A1E1C",
    "band1":"#8FA394",
    "band2":"#C0A58D",
    "band3":"#7E8792",
    "darkshape":"#101311"
}
LIGHT = {
    "bg":"#EAE7DF",
    "panel":"#EAE7DF",
    "panel2":"#DED9CF",
    "card":"#EAE7DF",
    "text":"#292E2B",
    "muted":"#777B74",
    "border":"#EAE7DF",
    "accent":"#8FA394",
    "accent2":"#C0A58D",
    "green":"#8FA394",
    "orange":"#C0A58D",
    "red":"#A77D72",
    "purple":"#7E8792",
    "review":"#7E8792",
    "entry":"#E1DDD4",
    "band1":"#8FA394",
    "band2":"#C0A58D",
    "band3":"#7E8792",
    "darkshape":"#343A36"
}


def qss(c):
    return f"""
    QWidget {{
        background: {c['bg']};
        color: {c['text']};
        font-family: "Microsoft YaHei UI", "Noto Sans CJK SC", "Segoe UI";
        font-size: 10pt;
    }}

    QMainWindow {{
        background: {c['bg']};
    }}

    QLabel {{
        background: transparent;
        border: none;
    }}

    QFrame#sidebar {{
        background: {c['panel']};
        border: none;
    }}

    QFrame#topbar {{
        background: {c['bg']};
        border: none;
    }}

    QFrame#card {{
        background: transparent;
        border: none;
    }}

    QLabel#pageTitle {{
        font-size: 25pt;
        font-weight: 600;
        letter-spacing: 1px;
        color: {c['text']};
    }}

    QLabel#muted {{
        color: {c['muted']};
    }}

    QLabel#brand {{
        background: transparent;
        border: none;
        font-size: 15pt;
        font-weight: 600;
        color: {c['text']};
        padding: 0px;
    }}

    QLabel#sectionTitle {{
        font-size: 12pt;
        font-weight: 600;
        color: {c['text']};
    }}

    QPushButton {{
        background: transparent;
        color: {c['text']};
        border: none;
        border-radius: 0px;
        padding: 8px 10px;
        min-height: 20px;
    }}

    QPushButton:hover {{
        background: {c['panel2']};
        color: {c['text']};
    }}

    QPushButton:pressed {{
        background: {c['entry']};
    }}

    QPushButton#primary {{
        background: {c['darkshape']};
        color: #F2EFE7;
        border: none;
        border-radius: 0px;
        font-weight: 600;
        padding: 10px 18px;
    }}

    QPushButton#primary:hover {{
        background: {c['text']};
        color: {c['bg']};
    }}

    QPushButton#danger {{
        background: transparent;
        color: {c['red']};
        border: none;
    }}

    QPushButton#nav {{
        text-align: left;
        padding: 10px 4px;
        border: none;
        background: transparent;
        color: {c['muted']};
        font-size: 10pt;
    }}

    QPushButton#nav:hover {{
        background: transparent;
        color: {c['text']};
    }}

    QPushButton#navActive {{
        text-align: left;
        padding: 10px 4px;
        border: none;
        background: transparent;
        color: {c['text']};
        font-weight: 600;
    }}

    QLineEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
        background: {c['entry']};
        color: {c['text']};
        border: none;
        border-radius: 0px;
        padding: 8px 10px;
        selection-background-color: {c['band1']};
    }}

    QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus,
    QSpinBox:focus, QDoubleSpinBox:focus {{
        background: {c['panel2']};
        border: none;
    }}

    QCheckBox {{
        spacing: 8px;
        color: {c['text']};
        background: transparent;
    }}

    QCheckBox::indicator {{
        width: 15px;
        height: 15px;
        border: none;
        background: {c['panel2']};
    }}

    QCheckBox::indicator:checked {{
        background: {c['band1']};
    }}

    QTableWidget {{
        background: transparent;
        color: {c['text']};
        gridline-color: transparent;
        border: none;
        alternate-background-color: {c['panel2']};
        selection-background-color: {c['band1']};
        selection-color: {c['darkshape']};
    }}

    QHeaderView::section {{
        background: transparent;
        color: {c['muted']};
        border: none;
        padding: 9px 8px;
        font-weight: 600;
    }}

    QProgressBar {{
        background: {c['panel2']};
        color: transparent;
        border: none;
        border-radius: 0px;
        height: 6px;
        text-align: center;
    }}

    QProgressBar::chunk {{
        background: {c['band1']};
        border-radius: 0px;
    }}

    QTabWidget::pane {{
        border: none;
        background: transparent;
    }}

    QTabBar::tab {{
        background: transparent;
        color: {c['muted']};
        padding: 8px 14px;
        border: none;
    }}

    QTabBar::tab:selected {{
        color: {c['text']};
        background: transparent;
        font-weight: 600;
    }}

    QListWidget {{
        background: transparent;
        color: {c['text']};
        border: none;
        padding: 0px;
    }}

    QListWidget::item {{
        padding: 10px 6px;
        border: none;
    }}

    QListWidget::item:selected {{
        background: {c['panel2']};
        color: {c['text']};
    }}

    QSplitter::handle {{
        background: {c['bg']};
    }}

    QToolTip {{
        background: {c['darkshape']};
        color: #F2EFE7;
        border: none;
        padding: 6px 8px;
    }}
    """


class Worker(QObject):
    progress = Signal(int, int, object)
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, scanner, cases):
        super().__init__()
        self.scanner = scanner
        self.cases = cases

    def run(self):
        try:
            def cb(i, n, case, result):
                self.progress.emit(i, n, result)
            results = self.scanner.run(self.cases, cb)
            self.finished.emit(results)
        except Exception as e:
            self.failed.emit(str(e))


class DropTextEdit(QPlainTextEdit):
    fileDropped = Signal(str)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e: QDragEnterEvent):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
        else:
            super().dragEnterEvent(e)

    def dropEvent(self, e: QDropEvent):
        urls = e.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if path:
                self.fileDropped.emit(path)
                e.acceptProposedAction()
                return
        super().dropEvent(e)


class CustomCaseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加自定义无害用例 / Add Custom Benign Case")
        form = QFormLayout(self)
        self.name = QLineEdit("custom_case")
        self.filename = QLineEdit("custom.txt")
        self.mime = QLineEdit("text/plain")
        self.level = QComboBox()
        self.level.addItems(["低档 / Low", "中档 / Medium", "高档 / High"])
        self.level.setCurrentText("中档 / Medium")
        self.content = QPlainTextEdit("SAFE_CUSTOM_UPLOAD_TEST")
        self.content.setMaximumHeight(120)
        form.addRow("用例名称 / Case name", self.name)
        form.addRow("文件名 / Filename", self.filename)
        form.addRow("Content-Type", self.mime)
        form.addRow("测试档位 / Level", self.level)
        form.addRow("无害内容 / Benign content", self.content)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)


class ThemeDialog(QDialog):
    def __init__(self, current_colors, parent=None):
        super().__init__(parent)
        self.setWindowTitle("自定义主题配色")
        self.setMinimumWidth(520)
        self.colors = dict(current_colors)

        layout = QVBoxLayout(self)
        intro = QLabel("选择需要调整的核心颜色。建议保持低饱和、少色带和较强留白。")
        intro.setWordWrap(True)
        layout.addWidget(intro)

        self.rows = {}
        form = QFormLayout()
        layout.addLayout(form)

        items = [
            ("bg", "背景色"),
            ("text", "主要文字"),
            ("muted", "次级文字"),
            ("entry", "输入区域"),
            ("band1", "主色带"),
            ("band2", "辅色带"),
            ("band3", "第三色带"),
            ("darkshape", "暗部结构"),
        ]

        for key, label in items:
            row = QWidget()
            hl = QHBoxLayout(row)
            hl.setContentsMargins(0, 0, 0, 0)

            preview = QLabel()
            preview.setFixedSize(34, 22)

            value = QLineEdit(self.colors.get(key, "#000000"))
            value.setReadOnly(True)

            choose = QPushButton("选择")
            choose.clicked.connect(
                lambda checked=False, k=key, p=preview, v=value:
                self.pick_color(k, p, v)
            )

            hl.addWidget(preview)
            hl.addWidget(value, 1)
            hl.addWidget(choose)

            self.rows[key] = (preview, value)
            self.update_preview(key)
            form.addRow(label, row)

        note = QLabel(
            "深色和浅色主题分别保存；修改当前模式不会覆盖另一套配色。"
            "主题会保存在当前 Windows 用户目录，下次启动自动加载。"
        )
        note.setWordWrap(True)
        layout.addWidget(note)

        buttons = QDialogButtonBox()
        reset = buttons.addButton("恢复当前模式默认色", QDialogButtonBox.ResetRole)
        ok = buttons.addButton("应用并保存", QDialogButtonBox.AcceptRole)
        cancel = buttons.addButton("取消", QDialogButtonBox.RejectRole)
        reset.clicked.connect(self.reset_defaults)
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        layout.addWidget(buttons)

    def pick_color(self, key, preview, value):
        initial = QColor(self.colors.get(key, "#000000"))
        color = QColorDialog.getColor(initial, self, f"选择 {key} 颜色")
        if color.isValid():
            self.colors[key] = color.name()
            value.setText(color.name())
            self.update_preview(key)

    def update_preview(self, key):
        preview, value = self.rows[key]
        color = self.colors.get(key, "#000000")
        preview.setStyleSheet(f"background:{color};border:none;")
        value.setText(color)

    def reset_defaults(self):
        base = DARK if self.parent().theme_name == "dark" else LIGHT
        for key in self.rows:
            self.colors[key] = base.get(key, self.colors.get(key, "#000000"))
            self.update_preview(key)



class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UploadSentinel v1.1")
        self.resize(1520, 940)

        self.theme_name = "dark"
        self.custom_theme_file = Path.home() / ".uploadsentinel_theme.json"
        self.custom_themes = {"dark": None, "light": None}
        self.custom_theme = None
        self.colors = dict(DARK)
        self.load_custom_theme()

        self.results = []
        self.custom_cases = []
        self.disabled_builtin = set()
        self.scan_history = load_history(limit=30)

        self.raw_request_cache = ""
        self.form_fields_cache = ""
        self.headers_cache = ""

        self._build()
        self.apply_theme()
        self.show_page("概览")

    def _build(self):
        root = QWidget()
        self.setCentralWidget(root)
        outer = QHBoxLayout(root)
        outer.setContentsMargins(0,0,0,0)
        outer.setSpacing(0)

        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(188)
        side = QVBoxLayout(self.sidebar)
        side.setContentsMargins(24,28,20,24)

        brand_area = QWidget()
        brand_area.setStyleSheet("background:transparent;border:none;")
        brand_layout = QVBoxLayout(brand_area)
        brand_layout.setContentsMargins(0, 0, 0, 0)
        brand_layout.setSpacing(4)

        brand = QLabel("UploadSentinel")
        brand.setObjectName("brand")
        brand.setStyleSheet("background:transparent;border:none;")
        brand_layout.addWidget(brand)

        sub = QLabel("文件上传安全测试工作台")
        sub.setObjectName("muted")
        sub.setStyleSheet("background:transparent;border:none;")
        brand_layout.addWidget(sub)

        brand_bands = QWidget()
        brand_bands.setFixedHeight(5)
        brand_bands.setMaximumWidth(112)
        brand_bands.setStyleSheet("background:transparent;border:none;")
        band_row = QHBoxLayout(brand_bands)
        band_row.setContentsMargins(0, 0, 0, 0)
        band_row.setSpacing(0)

        brand_band_main = QFrame()
        brand_band_main.setStyleSheet(
            f"background:{self.colors['band1']};border:none;"
        )
        brand_band_sub = QFrame()
        brand_band_sub.setStyleSheet(
            f"background:{self.colors['band2']};border:none;"
        )
        brand_band_dark = QFrame()
        brand_band_dark.setStyleSheet(
            f"background:{self.colors['darkshape']};border:none;"
        )

        band_row.addWidget(brand_band_main, 5)
        band_row.addWidget(brand_band_sub, 2)
        band_row.addWidget(brand_band_dark, 1)
        brand_layout.addWidget(brand_bands)

        side.addWidget(brand_area)
        side.addSpacing(24)

        self.nav = {}
        for name in [
            "概览",
            "扫描器",
            "请求编辑",
            "测试用例",
            "判定规则",
            "测试结果",
            "扫描历史",
            "项目管理",
        ]:
            b = QPushButton(name)
            b.setObjectName("nav")
            b.clicked.connect(lambda checked=False, n=name: self.show_page(n))
            side.addWidget(b)
            self.nav[name] = b

        side.addStretch()

        theme_btn = QPushButton("切换明暗")
        theme_btn.setObjectName("nav")
        theme_btn.clicked.connect(self.toggle_theme)
        side.addWidget(theme_btn)

        custom_theme_btn = QPushButton("自定义配色")
        custom_theme_btn.setObjectName("nav")
        custom_theme_btn.clicked.connect(self.open_theme_editor)
        side.addWidget(custom_theme_btn)

        reset_theme_btn = QPushButton("恢复当前主题")
        reset_theme_btn.setObjectName("nav")
        reset_theme_btn.clicked.connect(self.reset_custom_theme)
        side.addWidget(reset_theme_btn)

        about = QPushButton("关于")
        about.setObjectName("nav")
        about.clicked.connect(self.about)
        side.addWidget(about)

        outer.addWidget(self.sidebar)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0,0,0,0)
        right_layout.setSpacing(0)

        self.topbar = QFrame()
        self.topbar.setObjectName("topbar")
        self.topbar.setFixedHeight(92)
        tb = QHBoxLayout(self.topbar)
        tb.setContentsMargins(34,14,34,14)

        left = QVBoxLayout()
        lab = QLabel("测试目标")
        lab.setObjectName("muted")
        left.addWidget(lab)
        left.setSpacing(6)
        target_row = QHBoxLayout()
        target_row.setSpacing(14)
        self.url = QLineEdit()
        self.url.setPlaceholderText("例如：https://example.com/upload")
        self.url.setMinimumWidth(560)
        self.url.setMinimumHeight(38)
        target_row.addWidget(self.url)
        imp = QPushButton("导入 Burp 请求")
        imp.setMinimumHeight(38)
        imp.clicked.connect(self.import_raw)
        target_row.addWidget(imp)
        left.addLayout(target_row)
        tb.addLayout(left)
        tb.addStretch()

        status_box = QVBoxLayout()
        self.top_status = QLabel("就绪")
        status_box.addWidget(self.top_status, alignment=Qt.AlignRight)
        ver = QLabel("UploadSentinel v1.1")
        ver.setObjectName("muted")
        status_box.addWidget(ver, alignment=Qt.AlignRight)
        tb.addLayout(status_box)

        right_layout.addWidget(self.topbar)

        self.stack = QStackedWidget()
        right_layout.addWidget(self.stack)
        outer.addWidget(right, 1)

        self.pages = {}
        for name in ["概览","扫描器","请求编辑","测试用例","判定规则","测试结果","扫描历史","项目管理"]:
            w = QWidget()
            self.stack.addWidget(w)
            self.pages[name] = w
        self.build_dashboard()
        self.build_scanner()
        self.build_request()
        self.build_cases()
        self.build_rules()
        self.build_results()
        self.build_history()
        self.build_project()

    def validate_page_registry(self):
        required = [
            "概览", "扫描器", "请求编辑", "测试用例",
            "判定规则", "测试结果", "扫描历史", "项目管理"
        ]
        missing = [name for name in required if name not in self.pages]
        if missing:
            raise RuntimeError("页面注册不完整，缺少：" + "、".join(missing))

    def page_layout(self, page, title, subtitle):
        lay = QVBoxLayout(page)
        lay.setContentsMargins(34, 30, 36, 30)
        lay.setSpacing(10)

        t = QLabel(title)
        t.setObjectName("pageTitle")
        lay.addWidget(t)

        s = QLabel(subtitle)
        s.setObjectName("muted")
        lay.addWidget(s)

        lay.addSpacing(10)
        self.add_color_bands(lay, sum(ord(ch) for ch in title) % 3)
        lay.addSpacing(18)
        return lay

    def card(self):
        f = QFrame()
        f.setObjectName("card")
        return f

    def add_color_bands(self, layout, variant=0):
        """Sparse flat bands used as a page-level visual accent."""
        band = QWidget()
        band.setFixedHeight(26 if variant % 2 == 0 else 34)
        row = QHBoxLayout(band)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        widths = [(5, 2, 1), (3, 5, 2), (6, 1, 3)][variant % 3]
        colors = [self.colors["band1"], self.colors["band2"], self.colors["darkshape"]]

        for w, color in zip(widths, colors):
            piece = QFrame()
            piece.setStyleSheet(f"background:{color};border:none;")
            row.addWidget(piece, w)

        layout.addWidget(band)

    def build_dashboard(self):
        # Dashboard uses a semantic status bar instead of the generic decorative band.
        page = self.pages["概览"]
        lay = QVBoxLayout(page)
        lay.setContentsMargins(34, 30, 36, 30)
        lay.setSpacing(10)

        title = QLabel("概览")
        title.setObjectName("pageTitle")
        lay.addWidget(title)

        subtitle = QLabel("查看当前文件上传安全测试任务的整体状态与风险分布。")
        subtitle.setObjectName("muted")
        lay.addWidget(subtitle)
        lay.addSpacing(16)

        # Semantic distribution bar.
        self.dashboard_distribution = QWidget()
        self.dashboard_distribution.setFixedHeight(18)
        self.dashboard_distribution_layout = QHBoxLayout(self.dashboard_distribution)
        self.dashboard_distribution_layout.setContentsMargins(0, 0, 0, 0)
        self.dashboard_distribution_layout.setSpacing(0)

        self.dashboard_segments = {}
        segment_specs = [
            ("high", self.colors["orange"]),     # HIGH_REVIEW
            ("review", self.colors["review"]),   # REVIEW
            ("rejected", self.colors["green"]), # REJECTED
            ("errors", self.colors["red"]),      # ERROR
        ]
        for key, color in segment_specs:
            piece = QFrame()
            piece.setStyleSheet(f"background:{color};border:none;")
            self.dashboard_distribution_layout.addWidget(piece, 1)
            self.dashboard_segments[key] = piece

        lay.addWidget(self.dashboard_distribution)

        # Small semantic legend; no boxes, no borders.
        legend = QHBoxLayout()
        legend.setSpacing(22)
        for label, color in [
            ("重点复核", self.colors["orange"]),
            ("待复核", self.colors["review"]),
            ("已拒绝", self.colors["green"]),
            ("错误", self.colors["red"]),
        ]:
            item = QWidget()
            row = QHBoxLayout(item)
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(7)
            swatch = QFrame()
            swatch.setFixedSize(18, 5)
            swatch.setStyleSheet(f"background:{color};border:none;")
            txt = QLabel(label)
            txt.setObjectName("muted")
            row.addWidget(swatch)
            row.addWidget(txt)
            legend.addWidget(item)
        legend.addStretch()
        lay.addLayout(legend)
        lay.addSpacing(18)

        # Metrics: total is neutral; status metrics use the same exact semantic colors.
        stats = QGridLayout()
        stats.setHorizontalSpacing(34)
        self.stat_labels = {}
        self.stat_bars = {}

        specs = [
            ("total", "测试总数", self.colors["muted"]),
            ("high", "重点复核", self.colors["orange"]),
            ("review", "待复核", self.colors["review"]),
            ("rejected", "已拒绝", self.colors["green"]),
            ("errors", "错误", self.colors["red"]),
        ]

        for i, (key, metric_title, color) in enumerate(specs):
            c = self.card()
            cl = QVBoxLayout(c)
            cl.setContentsMargins(10, 4, 10, 4)

            l1 = QLabel(metric_title)
            l1.setObjectName("muted")
            l2 = QLabel("0")
            l2.setFont(QFont("Microsoft YaHei UI", 16, QFont.DemiBold))

            self.stat_labels[key] = l2
            c.setStyleSheet("background:transparent;border:none;")
            cl.addWidget(l1)
            cl.addWidget(l2)

            bar = QFrame()
            bar.setFixedHeight(4)
            bar.setStyleSheet(f"background:{color};border:none;")
            cl.addWidget(bar)
            self.stat_bars[key] = bar

            stats.addWidget(c, 0, i)

        lay.addLayout(stats)
        lay.addSpacing(18)

        lower = QHBoxLayout()
        lower.setSpacing(42)

        quick = self.card()
        ql = QVBoxLayout(quick)
        ql.setContentsMargins(10, 0, 10, 0)
        ql.addWidget(QLabel("快速开始"))

        for item_text in [
            "1. 在 Burp 中抓取一次正常的文件上传请求。",
            "2. 导入原始请求，或直接填写上传接口地址。",
            "3. 选择需要执行的无害测试用例。",
            "4. 执行扫描，优先关注 HIGH_REVIEW / REVIEW。",
            "5. 查看响应、基线差异和返回地址验证结果。"
        ]:
            ql.addWidget(QLabel(item_text))

        b = QPushButton("打开扫描器")
        b.setObjectName("primary")
        b.clicked.connect(lambda: self.show_page("扫描器"))
        ql.addWidget(b, alignment=Qt.AlignLeft)
        ql.addStretch()

        posture = self.card()
        pl = QVBoxLayout(posture)
        pl.setContentsMargins(10, 0, 10, 0)
        pl.addWidget(QLabel("当前配置"))

        safe = QLabel("SAFE MODE")
        safe.setStyleSheet(f"color:{self.colors['green']};font-weight:600;")
        pl.addWidget(safe)

        for item_text in [
            "• 不包含 WebShell 或命令执行载荷",
            "• 基于正常上传基线进行响应比较",
            "• 支持返回文件地址可达性检查",
            "• 支持 Burp 代理联动工作流",
            "• 支持项目保存与扫描历史"
        ]:
            pl.addWidget(QLabel(item_text))

        pl.addStretch()

        lower.addWidget(quick, 1)
        lower.addWidget(posture, 1)
        lay.addLayout(lower, 1)

    def build_scanner(self):
        lay = self.page_layout(
            self.pages["扫描器"],
            "扫描器",
            "配置并执行授权范围内的文件上传安全测试任务。"
        )

        cfg = self.card()
        form = QGridLayout(cfg)
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(14)

        self.field = QLineEdit("file")
        self.method = QComboBox()
        self.method.addItems(["POST", "PUT", "PATCH"])

        self.scheme = QComboBox()
        self.scheme.addItems(["https", "http"])

        self.delay = QDoubleSpinBox()
        self.delay.setRange(0.0, 60.0)
        self.delay.setDecimals(2)
        self.delay.setSingleStep(0.05)
        self.delay.setValue(0.25)

        self.timeout = QSpinBox()
        self.timeout.setRange(1, 300)
        self.timeout.setValue(15)

        self.cluster_threshold = QDoubleSpinBox()
        self.cluster_threshold.setRange(0.50, 1.00)
        self.cluster_threshold.setDecimals(2)
        self.cluster_threshold.setSingleStep(0.01)
        self.cluster_threshold.setValue(0.92)

        self.proxy = QLineEdit()
        self.proxy.setPlaceholderText("例如：http://127.0.0.1:8080")

        self.raw_mode = QCheckBox("使用导入的原始请求")
        self.ref_check = QCheckBox("验证返回的文件地址")
        self.ref_check.setChecked(True)
        self.insecure = QCheckBox("关闭 TLS 证书校验")
        self.persist_history = QCheckBox("将扫描历史持久化到磁盘")
        self.persist_history.setChecked(False)

        self.scan_preset = QComboBox()
        self.scan_preset.addItems(["温和", "标准", "快速"])
        self.scan_preset.setCurrentText("标准")
        self.scan_preset.currentTextChanged.connect(self.apply_scan_preset)
        self.test_level = QComboBox()
        self.test_level.addItems(["低档（基础）", "中档（推荐）", "高档（全面）"])
        self.test_level.setCurrentText("中档（推荐）")
        self.test_level.currentTextChanged.connect(self.update_level_summary)
        self.level_summary = QLabel("")
        self.level_summary.setObjectName("muted")

        form.addWidget(QLabel("文件字段"), 0, 0)
        form.addWidget(self.field, 0, 1)

        form.addWidget(QLabel("请求方法"), 0, 2)
        form.addWidget(self.method, 0, 3)

        form.addWidget(QLabel("协议"), 0, 4)
        form.addWidget(self.scheme, 0, 5)

        form.addWidget(QLabel("请求间隔（秒）"), 1, 0)
        form.addWidget(self.delay, 1, 1)

        form.addWidget(QLabel("超时（秒）"), 1, 2)
        form.addWidget(self.timeout, 1, 3)

        form.addWidget(QLabel("聚类阈值"), 1, 4)
        form.addWidget(self.cluster_threshold, 1, 5)

        form.addWidget(QLabel("扫描速度"), 2, 0)
        form.addWidget(self.scan_preset, 2, 1)
        form.addWidget(QLabel("测试档位"), 2, 2)
        form.addWidget(self.test_level, 2, 3)
        form.addWidget(self.level_summary, 2, 4, 1, 2)
        form.addWidget(QLabel("代理地址"), 3, 0)
        form.addWidget(self.proxy, 3, 1, 1, 5)

        form.addWidget(self.raw_mode, 4, 0, 1, 2)
        form.addWidget(self.ref_check, 4, 2, 1, 2)
        form.addWidget(self.insecure, 4, 4, 1, 2)
        form.addWidget(self.persist_history, 5, 0, 1, 3)

        action_row = QHBoxLayout()
        self.run_btn = QPushButton("开始安全测试")
        self.run_btn.setObjectName("primary")
        self.run_btn.clicked.connect(self.start_scan)

        imp = QPushButton("导入请求")
        imp.clicked.connect(self.import_raw)

        view = QPushButton("查看结果")
        view.clicked.connect(lambda: self.show_page("测试结果"))

        action_row.addWidget(self.run_btn)
        action_row.addWidget(imp)
        action_row.addWidget(view)
        action_row.addStretch()
        form.addLayout(action_row, 6, 0, 1, 6)

        lay.addWidget(cfg)

        prog_card = self.card()
        pv = QVBoxLayout(prog_card)
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.scan_status = QLabel("就绪")
        self.scan_status.setObjectName("muted")
        pv.addWidget(self.progress)
        pv.addWidget(self.scan_status)
        lay.addWidget(prog_card)

        log_card = self.card()
        lv = QVBoxLayout(log_card)
        lv.addWidget(QLabel("实时日志"))
        self.live_log = QPlainTextEdit()
        self.live_log.setReadOnly(True)
        lv.addWidget(self.live_log)
        lay.addWidget(log_card, 1)
        self.update_level_summary()

    def current_test_level(self):
        value = self.test_level.currentText() if hasattr(self, "test_level") else "中档（推荐）"
        if value.startswith("低"):
            return "low"
        if value.startswith("高"):
            return "high"
        return "medium"

    def update_level_summary(self, *args):
        from uploadsentinel import filter_cases_by_level
        level = self.current_test_level()
        cases = filter_cases_by_level(build_safe_cases(), level)
        counts = {k: sum(c.level == k for c in cases) for k in ("low","medium","high")}
        if level == "low":
            label = f"共 {len(cases)} 项 · 低 {counts['low']}"
        elif level == "medium":
            label = f"共 {len(cases)} 项 · 低 {counts['low']} + 中 {counts['medium']}"
        else:
            label = f"共 {len(cases)} 项 · 低 {counts['low']} + 中 {counts['medium']} + 高 {counts['high']}"
        if hasattr(self, "level_summary"):
            self.level_summary.setText(label)

    def apply_scan_preset(self, name):
        """Apply conservative request-rate presets; all use benign test content."""
        presets = {
            "温和": {
                "delay": 1.00,
                "timeout": 20,
                "cluster": 0.92,
                "ref_check": False,
            },
            "标准": {
                "delay": 0.25,
                "timeout": 15,
                "cluster": 0.92,
                "ref_check": True,
            },
            "快速": {
                "delay": 0.05,
                "timeout": 10,
                "cluster": 0.90,
                "ref_check": True,
            },
        }
        p = presets.get(name, presets["标准"])
        self.delay.setValue(p["delay"])
        self.timeout.setValue(p["timeout"])
        self.cluster_threshold.setValue(p["cluster"])
        self.ref_check.setChecked(p["ref_check"])
        self.top_status.setText(f"已应用“{name}”扫描预设")

    def build_request(self):
        lay = self.page_layout(self.pages["请求编辑"], "请求编辑",
                               "编辑或拖入原始 HTTP 请求，并管理附加表单参数与请求头。")
        tools = QHBoxLayout()
        preflight = QPushButton("预检原始请求")
        preflight.setObjectName("primary")
        preflight.clicked.connect(self.preflight_raw_request)
        tools.addWidget(preflight)
        tools.addStretch()
        lay.addLayout(tools)

        tabs = QTabWidget()

        self.raw = DropTextEdit()
        self.raw.setPlaceholderText("将 Burp 原始请求粘贴到这里，或直接拖入 .txt 请求文件。")
        self.raw.fileDropped.connect(self.load_raw_file)
        self.data_text = QPlainTextEdit()
        self.data_text.setPlaceholderText("KEY=VALUE\nKEY2=VALUE2")
        self.header_text = QPlainTextEdit()
        self.header_text.setPlaceholderText("X-Test=1\nAuthorization=Bearer ...")

        tabs.addTab(self.raw, "原始 HTTP")
        tabs.addTab(self.data_text, "表单参数")
        tabs.addTab(self.header_text, "请求头")
        lay.addWidget(tabs,1)

    def preflight_raw_request(self):
        """
        Parse the raw request locally without sending any network request.
        """
        raw_text = self.raw.toPlainText().strip()
        if not raw_text:
            QMessageBox.information(self, "请求预检", "请先粘贴或导入一条原始 HTTP 请求。")
            return

        try:
            from uploadsentinel import parse_raw_request, extract_form_fields_from_multipart
            raw = parse_raw_request(raw_text)
            fields, detected_file_field = extract_form_fields_from_multipart(
                raw,
                self.field.text().strip() or "file"
            )
            inferred = raw.infer_url(self.scheme.currentText())

            header_lines = [
                f"请求方法：{raw.method}",
                f"目标地址：{inferred}",
                f"Host：{raw.host or '未识别'}",
                f"文件字段：{detected_file_field}",
                f"普通表单字段：{len(fields)} 个",
            ]
            if fields:
                header_lines.append("")
                header_lines.append("表单字段：")
                for k, v in list(fields.items())[:20]:
                    display = v if len(v) <= 100 else v[:100] + "..."
                    header_lines.append(f"  {k} = {display}")

            QMessageBox.information(
                self,
                "请求预检结果",
                "\n".join(header_lines)
            )
        except Exception as e:
            QMessageBox.critical(self, "请求预检失败", str(e))

    def build_cases(self):
        lay = self.page_layout(self.pages["测试用例"], "测试用例",
                               "选择内置测试项，或添加自定义无害文本测试用例。")

        bar = QHBoxLayout()
        self.case_search = QLineEdit()
        self.case_search.setPlaceholderText("搜索用例名称、文件名或说明")
        self.case_search.textChanged.connect(self.populate_cases)
        self.case_category = QComboBox()
        self.case_category.addItems(["全部分类","baseline","filename","mime","type","content","custom"])
        self.case_category.currentTextChanged.connect(self.populate_cases)
        self.case_level_filter = QComboBox()
        self.case_level_filter.addItems(["全部档位", "低档", "中档", "高档"])
        self.case_level_filter.currentTextChanged.connect(self.populate_cases)
        add = QPushButton("添加自定义用例"); add.setObjectName("primary"); add.clicked.connect(self.add_custom_case)
        ena = QPushButton("全部启用"); ena.clicked.connect(lambda:self.set_all_cases(True))
        dis = QPushButton("全部禁用"); dis.clicked.connect(lambda:self.set_all_cases(False))
        bar.addWidget(add); bar.addWidget(ena); bar.addWidget(dis)
        bar.addStretch()
        bar.addWidget(self.case_search, 1)
        bar.addWidget(self.case_category)
        bar.addWidget(self.case_level_filter)
        lay.addLayout(bar)

        self.case_table = QTableWidget(0,7)
        self.case_table.setHorizontalHeaderLabels(["启用","档位","分类","用例名称","文件名","MIME","说明"])
        self.case_table.setAlternatingRowColors(True)
        self.case_table.verticalHeader().setDefaultSectionSize(34)
        self.case_table.verticalHeader().setVisible(False)
        self.case_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.case_table.cellDoubleClicked.connect(self.toggle_case)
        lay.addWidget(self.case_table,1)
        self.populate_cases()

    def build_rules(self):
        lay = self.page_layout(
            self.pages["判定规则"], "Verdict Rules",
            "Add optional response rules for triage. These rules do not generate payloads."
        )

        info = self.card()
        iv = QVBoxLayout(info)
        note = QLabel(
            "Reject rules are evaluated before success rules. Enter one regular expression per line. "
            "Invalid regex patterns are highlighted when you validate."
        )
        note.setWordWrap(True)
        note.setObjectName("muted")
        iv.addWidget(note)
        lay.addWidget(info)

        split = QHBoxLayout()

        left = self.card()
        lv = QVBoxLayout(left)
        lv.addWidget(QLabel("Success response regex"))
        self.success_regex = QPlainTextEdit()
        self.success_regex.setPlaceholderText('e.g.\\n"success"\\s*:\\s*true\\n上传成功')
        lv.addWidget(self.success_regex)
        lv.addWidget(QLabel("Success HTTP status (comma-separated)"))
        self.success_status = QLineEdit()
        self.success_status.setPlaceholderText("200,201")
        lv.addWidget(self.success_status)

        right = self.card()
        rv = QVBoxLayout(right)
        rv.addWidget(QLabel("Reject response regex"))
        self.reject_regex = QPlainTextEdit()
        self.reject_regex.setPlaceholderText("e.g.\\n文件类型不支持\\nnot allowed")
        rv.addWidget(self.reject_regex)
        rv.addWidget(QLabel("Reject HTTP status (comma-separated)"))
        self.reject_status = QLineEdit()
        self.reject_status.setPlaceholderText("400,415")
        rv.addWidget(self.reject_status)

        split.addWidget(left,1)
        split.addWidget(right,1)
        lay.addLayout(split,1)

        row = QHBoxLayout()
        validate = QPushButton("Validate Rules")
        validate.setObjectName("primary")
        validate.clicked.connect(self.validate_rules)
        clear = QPushButton("Clear Rules")
        clear.clicked.connect(self.clear_rules_ui)
        row.addWidget(validate)
        row.addWidget(clear)
        row.addStretch()
        lay.addLayout(row)

    def parse_status_list(self, text):
        out = []
        for token in (text or "").replace(";", ",").split(","):
            token = token.strip()
            if not token:
                continue
            value = int(token)
            if value < 100 or value > 599:
                raise ValueError(f"Invalid HTTP status: {value}")
            out.append(value)
        return out

    def current_rules(self):
        import re
        success = [x.strip() for x in self.success_regex.toPlainText().splitlines() if x.strip()]
        reject = [x.strip() for x in self.reject_regex.toPlainText().splitlines() if x.strip()]
        for pattern in success + reject:
            re.compile(pattern, re.I | re.M)
        return RuleConfig(
            success_regex=success,
            reject_regex=reject,
            success_status=self.parse_status_list(self.success_status.text()),
            reject_status=self.parse_status_list(self.reject_status.text()),
        )

    def validate_rules(self):
        import re
        try:
            rules = self.current_rules()
            for p in rules.success_regex + rules.reject_regex:
                re.compile(p, re.I | re.M)
            QMessageBox.information(self, "Rules valid", "All verdict rules are valid.")
        except Exception as e:
            QMessageBox.critical(self, "Invalid rule", str(e))

    def clear_rules_ui(self):
        self.success_regex.clear()
        self.reject_regex.clear()
        self.success_status.clear()
        self.reject_status.clear()

    def build_results(self):
        lay = self.page_layout(self.pages["测试结果"], "测试结果",
                               "筛选疑似接受的响应，并查看基线差异、返回地址与人工复核状态。")

        top = QHBoxLayout()
        top.addWidget(QLabel("筛选"))
        self.filter_box = QComboBox()
        self.filter_box.addItems(["ALL","HIGH_REVIEW","REVIEW","UNKNOWN","REJECTED","BLOCKED","ERROR","BASELINE"])
        self.filter_box.currentTextChanged.connect(self.refresh_results)
        top.addWidget(self.filter_box)
        top.addStretch()
        confirmed = QPushButton("Mark Confirmed"); confirmed.clicked.connect(lambda:self.set_manual_state("CONFIRMED"))
        falsep = QPushButton("Mark False Positive"); falsep.clicked.connect(lambda:self.set_manual_state("FALSE_POSITIVE"))
        resetm = QPushButton("Reset Review"); resetm.clicked.connect(lambda:self.set_manual_state("UNREVIEWED"))
        top.addWidget(confirmed); top.addWidget(falsep); top.addWidget(resetm)
        exp = QPushButton("导出报告"); exp.clicked.connect(self.export_results)
        top.addWidget(exp)
        lay.addLayout(top)

        self.result_summary = QLabel("暂无结果")
        self.result_summary.setObjectName("muted")
        lay.addWidget(self.result_summary)

        split = QSplitter(Qt.Vertical)

        self.result_table = QTableWidget(0,13)
        self.result_table.setHorizontalHeaderLabels(
            ["Verdict","Score","聚类","Manual","Category","Case","Filename","MIME","HTTP","ms","Bytes","Similarity","Notes"]
        )
        self.result_table.setAlternatingRowColors(True)
        self.result_table.verticalHeader().setDefaultSectionSize(34)
        self.result_table.verticalHeader().setVisible(False)
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.result_table.horizontalHeader().setStretchLastSection(True)
        self.result_table.itemSelectionChanged.connect(self.result_selected)
        split.addWidget(self.result_table)

        detail_tabs = QTabWidget()
        self.resp_text = QPlainTextEdit(); self.resp_text.setReadOnly(True)
        self.diff_text = QPlainTextEdit(); self.diff_text.setReadOnly(True)
        self.url_text = QPlainTextEdit(); self.url_text.setReadOnly(True)
        detail_tabs.addTab(self.resp_text,"响应内容")
        detail_tabs.addTab(self.diff_text,"基线差异")
        detail_tabs.addTab(self.url_text,"返回地址")
        split.addWidget(detail_tabs)
        split.setSizes([470,260])
        lay.addWidget(split,1)

    def build_history(self):
        lay = self.page_layout(self.pages["扫描历史"], "扫描历史",
                               "查看当前会话及可选持久化保存的历史扫描任务。")
        privacy = QLabel("Disk persistence is optional and off by default because response previews may contain business data.")
        privacy.setObjectName("muted")
        privacy.setWordWrap(True)
        lay.addWidget(privacy)
        row = QHBoxLayout()
        clear_btn = QPushButton("清空历史")
        clear_btn.clicked.connect(self.clear_history_ui)
        row.addStretch(); row.addWidget(clear_btn)
        lay.addLayout(row)
        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self.open_history_item)
        lay.addWidget(self.history_list,1)

    def build_project(self):
        lay = self.page_layout(self.pages["项目管理"], "项目管理",
                               "保存或恢复测试目标、请求、规则和测试用例配置。")

        c = self.card()
        v = QVBoxLayout(c)
        row = QHBoxLayout()
        s = QPushButton("保存项目"); s.setObjectName("primary"); s.clicked.connect(self.save_project_ui)
        o = QPushButton("打开项目"); o.clicked.connect(self.open_project)
        e = QPushButton("导出结果"); e.clicked.connect(self.export_results)
        row.addWidget(s); row.addWidget(o); row.addWidget(e); row.addStretch()
        v.addLayout(row)
        for t in [
            "Saved: target URL, request, fields, headers, proxy and scanner options",
            "Saved: enabled / disabled built-in cases",
            "Saved: custom benign cases",
            "Results are exported separately as JSON / CSV / HTML"
        ]:
            lab = QLabel("• "+t); lab.setObjectName("muted"); v.addWidget(lab)
        lay.addWidget(c)
        lay.addStretch()

    def load_custom_theme(self):
        if not hasattr(self, "custom_theme_file"):
            self.custom_theme_file = Path.home() / ".uploadsentinel_theme.json"
        if not hasattr(self, "custom_themes"):
            self.custom_themes = {"dark": None, "light": None}

        try:
            if not self.custom_theme_file.exists():
                self.custom_theme = None
                self.colors = dict(DARK if self.theme_name == "dark" else LIGHT)
                return

            data = json.loads(
                self.custom_theme_file.read_text(encoding="utf-8")
            )
            if not isinstance(data, dict):
                raise ValueError("主题文件格式不是 JSON 对象")

            if "dark" in data or "light" in data:
                self.custom_themes["dark"] = data.get("dark")
                self.custom_themes["light"] = data.get("light")
            else:
                accent_keys = ("band1", "band2", "band3", "darkshape")
                migrated = {k: data[k] for k in accent_keys if k in data}
                self.custom_themes["dark"] = dict(migrated) if migrated else None
                self.custom_themes["light"] = dict(migrated) if migrated else None

            active = self.custom_themes.get(self.theme_name)
            self.custom_theme = active
            self.colors = self.derive_theme(
                dict(DARK if self.theme_name == "dark" else LIGHT),
                active or {}
            )
        except Exception as e:
            self.custom_theme = None
            self.custom_themes = {"dark": None, "light": None}
            self.colors = dict(DARK if self.theme_name == "dark" else LIGHT)
            print("[UploadSentinel] theme load failed:", e)

    def derive_theme(self, base, custom):
        """
        Apply the palette for the current mode only.
        A dark custom palette never overrides the light palette and vice versa.
        """
        custom = custom or {}
        for key in ("bg","text","muted","entry","band1","band2","band3","darkshape"):
            if key in custom and isinstance(custom[key], str):
                base[key] = custom[key]

        base["panel"] = base["bg"]
        base["card"] = base["bg"]
        base["panel2"] = base["entry"]
        base["accent"] = base["band1"]
        base["accent2"] = base["band2"]
        base["green"] = base["band1"]
        base["orange"] = base["band2"]
        base["purple"] = base["band3"]
        base["review"] = base["band3"]
        return base
    def open_theme_editor(self):
        if not hasattr(self, "custom_theme_file"):
            self.custom_theme_file = Path.home() / ".uploadsentinel_theme.json"
        if not hasattr(self, "custom_themes"):
            self.custom_themes = {"dark": None, "light": None}

        dialog = ThemeDialog(self.colors, self)
        if dialog.exec() == QDialog.Accepted:
            palette = {
                key: dialog.colors[key]
                for key in (
                    "bg", "text", "muted", "entry",
                    "band1", "band2", "band3", "darkshape"
                )
            }

            self.custom_themes[self.theme_name] = palette
            self.custom_theme = palette
            self.colors = self.derive_theme(
                dict(DARK if self.theme_name == "dark" else LIGHT),
                palette
            )

            try:
                self.custom_theme_file.write_text(
                    json.dumps(
                        self.custom_themes,
                        ensure_ascii=False,
                        indent=2
                    ),
                    encoding="utf-8"
                )
            except Exception as e:
                QMessageBox.warning(self, "主题保存失败", str(e))
                return

            self.apply_theme()
            self.refresh_dashboard()
            self.refresh_results()
            self.top_status.setText("主题已保存")

    def reset_custom_theme(self):
        if not hasattr(self, "custom_theme_file"):
            self.custom_theme_file = Path.home() / ".uploadsentinel_theme.json"
        if not hasattr(self, "custom_themes"):
            self.custom_themes = {"dark": None, "light": None}

        self.custom_themes[self.theme_name] = None
        self.custom_theme = None

        try:
            if any(self.custom_themes.values()):
                self.custom_theme_file.write_text(
                    json.dumps(
                        self.custom_themes,
                        ensure_ascii=False,
                        indent=2
                    ),
                    encoding="utf-8"
                )
            elif self.custom_theme_file.exists():
                self.custom_theme_file.unlink()
        except Exception as e:
            QMessageBox.warning(self, "主题重置失败", str(e))

        self.colors = dict(DARK if self.theme_name == "dark" else LIGHT)
        self.apply_theme()
        self.refresh_dashboard()
        self.refresh_results()
        self.top_status.setText("已恢复当前主题默认配色")

    def apply_theme(self):
        self.setStyleSheet(qss(self.colors))

    def toggle_theme(self):
        if not hasattr(self, "custom_themes"):
            self.custom_themes = {"dark": None, "light": None}

        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        base = dict(LIGHT if self.theme_name == "light" else DARK)

        active = self.custom_themes.get(self.theme_name)
        self.custom_theme = active
        self.colors = self.derive_theme(base, active or {})

        self.apply_theme()
        self.refresh_dashboard()
        self.refresh_results()
        self.top_status.setText(
            "已切换为浅色主题"
            if self.theme_name == "light"
            else "已切换为深色主题"
        )

    def show_page(self, name):
        if name not in self.pages:
            QMessageBox.critical(
                self,
                "页面错误",
                f"未找到页面：{name}\n\n请检查程序页面注册配置。"
            )
            return

        self.stack.setCurrentWidget(self.pages[name])

        for n, b in self.nav.items():
            b.setObjectName("navActive" if n == name else "nav")
            b.style().unpolish(b)
            b.style().polish(b)

        if name == "概览":
            self.refresh_dashboard()
        elif name == "测试结果":
            self.refresh_results()
        elif name == "测试用例":
            self.populate_cases()
        elif name == "扫描历史":
            self.refresh_history()

    def refresh_dashboard_palette(self):
        if not hasattr(self, "stat_bars"):
            return
        color_map = {
            "total": self.colors["muted"],
            "high": self.colors["orange"],
            "review": self.colors["review"],
            "rejected": self.colors["green"],
            "errors": self.colors["red"],
        }
        for key, bar in self.stat_bars.items():
            bar.setStyleSheet(
                f"background:{color_map.get(key, self.colors['muted'])};border:none;"
            )

    def refresh_dashboard(self):
        self.refresh_dashboard_palette()
        total = len(self.results)
        high = sum(r.verdict == "HIGH_REVIEW" for r in self.results)
        review = sum(r.verdict == "REVIEW" for r in self.results)
        rejected = sum(r.verdict == "REJECTED" for r in self.results)
        errors = sum(r.verdict == "ERROR" for r in self.results)

        stats = {
            "total": total,
            "high": high,
            "review": review,
            "rejected": rejected,
            "errors": errors,
        }

        for key, value in stats.items():
            if key in self.stat_labels:
                self.stat_labels[key].setText(str(value))

        # Distribution excludes total because total is not a status category.
        status_counts = {
            "high": high,
            "review": review,
            "rejected": rejected,
            "errors": errors,
        }
        status_total = sum(status_counts.values())

        if hasattr(self, "dashboard_distribution_layout"):
            if status_total == 0:
                # No scan yet: show a neutral single-tone bar rather than fake proportions.
                for key, segment in self.dashboard_segments.items():
                    segment.setVisible(key == "review")
                    self.dashboard_distribution_layout.setStretch(
                        self.dashboard_distribution_layout.indexOf(segment),
                        1 if key == "review" else 0
                    )
                neutral = self.dashboard_segments["review"]
                neutral.setStyleSheet(
                    f"background:{self.colors['entry']};border:none;"
                )
            else:
                color_map = {
                    "high": self.colors["orange"],
                    "review": self.colors["review"],
                    "rejected": self.colors["green"],
                    "errors": self.colors["red"],
                }
                for key, segment in self.dashboard_segments.items():
                    count = status_counts[key]
                    segment.setVisible(count > 0)
                    segment.setStyleSheet(
                        f"background:{color_map[key]};border:none;"
                    )
                    index = self.dashboard_distribution_layout.indexOf(segment)
                    self.dashboard_distribution_layout.setStretch(
                        index,
                        max(count, 0)
                    )
    def parse_lines(self, widget):
        out={}
        for line in widget.toPlainText().splitlines():
            line=line.strip()
            if not line or line.startswith("#"): continue
            if "=" not in line: raise ValueError("Expected KEY=VALUE: "+line)
            k,v=line.split("=",1); out[k.strip()]=v.strip()
        return out

    def selected_cases(self):
        base=build_safe_cases()
        for c in base:
            c.enabled = c.name not in self.disabled_builtin
        return base + self.custom_cases

    def populate_cases(self, *args):
        if not hasattr(self, "case_table"):
            return
        cases = self.selected_cases()
        query = self.case_search.text().strip().lower() if hasattr(self, "case_search") else ""
        category = self.case_category.currentText() if hasattr(self, "case_category") else "全部分类"
        level_filter = self.case_level_filter.currentText() if hasattr(self, "case_level_filter") else "全部档位"
        filter_map = {"低档":"low","中档":"medium","高档":"high"}
        level_cn = {"low":"低","medium":"中","high":"高"}

        visible = []
        for source_index, c in enumerate(cases):
            if category != "全部分类" and c.category != category:
                continue
            if level_filter != "全部档位" and c.level != filter_map.get(level_filter):
                continue
            haystack = " ".join([c.level,c.category,c.name,c.filename,c.content_type,c.description]).lower()
            if query and query not in haystack:
                continue
            visible.append((source_index,c))

        self.case_table.setRowCount(len(visible))
        self.case_table.setProperty("sourceRows",[i for i,_ in visible])
        for r,(source_index,c) in enumerate(visible):
            vals = ["是" if c.enabled else "否",level_cn.get(c.level,c.level),c.category,c.name,c.filename,c.content_type,c.description]
            for col,val in enumerate(vals):
                item=QTableWidgetItem(str(val))
                item.setData(Qt.UserRole,source_index)
                if col in (0,1):
                    item.setTextAlignment(Qt.AlignCenter)
                self.case_table.setItem(r,col,item)

    def toggle_case(self, row, col):
        source_rows = self.case_table.property("sourceRows") or []
        if row < 0 or row >= len(source_rows):
            return
        source_index = source_rows[row]

        base_len = len(build_safe_cases())
        if source_index < base_len:
            name = build_safe_cases()[source_index].name
            if name in self.disabled_builtin:
                self.disabled_builtin.remove(name)
            else:
                self.disabled_builtin.add(name)
        else:
            custom_index = source_index - base_len
            if 0 <= custom_index < len(self.custom_cases):
                c = self.custom_cases[custom_index]
                c.enabled = not c.enabled

        self.populate_cases()
    def set_all_cases(self,state):
        self.disabled_builtin=set() if state else {c.name for c in build_safe_cases()}
        for c in self.custom_cases:c.enabled=state
        self.populate_cases()

    def add_custom_case(self):
        d = CustomCaseDialog(self)
        if d.exec() == QDialog.Accepted:
            level_text = d.level.currentText()
            level = "low" if level_text.startswith("低") else "high" if level_text.startswith("高") else "medium"
            self.custom_cases.append(custom_case_from_text(
                d.name.text().strip() or "custom_case",
                "custom",
                d.filename.text().strip() or "custom.txt",
                d.mime.text().strip() or "text/plain",
                d.content.toPlainText(),
                level
            ))
            self.populate_cases()
            self.update_level_summary()

    def import_raw(self):
        p,_=QFileDialog.getOpenFileName(self,"导入原始 HTTP 请求","","Text files (*.txt);;All files (*)")
        if p:self.load_raw_file(p)

    def load_raw_file(self,path):
        try:
            text=Path(path).read_text(encoding="utf-8",errors="replace")
            self.raw.setPlainText(text)
            self.raw_mode.setChecked(True)
            self.top_status.setText("Raw request imported")
            self.show_page("请求编辑")
        except Exception as e:
            QMessageBox.critical(self,"导入失败",str(e))

    def build_runtime_scanner(self):
        delay=float(self.delay.value())
        if self.raw_mode.isChecked():
            raw=self.raw.toPlainText().strip()
            if not raw: raise ValueError("Raw request mode is enabled but request is empty.")
            return Scanner.from_raw_request(
                raw,
                scheme=self.scheme.currentText(),
                file_field_hint=self.field.text().strip() or "file",
                proxy=self.proxy.text().strip() or None,
                timeout=self.timeout.value(),
                verify_tls=not self.insecure.isChecked(),
                delay=delay,
                verify_returned_refs=self.ref_check.isChecked(),
                rules=self.current_rules(),
                cluster_threshold=self.cluster_threshold.value()
            )
        if not self.url.text().strip():
            raise ValueError("Target URL is required.")
        return Scanner(
            self.url.text().strip(),
            self.field.text().strip() or "file",
            self.method.currentText(),
            self.parse_lines(self.data_text),
            self.parse_lines(self.header_text),
            {},
            self.proxy.text().strip() or None,
            self.timeout.value(),
            not self.insecure.isChecked(),
            True,
            delay,
            self.ref_check.isChecked(),
            self.current_rules(),
            self.cluster_threshold.value()
        )

    def start_scan(self):
        try:
            scanner=self.build_runtime_scanner()
        except Exception as e:
            QMessageBox.critical(self,"输入错误",str(e)); return

        from uploadsentinel import filter_cases_by_level
        cases=[c for c in filter_cases_by_level(self.selected_cases(), self.current_test_level()) if c.enabled]
        if not cases:
            QMessageBox.information(self,"没有可执行用例","请至少启用一个测试用例。"); return

        self.run_btn.setEnabled(False)
        self.progress.setValue(0)
        self.scan_status.setText("扫描中...")
        self.live_log.clear()
        self.top_status.setText("正在扫描")

        self.thread=QThread()
        self.worker=Worker(scanner,cases)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.failed.connect(self.on_failed)
        self.worker.finished.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)
        self.thread.start()
        self.scanner=scanner

    def on_progress(self,i,n,r):
        self.progress.setMaximum(n); self.progress.setValue(i)
        self.scan_status.setText(f"{i}/{n} · {r.case}")
        self.top_status.setText(f"Scanning {i}/{n}")
        self.live_log.appendPlainText(
            f"[{i:02}/{n:02}] {r.verdict:11} score={r.score:3} HTTP={r.status_code:<3} "
            f"sim={r.similarity_to_baseline:.2f} {r.case}"
        )

    def on_finished(self,results):
        self.results=list(results)
        self.run_btn.setEnabled(True)
        needs=sum(1 for r in self.results if r.verdict in ("HIGH_REVIEW","REVIEW"))
        self.scan_status.setText(f"Done · {len(self.results)} cases · {needs} need review")
        self.top_status.setText("扫描完成")
        entry = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "target": getattr(self.scanner,"url",""),
            "count": len(self.results),
            "review": needs,
            "results": self.results
        }
        self.scan_history.append(entry)
        self.scan_history = self.scan_history[-30:]
        if self.persist_history.isChecked():
            try:
                append_history(entry, limit=30)
            except Exception as e:
                self.live_log.appendPlainText(f"[history warning] {e}")
        self.refresh_results()
        self.refresh_dashboard()
        self.refresh_history()

    def on_failed(self,msg):
        self.run_btn.setEnabled(True)
        self.scan_status.setText("Failed")
        self.top_status.setText("扫描失败")
        QMessageBox.critical(self,"扫描失败",msg)

    def refresh_results(self):
        if not hasattr(self,"result_table"): return
        if hasattr(self, "result_summary"):
            total = len(self.results)
            high = sum(r.verdict == "HIGH_REVIEW" for r in self.results)
            review = sum(r.verdict == "REVIEW" for r in self.results)
            rejected = sum(r.verdict == "REJECTED" for r in self.results)
            clusters = len({getattr(r, "cluster_id", 0) for r in self.results if getattr(r, "cluster_id", 0)})
            self.result_summary.setText(
                f"总计 {total} 条 · 重点复核 {high} · 复核 {review} · 已拒绝 {rejected} · 聚类 {clusters}"
            )
        filt=self.filter_box.currentText()
        rows=[(i,r) for i,r in enumerate(self.results) if filt=="ALL" or r.verdict==filt]
        self.result_table.setRowCount(len(rows))
        self.result_table.setProperty("sourceRows",[i for i,_ in rows])
        for rr,(src_idx,r) in enumerate(rows):
            vals=[r.verdict,r.score,r.cluster_id,r.manual_state,r.category,r.case,r.filename,r.content_type,
                  r.status_code,r.elapsed_ms,r.response_bytes,f"{r.similarity_to_baseline:.2f}",r.notes]
            for c,val in enumerate(vals):
                item=QTableWidgetItem(str(val))
                if c in (1,2,8,9,10,11): item.setTextAlignment(Qt.AlignCenter)
                if c==0:
                    if r.verdict=="HIGH_REVIEW": item.setForeground(QColor(self.colors["orange"]))
                    elif r.verdict=="REJECTED": item.setForeground(QColor(self.colors["green"]))
                    elif r.verdict=="ERROR": item.setForeground(QColor(self.colors["red"]))
                    elif r.verdict=="REVIEW": item.setForeground(QColor(self.colors["purple"]))
                self.result_table.setItem(rr,c,item)

    def result_selected(self):
        row=self.result_table.currentRow()
        if row<0:return
        src=self.result_table.property("sourceRows") or []
        if row>=len(src):return
        r=self.results[src[row]]
        self.resp_text.setPlainText(r.response_preview)
        self.diff_text.setPlainText(r.diff_preview)
        lines=list(r.possible_refs)
        if r.ref_checks:
            lines.append("\n--- Reachability checks ---")
            for x in r.ref_checks:
                prefix = "SKIP" if x.get("skipped") else (x.get("method","") or "CHECK")
                lines.append(f"{prefix} {x.get('status',0)} {x.get('content_type','')} {x.get('url','')}")
                if x.get("error"): lines.append("  error: "+x["error"])
        if r.matched_rules:
            lines.append("\n--- Matched verdict rules ---")
            lines.extend(r.matched_rules)
        self.url_text.setPlainText("\n".join(lines))

    def set_manual_state(self, state):
        row = self.result_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select result", "Select a result row first.")
            return
        src = self.result_table.property("sourceRows") or []
        if row >= len(src):
            return
        self.results[src[row]].manual_state = state
        if self.persist_history.isChecked():
            try:
                save_history(self.scan_history, limit=30)
            except Exception:
                pass
        self.refresh_results()

    def refresh_history(self):
        self.history_list.clear()
        for idx,h in enumerate(reversed(self.scan_history)):
            item=QListWidgetItem(
                f"{h['time']}   {h['target']}   · {h['count']} cases · {h['review']} need review"
            )
            item.setData(Qt.UserRole,len(self.scan_history)-1-idx)
            self.history_list.addItem(item)

    def clear_history_ui(self):
        answer = QMessageBox.question(self, "Clear history", "Delete persistent scan history?")
        if answer == QMessageBox.Yes:
            self.scan_history = []
            try:
                clear_history()
            except Exception as e:
                QMessageBox.critical(self, "Clear history failed", str(e))
            self.refresh_history()

    def open_history_item(self,item):
        idx=item.data(Qt.UserRole)
        if isinstance(idx,int) and 0<=idx<len(self.scan_history):
            self.results=list(self.scan_history[idx]["results"])
            self.show_page("测试结果")

    def save_project_ui(self):
        p,_=QFileDialog.getSaveFileName(self,"保存项目","","UploadSentinel Project (*.usproj)")
        if not p:return
        if not p.endswith(".usproj"): p += ".usproj"
        cfg={
            "url":self.url.text(),
            "field":self.field.text(),
            "method":self.method.currentText(),
            "scheme":self.scheme.currentText(),
            "proxy":self.proxy.text(),
            "insecure":self.insecure.isChecked(),
            "ref_check":self.ref_check.isChecked(),
            "raw_mode":self.raw_mode.isChecked(),
            "delay":self.delay.value(),
            "timeout":self.timeout.value(),
            "cluster_threshold":self.cluster_threshold.value(),
            "persist_history":self.persist_history.isChecked(),
            "test_level":self.current_test_level(),
            "rules":self.current_rules().to_dict(),
            "raw_request":self.raw.toPlainText(),
            "data":self.data_text.toPlainText(),
            "headers":self.header_text.toPlainText(),
            "disabled_builtin":list(self.disabled_builtin)
        }
        save_project(p,cfg,self.custom_cases)
        self.top_status.setText("项目已保存")

    def open_project(self):
        p,_=QFileDialog.getOpenFileName(self,"打开项目","","UploadSentinel Project (*.usproj);;All files (*)")
        if not p:return
        try:
            cfg,custom=load_project(p)
            self.custom_cases=custom
            self.url.setText(cfg.get("url",""))
            self.field.setText(cfg.get("field","file"))
            self.method.setCurrentText(cfg.get("method","POST"))
            self.scheme.setCurrentText(cfg.get("scheme","https"))
            self.proxy.setText(cfg.get("proxy",""))
            self.insecure.setChecked(cfg.get("insecure",False))
            self.ref_check.setChecked(cfg.get("ref_check",True))
            self.raw_mode.setChecked(cfg.get("raw_mode",False))
            self.delay.setValue(float(cfg.get("delay",0.25)))
            self.timeout.setValue(int(cfg.get("timeout",15)))
            self.cluster_threshold.setValue(float(cfg.get("cluster_threshold",0.92)))
            self.persist_history.setChecked(bool(cfg.get("persist_history",False)))
            saved_level=cfg.get("test_level","medium")
            self.test_level.setCurrentText("低档（基础）" if saved_level=="low" else "高档（全面）" if saved_level=="high" else "中档（推荐）")
            self.update_level_summary()
            rules = RuleConfig.from_dict(cfg.get("rules",{}))
            self.success_regex.setPlainText("\n".join(rules.success_regex))
            self.reject_regex.setPlainText("\n".join(rules.reject_regex))
            self.success_status.setText(",".join(str(x) for x in rules.success_status))
            self.reject_status.setText(",".join(str(x) for x in rules.reject_status))
            self.raw.setPlainText(cfg.get("raw_request",""))
            self.data_text.setPlainText(cfg.get("data",""))
            self.header_text.setPlainText(cfg.get("headers",""))
            self.disabled_builtin=set(cfg.get("disabled_builtin",[]))
            self.populate_cases()
            self.top_status.setText("项目已加载")
        except Exception as e:
            QMessageBox.critical(self,"项目打开失败",str(e))

    def export_results(self):
        if not self.results:
            QMessageBox.information(self,"没有测试结果","请先执行一次扫描。"); return
        folder=QFileDialog.getExistingDirectory(self,"选择导出目录")
        if not folder:return
        base=Path(folder)/"uploadsentinel-v4.1-results"
        save_json(self.results,str(base)+".json")
        save_csv(self.results,str(base)+".csv")
        target=getattr(getattr(self,"scanner",None),"url",self.url.text())
        save_html(self.results,str(base)+".html",target)
        self.top_status.setText("结果已导出")
        QMessageBox.information(self,"导出完成",f"Saved:\n{base}.json\n{base}.csv\n{base}.html")

    def about(self):
        QMessageBox.information(
            self,"关于 UploadSentinel v1.1",
            "UploadSentinel v1.1"
            "Qt-based file-upload security workbench with response clustering, custom verdict rules, and persistent history for authorized assessments.\n"
            "Built-in payloads are benign and non-executable.\n\n"
            "HIGH_REVIEW / REVIEW are triage signals, not confirmed vulnerabilities."
        )


def main():
    app=QApplication(sys.argv)
    app.setApplicationName("UploadSentinel")
    app.setStyle("Fusion")
    win=App()
    win.show()
    sys.exit(app.exec())


if __name__=="__main__":
    main()
