import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QToolBar,
                           QFileDialog, QColorDialog, QFontDialog, QMenu, QFontComboBox, QComboBox,
                           QLabel, QVBoxLayout, QWidget, QHBoxLayout, QSplitter, QInputDialog,
                           QStatusBar, QDialog, QVBoxLayout, QTextEdit, QPushButton, QDialogButtonBox,
                           QToolButton, QWidgetAction, QToolTip, QFrame)
from PySide6.QtGui import (QIcon, QTextCharFormat, QFont, QColor, QAction, 
                         QPainter, QPixmap, QTextCursor, QBrush, QPen, QLinearGradient,
                         QSyntaxHighlighter, QTextBlockFormat, QTextListFormat, QTextDocument,
                         QRadialGradient, QPainterPath, QDesktopServices, QPalette)
from PySide6.QtCore import Qt, QSize, QRegularExpression, QDateTime, QTimer, QPoint, QUrl, Signal
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
import re
import math
import random
import time

class JaganEyeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(400, 400)
        
        # Create circular mask for clickable area
        mask = QPixmap(400, 400)
        mask.fill(Qt.GlobalColor.transparent)
        painter = QPainter(mask)
        painter.setBrush(Qt.GlobalColor.black)
        painter.drawEllipse(0, 0, 400, 400)
        painter.end()
        self.setMask(mask.mask())
        
        # Eye state
        self.eye_open = False
        self.eye_transition = 0.0
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.update_eye_transition)
        self.blink_timer.setInterval(20)
        
        # Idle timer for closing eye
        self.idle_timer = QTimer()
        self.idle_timer.timeout.connect(self.handle_idle)
        self.idle_timer.setInterval(1000)
        self.last_activity_time = time.time()
        self.IDLE_TIMEOUT = 0.5
        
        # Mouse tracking for dragging
        self.drag_start_pos = None
        self.is_dragging = False
        
        # Glow effect
        self.glow_opacity = 0
        self.glow_timer = QTimer()
        self.glow_timer.timeout.connect(self.update_glow)
        self.glow_timer.setInterval(50)
        self.glow_timer.start()
        
        # Tibetan text
        self.tibetan_chars = ["ཨོཾ", "མ་", "ཎི", "པདྨེ", "ཧཱུྃ", "ཨོཾ", "མ་", "ཎི", "པདྨེ", "ཧཱུྃ"]
        self.outer_tibetan_chars = ["ཨོཾ", "མ་", "ཎི", "པདྨེ", "ཧཱུྃ", "ཨོཾ", "མ་", "ཎི", "པདྨེ", "ཧཱུྃ"]
        self.middle_tibetan_chars = ["ཨོཾ", "མ་", "ཎི", "པདྨེ", "ཧཱུྃ", "ཨོཾ", "མ་", "ཎི", "པདྨེ", "ཧཱུྃ"]
        self.text_rotation = 0
        self.outer_text_rotation = 0
        self.middle_text_rotation = 0
        self.text_timer = QTimer()
        self.text_timer.timeout.connect(self.update_text_rotation)
        self.text_timer.setInterval(50)
        self.text_timer.start()
        
        # Start idle timer
        self.idle_timer.start()

    def handle_keystroke(self):
        self.last_activity_time = time.time()
        if not self.eye_open:
            self.eye_open = True
            self.blink_timer.start()

    def handle_idle(self):
        if time.time() - self.last_activity_time > self.IDLE_TIMEOUT:
            if self.eye_open:
                self.eye_open = False
                self.blink_timer.start()

    def update_eye_transition(self):
        if self.eye_open:
            if self.eye_transition < 1:
                self.eye_transition += 0.1
                if self.eye_transition >= 1:
                    self.eye_transition = 1
        else:
            if self.eye_transition > 0:
                self.eye_transition -= 0.05
                if self.eye_transition <= 0:
                    self.eye_transition = 0
        self.update()

    def update_text_rotation(self):
        if self.eye_open:
            # Inner ring rotates clockwise
            self.text_rotation += 0.5
            if self.text_rotation >= 360:
                self.text_rotation = 0
            # Middle ring rotates counter-clockwise
            self.middle_text_rotation -= 0.3
            if self.middle_text_rotation <= -360:
                self.middle_text_rotation = 0
            # Outer ring rotates counter-clockwise
            self.outer_text_rotation -= 0.7  # Slightly faster for visual interest
            if self.outer_text_rotation <= -360:
                self.outer_text_rotation = 0
            self.update()

    def update_glow(self):
        if self.eye_transition > 0:
            self.glow_opacity = 0.1 + 0.2 * (math.sin(time.time() * 2) + 1) / 2
        else:
            self.glow_opacity = 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw glow
        if self.eye_transition > 0 and self.glow_opacity > 0:
            gradient = QRadialGradient(200, 200, 100)
            gradient.setColorAt(0, QColor(255, 0, 0, int(self.glow_opacity * 255 * 0.3 * self.eye_transition)))
            gradient.setColorAt(0.5, QColor(255, 0, 0, int(self.glow_opacity * 255 * 0.2 * self.eye_transition)))
            gradient.setColorAt(1, QColor(255, 0, 0, 0))
            painter.setBrush(gradient)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(100, 100, 200, 200)

        # Draw Tibetan text circles
        center_x, center_y = 200, 200
        
        # Inner circle of text
        inner_radius = 85
        for i, char in enumerate(self.tibetan_chars):
            base_angle = (2 * math.pi * i / len(self.tibetan_chars))
            if self.eye_open:
                angle = base_angle + math.radians(self.text_rotation)
            else:
                angle = base_angle
            
            x = center_x + inner_radius * math.cos(angle)
            y = center_y + inner_radius * math.sin(angle)
            
            font = QFont("Noto Sans Tibetan", 12)
            painter.setFont(font)
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            
            painter.save()
            painter.translate(x, y)
            painter.rotate(math.degrees(angle) + 90)
            painter.drawText(0, 0, char)
            painter.restore()

        # Middle circle of text when eye is open
        if self.eye_open:
            middle_radius = 110
            for i, char in enumerate(self.middle_tibetan_chars):
                base_angle = (2 * math.pi * i / len(self.middle_tibetan_chars))
                angle = base_angle + math.radians(self.middle_text_rotation)
                
                x = center_x + middle_radius * math.cos(angle)
                y = center_y + middle_radius * math.sin(angle)
                
                font = QFont("Noto Sans Tibetan", 12)
                painter.setFont(font)
                painter.setPen(QPen(QColor(255, 255, 255), 1))
                
                painter.save()
                painter.translate(x, y)
                painter.rotate(math.degrees(angle) + 90)
                painter.drawText(0, 0, char)
                painter.restore()

        # Outer circle of text when eye is open
        if self.eye_open:
            outer_radius = 145
            for i, char in enumerate(self.outer_tibetan_chars):
                base_angle = (2 * math.pi * i / len(self.outer_tibetan_chars))
                angle = base_angle + math.radians(self.outer_text_rotation)
                
                x = center_x + outer_radius * math.cos(angle)
                y = center_y + outer_radius * math.sin(angle)
                
                font = QFont("Noto Sans Tibetan", 12)
                painter.setFont(font)
                painter.setPen(QPen(QColor(255, 255, 255), 1))
                
                painter.save()
                painter.translate(x, y)
                painter.rotate(math.degrees(angle) + 90)
                painter.drawText(0, 0, char)
                painter.restore()

        # Draw main white circle
        painter.setPen(QPen(QColor(255, 255, 255), 3))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(130, 130, 140, 140)

        if self.eye_transition > 0:
            # Draw black circle with brush effect
            painter.setPen(QPen(QColor(0, 0, 0), 6))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(135, 135, 130, 130)
            
            # Brush stroke variations
            offsets = [(0, 0), (1, 1), (-1, -1), (2, 0), (0, 2), (-2, 0), (0, -2)]
            for dx, dy in offsets:
                painter.setPen(QPen(QColor(0, 0, 0), random.randint(4, 7)))
                painter.drawEllipse(135 + dx, 135 + dy, 130, 130)

            # Draw concentric circles for iris
            circle_sizes = [20, 28]
            for size in circle_sizes:
                circle_size = int(size * self.eye_transition)
                painter.setPen(QPen(QColor(255, 255, 255), 1))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(200 - circle_size//2, 200 - circle_size//2, circle_size, circle_size)

            # Draw almond-shaped eye
            path = QPainterPath()
            start_y = 200
            control_y = 160 + (40 * (1 - self.eye_transition))
            path.moveTo(140, start_y)
            path.quadTo(200, control_y, 260, start_y)
            path.quadTo(200, 240 - (40 * (1 - self.eye_transition)), 140, start_y)
            painter.setPen(QPen(QColor(255, 255, 255), 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)
        else:
            # Draw closed eye with proper concentric circles
            # Main black circle
            painter.setPen(QPen(QColor(0, 0, 0), 4))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(135, 135, 130, 130)
            
            # First white circle (larger)
            painter.setPen(QPen(QColor(255, 255, 255), 2))
            painter.drawEllipse(187, 187, 25, 25)
            
            # Second white circle (smaller)
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.drawEllipse(192, 192, 15, 15)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.position().toPoint()
            self.is_dragging = True
            self.eye_open = True
            self.blink_timer.start()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.eye_open = False
            self.blink_timer.start()

    def mouseMoveEvent(self, event):
        if self.is_dragging and self.drag_start_pos is not None:
            delta = event.position().toPoint() - self.drag_start_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())

class ClickableTextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hover_note_popup = None

    def mouseMoveEvent(self, event):
        cursor = self.cursorForPosition(event.position().toPoint())
        char_format = cursor.charFormat()
        anchor_href = char_format.anchorHref() if char_format.isAnchor() else None
        # Check for hover note
        note = None
        if char_format.isValid() and char_format.property(1001):
            note = char_format.property(1001)
        if note:
            if not self.hover_note_popup:
                self.hover_note_popup = HoverNotePopup(note, self)
            else:
                self.hover_note_popup.close()
                self.hover_note_popup = HoverNotePopup(note, self)
            global_pos = self.mapToGlobal(event.position().toPoint())
            self.hover_note_popup.move(global_pos + QPoint(10, 20))
            self.hover_note_popup.show()
        else:
            if self.hover_note_popup:
                self.hover_note_popup.close()
                self.hover_note_popup = None
        # Hyperlink cursor
        if anchor_href:
            self.viewport().setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.viewport().unsetCursor()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        if self.hover_note_popup:
            self.hover_note_popup.close()
            self.hover_note_popup = None
        self.viewport().unsetCursor()
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event):
        cursor = self.cursorForPosition(event.position().toPoint())
        char_format = cursor.charFormat()
        if char_format.isAnchor():
            url = char_format.anchorHref()
            if url:
                if not (url.startswith('http://') or url.startswith('https://')):
                    url = 'https://' + url
                QDesktopServices.openUrl(QUrl(url))
                return
        super().mouseReleaseEvent(event)

class LinkFloatingBar(QFrame):
    def __init__(self, url, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setObjectName("LinkFloatingBar")
        # No border style
        self.setStyleSheet(f"""
            QFrame#LinkFloatingBar {{
                background: #000;
                border: none;
                border-radius: 8px;
                padding: 8px 12px 8px 12px;
                min-width: 120px;
                max-width: 420px;
            }}
            QPushButton#LinkBtn {{
                background: transparent;
                color: #39F;
                border: none;
                font-size: 13px;
                font-weight: bold;
                text-align: left;
                text-decoration: underline;
                padding: 0 0 0 0;
            }}
            QPushButton#LinkBtn:hover {{
                color: #5af;
                text-decoration: underline;
            }}
        """)
        self.url = url
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)
        link_btn = QPushButton(url)
        link_btn.setObjectName("LinkBtn")
        link_btn.setToolTip(url)
        link_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        link_btn.clicked.connect(self.open_link)
        layout.addWidget(link_btn, 1)
        self.setLayout(layout)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        # Drop shadow effect
        try:
            from PySide6.QtWidgets import QGraphicsDropShadowEffect
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(14)
            shadow.setColor(QColor(30, 30, 40, 180))
            shadow.setOffset(0, 2)
            self.setGraphicsEffect(shadow)
        except ImportError:
            pass

    def open_link(self):
        url = self.url
        if not (url.startswith('http://') or url.startswith('https://')):
            url = 'https://' + url
        QDesktopServices.openUrl(QUrl(url))
        self.close()

    def leaveEvent(self, event):
        self.close()
        super().leaveEvent(event)

class HoverNotePopup(QFrame):
    def __init__(self, note, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)
        self.setStyleSheet("""
            QFrame {
                background: #000;
                color: #fff;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                min-width: 80px;
                max-width: 320px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        label = QLabel(note)
        label.setStyleSheet("color: #fff;")
        label.setWordWrap(True)
        layout.addWidget(label)
        self.setLayout(layout)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        
        # Headers
        header_format = QTextCharFormat()
        header_format.setForeground(QColor(255, 150, 50))
        header_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((QRegularExpression(r'^#{1,6}\s.*$'), header_format))
        
        # Bold
        bold_format = QTextCharFormat()
        bold_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((QRegularExpression(r'\*\*.*\*\*'), bold_format))
        self.highlighting_rules.append((QRegularExpression(r'__.*__'), bold_format))
        
        # Italic
        italic_format = QTextCharFormat()
        italic_format.setFontItalic(True)
        self.highlighting_rules.append((QRegularExpression(r'\*.*\*'), italic_format))
        self.highlighting_rules.append((QRegularExpression(r'_.*_'), italic_format))
        
        # Code
        code_format = QTextCharFormat()
        code_format.setBackground(QColor(40, 40, 40))
        self.highlighting_rules.append((QRegularExpression(r'`.*`'), code_format))
        
        # Links
        link_format = QTextCharFormat()
        link_format.setForeground(QColor(100, 150, 255))
        self.highlighting_rules.append((QRegularExpression(r'\[.*\]\(.*\)'), link_format))
        
        # Lists
        list_format = QTextCharFormat()
        list_format.setForeground(QColor(200, 200, 200))
        self.highlighting_rules.append((QRegularExpression(r'^[\*\-+]\s.*$'), list_format))
        self.highlighting_rules.append((QRegularExpression(r'^\d+\.\s.*$'), list_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

class TextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(self.create_circle_icon())
        self.rainbow_colors = [
            QColor(255, 0, 0),    # Red
            QColor(255, 127, 0),  # Orange
            QColor(255, 255, 0),  # Yellow
            QColor(0, 255, 0),    # Green
            QColor(0, 0, 255),    # Blue
            QColor(75, 0, 130),   # Indigo
            QColor(148, 0, 211)   # Violet
        ]
        self.current_rainbow_index = 0
        self.track_changes = False
        self.changes = []
        self.preview_mode = False
        self.preview_type = "markdown"  # or "html"
        self.original_text = ""
        self.jagan_eye = None
        self.link_bar = None
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.initUI()
        
        # Connect context menu
        self.text_edit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.text_edit.customContextMenuRequested.connect(self.show_context_menu)

        # Connect text edit's textChanged signal
        self.text_edit.textChanged.connect(self.handle_text_changed)

    def initUI(self):
        self.setWindowTitle('Kristoferrian Null Editor')
        self.setGeometry(100, 100, 1200, 800)
        
        # Set the main window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
            }
            QTextEdit {
                background-color: #000000;
                color: #ffffff;
                border: none;
                padding: 10px;
                selection-background-color: #1a1a1a;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 14px;
                line-height: 1.5;
            }
            QMenuBar {
                background-color: #000000;
                color: #ffffff;
                border: none;
                padding: 5px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QMenuBar::item:selected {
                background-color: #1a1a1a;
            }
            QMenu {
                background-color: #000000;
                color: #ffffff;
                border: 1px solid #1a1a1a;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 25px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #1a1a1a;
            }
            QToolBar {
                background-color: #000000;
                border: none;
                spacing: 5px;
                padding: 5px;
            }
            QToolButton {
                background-color: transparent;
                border: none;
                padding: 5px;
                color: #ffffff;
                border-radius: 3px;
            }
            QToolButton:hover {
                background-color: #1a1a1a;
            }
            QComboBox {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #2a2a2a;
                border-radius: 3px;
                padding: 5px;
                min-width: 100px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #2a2a2a;
                selection-background-color: #2a2a2a;
            }
            QLabel {
                color: #ffffff;
            }
        """)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create text editor
        self.text_edit = ClickableTextEdit()
        self.text_edit.setAcceptRichText(True)
        self.text_edit.setFontFamily("Calibri")
        self.text_edit.setFontPointSize(10)
        # Enable clickable and hoverable hyperlinks
        self.text_edit.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction | Qt.TextInteractionFlag.LinksAccessibleByMouse)
        self.text_edit.document().setDefaultStyleSheet("a { color: #39F; text-decoration: underline; }")
        self.text_edit.setCursorWidth(2)
        self.text_edit.setMouseTracking(True)
        layout.addWidget(self.text_edit)
        
        # Create toolbar first
        self.toolbar = QToolBar()
        self.toolbar.setMovable(True)
        self.addToolBar(self.toolbar)
        
        # File operations
        new_action = QAction('New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_file)
        self.toolbar.addAction(new_action)
        
        open_action = QAction('Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        self.toolbar.addAction(open_action)
        
        # Save button
        save_action = QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        self.toolbar.addAction(save_action)
        
        # Font Family
        self.font_combo = QComboBox()
        self.font_combo.addItems(["Arial", "Calibri", "Courier", "Karbon"])
        self.font_combo.currentTextChanged.connect(self.text_edit.setFontFamily)
        self.font_combo.setCurrentText("Calibri")
        self.font_combo.setFixedWidth(50)
        self.toolbar.addWidget(self.font_combo)
        
        # Font Size
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems([str(i) for i in range(8, 73, 2)])
        self.font_size_combo.currentTextChanged.connect(lambda s: self.text_edit.setFontPointSize(float(s)))
        self.font_size_combo.setCurrentText("12")
        self.font_size_combo.setFixedWidth(18)
        self.toolbar.addWidget(self.font_size_combo)
        
        # Style Buttons
        bold_button = QToolButton()
        bold_button.setText("B")
        bold_button.setCheckable(True)
        bold_button.setStyleSheet("""
            QToolButton {
                font-weight: bold;
                padding: 5px 10px;
            }
            QToolButton:checked {
                background-color: #1a1a1a;
            }
        """)
        bold_button.clicked.connect(self.toggle_bold)
        self.toolbar.addWidget(bold_button)
        
        italic_button = QToolButton()
        italic_button.setText("I")
        italic_button.setCheckable(True)
        italic_button.setStyleSheet("""
            QToolButton {
                font-style: italic;
                padding: 5px 10px;
            }
            QToolButton:checked {
                background-color: #1a1a1a;
            }
        """)
        italic_button.clicked.connect(self.toggle_italic)
        self.toolbar.addWidget(italic_button)
        
        underline_button = QToolButton()
        underline_button.setText("U")
        underline_button.setCheckable(True)
        underline_button.setStyleSheet("""
            QToolButton {
                text-decoration: underline;
                padding: 5px 10px;
            }
            QToolButton:checked {
                background-color: #1a1a1a;
            }
        """)
        underline_button.clicked.connect(self.toggle_underline)
        self.toolbar.addWidget(underline_button)
        
        # Text Case Buttons
        uppercase_button = QToolButton()
        uppercase_button.setText("A")
        uppercase_button.setStyleSheet("""
            QToolButton {
                text-transform: uppercase;
                padding: 5px 10px;
            }
        """)
        uppercase_button.clicked.connect(self.to_uppercase)
        self.toolbar.addWidget(uppercase_button)
        
        lowercase_button = QToolButton()
        lowercase_button.setText("a")
        lowercase_button.setStyleSheet("""
            QToolButton {
                text-transform: lowercase;
                padding: 5px 10px;
            }
        """)
        lowercase_button.clicked.connect(self.to_lowercase)
        self.toolbar.addWidget(lowercase_button)
        
        titlecase_button = QToolButton()
        titlecase_button.setText("Aa")
        titlecase_button.setStyleSheet("""
            QToolButton {
                padding: 5px 10px;
            }
        """)
        titlecase_button.clicked.connect(self.to_title_case)
        self.toolbar.addWidget(titlecase_button)
        
        # Superscript and Subscript Buttons
        superscript_button = QToolButton()
        superscript_button.setText("x²")
        superscript_button.setCheckable(True)
        superscript_button.setStyleSheet("""
            QToolButton {
                padding: 5px 10px;
            }
            QToolButton:checked {
                background-color: #1a1a1a;
            }
        """)
        superscript_button.clicked.connect(self.toggle_superscript)
        self.toolbar.addWidget(superscript_button)
        
        # Add subscript button
        subscript_button = QToolButton()
        subscript_button.setText("x₂")
        subscript_button.setCheckable(True)
        subscript_button.setStyleSheet("""
            QToolButton {
                padding: 5px 10px;
            }
            QToolButton:checked {
                background-color: #1a1a1a;
            }
        """)
        subscript_button.clicked.connect(self.toggle_subscript)
        self.toolbar.addWidget(subscript_button)
        
        # Add hyperlink button
        hyperlink_button = QToolButton()
        hyperlink_button.setText("🔗")
        hyperlink_button.setStyleSheet("""
            QToolButton {
                padding: 5px 10px;
            }
        """)
        hyperlink_button.clicked.connect(self.insert_hyperlink)
        self.toolbar.addWidget(hyperlink_button)
        
        # Add hover note button
        hover_note_button = QToolButton()
        hover_note_button.setText("🛈")
        hover_note_button.setStyleSheet("""
            QToolButton {
                padding: 5px 10px;
            }
        """)
        hover_note_button.clicked.connect(self.insert_hover_note)
        self.toolbar.addWidget(hover_note_button)
        
        # Text Color Button
        text_color_button = QToolButton()
        text_color_button.setText("clr")
        text_color_button.setStyleSheet("""
            QToolButton {
                padding: 5px 10px;
                color: #39FF14;
                font-weight: bold;
            }
        """)
        text_color_button.clicked.connect(self.change_text_color)
        self.toolbar.addWidget(text_color_button)
        
        # Add preview button
        preview_button = QToolButton()
        preview_button.setText("Preview")
        preview_button.setCheckable(True)
        preview_button.setStyleSheet("""
            QToolButton {
                padding: 5px 10px;
                color: #ffffff;
            }
            QToolButton:checked {
                background-color: #1a1a1a;
            }
        """)
        preview_button.clicked.connect(self.toggle_preview)
        self.toolbar.addWidget(preview_button)
        
        # Word Count Label
        self.word_count_label = QLabel()
        self.word_count_label.setStyleSheet("""
            QLabel {
                padding: 5px 10px;
                color: #ffffff;
            }
        """)
        self.toolbar.addWidget(self.word_count_label)
        self.update_word_count()
        
        # Connect text changed signal
        self.text_edit.textChanged.connect(self.update_word_count)

    def create_file_menu(self):
        # Create File menu
        file_menu = self.menuBar().addMenu('File')
        
        # New
        new_action = QAction('New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        # Open
        open_action = QAction('Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        # Save submenu
        save_menu = QMenu('Save', self)
        
        # Save as TXT
        save_txt_action = QAction('Save as TXT', self)
        save_txt_action.setShortcut('Ctrl+S')
        save_txt_action.triggered.connect(self.save_file)
        save_menu.addAction(save_txt_action)
        
        # Save as PDF
        save_pdf_action = QAction('Save as PDF', self)
        save_pdf_action.setShortcut('Ctrl+Shift+P')
        save_pdf_action.triggered.connect(self.export_to_pdf)
        save_menu.addAction(save_pdf_action)
        
        # Save as HTML
        save_html_action = QAction('Save as HTML', self)
        save_html_action.setShortcut('Ctrl+Shift+H')
        save_html_action.triggered.connect(self.export_to_html)
        save_menu.addAction(save_html_action)
        
        file_menu.addMenu(save_menu)
        
        # Add to toolbar
        self.toolbar.addAction(new_action)
        self.toolbar.addAction(open_action)
        
        # Save button
        save_action = QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        self.toolbar.addAction(save_action)
        
        # Add separator
        self.toolbar.addSeparator()

    def create_formatting_toolbar(self):
        """Create the formatting toolbar with direct font and style controls"""
        # Add separator
        self.toolbar.addSeparator()
        
        # Font Family
        self.font_combo = QComboBox()
        self.font_combo.addItems(["Arial", "Calibri", "Courier", "Karbon"])
        self.font_combo.currentTextChanged.connect(self.text_edit.setFontFamily)
        self.font_combo.setCurrentText("Calibri")
        self.font_combo.setFixedWidth(50)
        self.toolbar.addWidget(self.font_combo)
        
        # Font Size
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems([str(i) for i in range(8, 73, 2)])
        self.font_size_combo.currentTextChanged.connect(lambda s: self.text_edit.setFontPointSize(float(s)))
        self.font_size_combo.setCurrentText("12")
        self.font_size_combo.setFixedWidth(18)
        self.toolbar.addWidget(self.font_size_combo)
        
        # Add separator
        self.toolbar.addSeparator()
        
        # Style Buttons
        bold_button = QToolButton()
        bold_button.setText("B")
        bold_button.setCheckable(True)
        bold_button.setStyleSheet("""
            QToolButton {
                font-weight: bold;
                padding: 5px 10px;
            }
            QToolButton:checked {
                background-color: #1a1a1a;
            }
        """)
        bold_button.clicked.connect(self.toggle_bold)
        self.toolbar.addWidget(bold_button)
        
        italic_button = QToolButton()
        italic_button.setText("I")
        italic_button.setCheckable(True)
        italic_button.setStyleSheet("""
            QToolButton {
                font-style: italic;
                padding: 5px 10px;
            }
            QToolButton:checked {
                background-color: #1a1a1a;
            }
        """)
        italic_button.clicked.connect(self.toggle_italic)
        self.toolbar.addWidget(italic_button)
        
        underline_button = QToolButton()
        underline_button.setText("U")
        underline_button.setCheckable(True)
        underline_button.setStyleSheet("""
            QToolButton {
                text-decoration: underline;
                padding: 5px 10px;
            }
            QToolButton:checked {
                background-color: #1a1a1a;
            }
        """)
        underline_button.clicked.connect(self.toggle_underline)
        self.toolbar.addWidget(underline_button)
        
        # Add separator
        self.toolbar.addSeparator()
        
        # Text Case Buttons
        uppercase_button = QToolButton()
        uppercase_button.setText("A")
        uppercase_button.setStyleSheet("""
            QToolButton {
                text-transform: uppercase;
                padding: 5px 10px;
            }
        """)
        uppercase_button.clicked.connect(self.to_uppercase)
        self.toolbar.addWidget(uppercase_button)
        
        lowercase_button = QToolButton()
        lowercase_button.setText("a")
        lowercase_button.setStyleSheet("""
            QToolButton {
                text-transform: lowercase;
                padding: 5px 10px;
            }
        """)
        lowercase_button.clicked.connect(self.to_lowercase)
        self.toolbar.addWidget(lowercase_button)
        
        titlecase_button = QToolButton()
        titlecase_button.setText("Aa")
        titlecase_button.setStyleSheet("""
            QToolButton {
                padding: 5px 10px;
            }
        """)
        titlecase_button.clicked.connect(self.to_title_case)
        self.toolbar.addWidget(titlecase_button)
        
        # Add separator
        self.toolbar.addSeparator()
        
        # Superscript and Subscript Buttons
        superscript_button = QToolButton()
        superscript_button.setText("x²")
        superscript_button.setCheckable(True)
        superscript_button.setStyleSheet("""
            QToolButton {
                padding: 5px 10px;
            }
            QToolButton:checked {
                background-color: #1a1a1a;
            }
        """)
        superscript_button.clicked.connect(self.toggle_superscript)
        self.toolbar.addWidget(superscript_button)
        
        # Add subscript button
        subscript_button = QToolButton()
        subscript_button.setText("x₂")
        subscript_button.setCheckable(True)
        subscript_button.setStyleSheet("""
            QToolButton {
                padding: 5px 10px;
            }
            QToolButton:checked {
                background-color: #1a1a1a;
            }
        """)
        subscript_button.clicked.connect(self.toggle_subscript)
        self.toolbar.addWidget(subscript_button)
        
        # Add hyperlink button
        hyperlink_button = QToolButton()
        hyperlink_button.setText("🔗")
        hyperlink_button.setStyleSheet("""
            QToolButton {
                padding: 5px 10px;
            }
        """)
        hyperlink_button.clicked.connect(self.insert_hyperlink)
        self.toolbar.addWidget(hyperlink_button)
        
        # Add hover note button
        hover_note_button = QToolButton()
        hover_note_button.setText("🛈")
        hover_note_button.setStyleSheet("""
            QToolButton {
                padding: 5px 10px;
            }
        """)
        hover_note_button.clicked.connect(self.insert_hover_note)
        self.toolbar.addWidget(hover_note_button)
        
        # Add separator
        self.toolbar.addSeparator()
        
        # Text Color Button
        text_color_button = QToolButton()
        text_color_button.setText("clr")
        text_color_button.setStyleSheet("""
            QToolButton {
                padding: 5px 10px;
                color: #39FF14;
                font-weight: bold;
            }
        """)
        text_color_button.clicked.connect(self.change_text_color)
        self.toolbar.addWidget(text_color_button)
        
        # Add preview button
        preview_button = QToolButton()
        preview_button.setText("Preview")
        preview_button.setCheckable(True)
        preview_button.setStyleSheet("""
            QToolButton {
                padding: 5px 10px;
                color: #ffffff;
            }
            QToolButton:checked {
                background-color: #1a1a1a;
            }
        """)
        preview_button.clicked.connect(self.toggle_preview)
        self.toolbar.addWidget(preview_button)
        
        # Add separator
        self.toolbar.addSeparator()
        
        # Word Count Label
        self.word_count_label = QLabel()
        self.word_count_label.setStyleSheet("""
            QLabel {
                padding: 5px 10px;
                color: #ffffff;
            }
        """)
        self.toolbar.addWidget(self.word_count_label)
        self.update_word_count()
        
        # Connect text changed signal
        self.text_edit.textChanged.connect(self.update_word_count)

    def create_icon(self, text):
        """Create an icon with the given text or emoji"""
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Use a slightly larger font for emojis
        if len(text) == 1 and ord(text) > 127:  # Emoji
            painter.setFont(QFont('Segoe UI Emoji', 14))
        else:
            painter.setFont(QFont('Arial', 12, QFont.Bold))
        
        painter.setPen(Qt.white)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, text)
        painter.end()
        return QIcon(pixmap)
        
    def create_circle_icon(self):
        # Create a pixmap for the icon
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        
        # Create a painter to draw the circle outline
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw the circle outline
        painter.setPen(QPen(QColor(255, 255, 255), 2))  # White color, 2px width
        painter.setBrush(Qt.transparent)  # No fill
        painter.drawEllipse(4, 4, 24, 24)  # Draw a circle outline
        
        painter.end()
        
        return QIcon(pixmap)
        
    def change_font(self, font_name):
        cursor = self.text_edit.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        format = cursor.charFormat()
        format.setFontFamily(font_name)
        cursor.mergeCharFormat(format)
        
    def change_font_size(self, size):
        cursor = self.text_edit.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        format = cursor.charFormat()
        format.setFontPointSize(float(size))
        cursor.mergeCharFormat(format)
        
    def new_file(self):
        self.text_edit.clear()
        
    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", 
                                                "Text Files (*.txt);;Markdown Files (*.md);;HTML Files (*.html);;All Files (*)")
        if filename:
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read()
                if filename.endswith('.html'):
                    self.text_edit.setHtml(content)
                elif filename.endswith('.md'):
                    # Basic markdown to HTML conversion
                    html = content.replace("\n\n", "</p><p>")
                    html = html.replace("\n", "<br>")
                    
                    # Headers
                    for i in range(6, 0, -1):
                        pattern = "#" * i + " "
                        if pattern in html:
                            html = html.replace(pattern, f"<h{i}>") + f"</h{i}>"
                    
                    # Bold
                    while "**" in html:
                        html = html.replace("**", "<strong>", 1)
                        html = html.replace("**", "</strong>", 1)
                    
                    # Italic
                    while "*" in html:
                        html = html.replace("*", "<em>", 1)
                        html = html.replace("*", "</em>", 1)
                    
                    # Underline
                    while "__" in html:
                        html = html.replace("__", "<u>", 1)
                        html = html.replace("__", "</u>", 1)
                    
                    html = f"<p>{html}</p>"
                    self.text_edit.setHtml(html)
                else:
                    self.text_edit.setPlainText(content)
                
    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save File", "", 
                                                "Text Files (*.txt);;Markdown Files (*.md);;PDF Files (*.pdf);;HTML Files (*.html);;All Files (*)")
        if filename:
            if filename.endswith('.pdf'):
                self.export_to_pdf(filename)
            elif filename.endswith('.html'):
                self.export_to_html(filename)
            else:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(self.text_edit.toPlainText())
                
    def toggle_bold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold if self.text_edit.fontWeight() != QFont.Bold 
                         else QFont.Normal)
        self.text_edit.mergeCurrentCharFormat(fmt)
        
    def toggle_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(not self.text_edit.fontItalic())
        self.text_edit.mergeCurrentCharFormat(fmt)
        
    def toggle_underline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(not self.text_edit.fontUnderline())
        self.text_edit.mergeCurrentCharFormat(fmt)
        
    def toggle_superscript(self):
        fmt = QTextCharFormat()
        fmt.setVerticalAlignment(QTextCharFormat.AlignSuperScript)
        self.text_edit.mergeCurrentCharFormat(fmt)
        
    def toggle_subscript(self):
        fmt = QTextCharFormat()
        fmt.setVerticalAlignment(QTextCharFormat.AlignSubScript)
        self.text_edit.mergeCurrentCharFormat(fmt)
        
    def change_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            cursor = self.text_edit.textCursor()
            format = cursor.charFormat()
            format.setForeground(color)
            cursor.mergeCharFormat(format)
            
            # Update the color button to show the selected color
            button = self.sender()
            if button:
                button.setStyleSheet(f"""
                    QToolButton {{
                        padding: 5px 10px;
                        color: {color.name()};
                        font-weight: bold;
                    }}
                """)
        
    def undo(self):
        self.text_edit.undo()

    def redo(self):
        self.text_edit.redo()

    def show_context_menu(self, pos):
        cursor = self.text_edit.cursorForPosition(pos)
        char_format = cursor.charFormat()
        is_link = char_format.isAnchor()
        
        menu = self.text_edit.createStandardContextMenu()
        menu.addSeparator()
        
        if is_link:
            # Add Edit Link action
            edit_link = menu.addAction("Edit Link")
            edit_link.triggered.connect(self.insert_hyperlink)
            
            # Add Remove Link action
            remove_link = menu.addAction("Remove Link")
            remove_link.triggered.connect(self.remove_hyperlink)
        else:
            # Add Insert Link action
            insert_link = menu.addAction("Insert Link")
            insert_link.triggered.connect(self.insert_hyperlink)
        
        # Add Insert Hover Note action
        insert_hover_note = menu.addAction("Insert Hover Note")
        insert_hover_note.triggered.connect(self.insert_hover_note)
        
        # Add Background submenu
        bg_menu = menu.addMenu("Background")
        white_bg_action = bg_menu.addAction("White Background")
        white_bg_action.triggered.connect(self.set_white_background)
        black_bg_action = bg_menu.addAction("Black Background")
        black_bg_action.triggered.connect(self.set_black_background)
        
        # Add other menu items
        show_toolbar = menu.addAction("Show Toolbar")
        show_toolbar.setCheckable(True)
        show_toolbar.setChecked(self.toolbar.isVisible())
        show_toolbar.triggered.connect(self.toggle_toolbar)
        
        toggle_eye = menu.addAction("Toggle Jagan Eye")
        toggle_eye.triggered.connect(self.toggle_jagan_eye)
        
        menu.exec_(self.text_edit.mapToGlobal(pos))

    def toggle_toolbar(self):
        if self.preview_mode:
            # Exit preview mode
            self.preview_mode = False
            self.text_edit.setPlainText(self.original_text)
            if hasattr(self, 'preview_button'):
                self.preview_button.setChecked(False)
        self.toolbar.setVisible(not self.toolbar.isVisible())

    def set_line_spacing(self, spacing):
        """Set line spacing for the current paragraph"""
        block_fmt = self.text_edit.textCursor().blockFormat()
        block_fmt.setLineHeight(float(spacing) * 100, block_fmt.LineHeightType.ProportionalHeight)
        self.text_edit.textCursor().setBlockFormat(block_fmt)

    def set_highlight_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            cursor = self.text_edit.textCursor()
            format = cursor.charFormat()
            format.setBackground(color)
            cursor.mergeCharFormat(format)

    def to_uppercase(self):
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText(text.upper())

    def to_lowercase(self):
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText(text.lower())

    def to_title_case(self):
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText(text.title())

    def create_export_menu(self):
        # Add export options to the file menu
        export_pdf_action = QAction('Export to PDF', self)
        export_pdf_action.triggered.connect(self.export_to_pdf)
        self.toolbar.addAction(export_pdf_action)
        
        export_html_action = QAction('Export to HTML', self)
        export_html_action.triggered.connect(self.export_to_html)
        self.toolbar.addAction(export_html_action)

    def export_to_pdf(self, filename=None):
        """Export the document to PDF"""
        if filename is None:
            filename, _ = QFileDialog.getSaveFileName(self, "Export PDF", "", "PDF files (*.pdf)")
        if filename:
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(filename)
            self.text_edit.document().print_(printer)

    def export_to_html(self, filename=None):
        """Export the document to HTML"""
        if filename is None:
            filename, _ = QFileDialog.getSaveFileName(self, "Export HTML", "", "HTML files (*.html)")
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.text_edit.toHtml())

    def update_word_count(self):
        text = self.text_edit.toPlainText()
        words = len(text.split())
        self.word_count_label.setText(f"Words: {words}")

    def contextMenuEvent(self, event):
        self.show_context_menu(event.pos())

    def toggle_preview(self, checked):
        if checked:
            self.preview_mode = True
            self.original_text = self.text_edit.toPlainText()
            if self.preview_type == "markdown":
                self.update_markdown_preview()
            else:
                self.update_html_preview()
        else:
            self.preview_mode = False
            self.text_edit.setPlainText(self.original_text)

    def update_markdown_preview(self):
        text = self.original_text
        # Convert markdown to HTML
        html = text.replace("\n\n", "</p><p>")
        html = html.replace("\n", "<br>")
        
        # Headers
        for i in range(6, 0, -1):
            pattern = "#" * i + " "
            if pattern in html:
                html = html.replace(pattern, f"<h{i}>") + f"</h{i}>"
        
        # Bold
        while "**" in html:
            html = html.replace("**", "<strong>", 1)
            html = html.replace("**", "</strong>", 1)
        
        # Italic
        while "*" in html:
            html = html.replace("*", "<em>", 1)
            html = html.replace("*", "</em>", 1)
        
        # Underline
        while "__" in html:
            html = html.replace("__", "<u>", 1)
            html = html.replace("__", "</u>", 1)
        
        html = f"<p>{html}</p>"
        self.text_edit.setHtml(html)

    def update_html_preview(self):
        self.text_edit.setHtml(self.original_text)

    def toggle_jagan_eye(self):
        if self.jagan_eye is None:
            self.jagan_eye = JaganEyeWidget(self)
            self.update_eye_position()  # Position in bottom-right corner
            self.jagan_eye.show()
        else:
            self.jagan_eye.close()
            self.jagan_eye = None

    def update_eye_position(self):
        if self.jagan_eye:
            # Position in bottom-right corner with some padding
            padding = 20
            x = self.width() - self.jagan_eye.width() - padding
            y = self.height() - self.jagan_eye.height() - padding
            self.jagan_eye.move(x, y)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_eye_position()  # Update eye position on window resize

    def handle_text_changed(self):
        if self.jagan_eye:
            self.jagan_eye.handle_keystroke()

    def insert_hyperlink(self):
        cursor = self.text_edit.textCursor()
        selected_text = cursor.selectedText()
        
        # Check if we're on an existing link
        char_format = cursor.charFormat()
        is_existing_link = char_format.isAnchor()
        current_url = char_format.anchorHref() if is_existing_link else 'https://'
        
        # Get URL from user
        url, ok = QInputDialog.getText(self, 'Insert Hyperlink',
                                     'Enter URL:', text=current_url)
        
        if ok and url:
            # Create HTML for the link
            if selected_text:
                html = f'<a href="{url}">{selected_text}</a>'
            else:
                html = f'<a href="{url}">{url}</a>'
            
            # Insert the link
            cursor.insertHtml(html)
            # Move cursor to the end of the inserted link
            cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, 1)
            # Insert a single plain space (unstyled)
            cursor.setCharFormat(QTextCharFormat())
            cursor.insertText(' ')
            self.text_edit.setTextCursor(cursor)

    def remove_hyperlink(self):
        cursor = self.text_edit.textCursor()
        char_format = cursor.charFormat()
        if char_format.isAnchor():
            # Select the anchor (hyperlink) at the cursor
            if not cursor.hasSelection():
                cursor.select(QTextCursor.WordUnderCursor)
            # Get the HTML of the selection
            selected_html = cursor.selection().toHtml()
            # Extract the plain text from the selection
            plain_text = cursor.selectedText()
            # Replace the selection with plain text (removes all HTML/anchor)
            cursor.insertText(plain_text)

    def insert_hover_note(self):
        cursor = self.text_edit.textCursor()
        selected_text = cursor.selectedText() or "Hover Note"
        note, ok = QInputDialog.getText(self, 'Insert Hover Note', 'Enter note to show on hover:')
        if ok and note:
            fmt = QTextCharFormat()
            # Use the current hover note color, default to green if not set
            color = getattr(self, 'hover_note_color', "#39FF14")
            fmt.setForeground(QColor(color))
            fmt.setProperty(1001, note)  # 1001 is a custom property id
            cursor.insertText(selected_text, fmt)
            cursor.setCharFormat(QTextCharFormat())
            self.text_edit.setTextCursor(cursor)

    def set_white_background(self):
        self.setStyleSheet("")
        # Set both normal and selection text color to black
        self.text_edit.setStyleSheet("background-color: #fff; color: #000; border: none; padding: 10px; selection-background-color: #e0e0e0; selection-color: #000; font-family: 'Consolas', 'Monaco', monospace; font-size: 14px; line-height: 1.5;")
        self.hover_note_color = "#6c2eb7"  # Deep purple for hover notes in white mode

    def set_black_background(self):
        self.setStyleSheet("")
        self.text_edit.setStyleSheet("background-color: #000; color: #fff; border: none; padding: 10px; selection-background-color: #1a1a1a; selection-color: #fff; font-family: 'Consolas', 'Monaco', monospace; font-size: 14px; line-height: 1.5;")
        self.hover_note_color = "#39FF14"  # Green for hover notes in black mode

def main():
    app = QApplication(sys.argv)
    # export_circle_icon()  # Remove or comment out after exporting the icon
    # Set tooltip style globally
    QToolTip.setPalette(QPalette(QColor("#000000")))
    app.setStyleSheet("QToolTip { background-color: #000; color: #fff; border: none; }")
    editor = TextEditor()
    editor.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 