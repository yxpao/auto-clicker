"""Compact floating HUD widget for monitoring status and quick stop."""

from __future__ import annotations
from typing import Optional
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton


class FloatingHUD(QWidget):
    """Semi-transparent always-on-top draggable mini HUD."""

    stop_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMinimumSize(280, 48)

        self._drag_pos = QPoint()
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 6, 10, 6)
        layout.setSpacing(10)

        # Status Dot & Text
        self.lbl_status = QLabel("● Ready")
        self.lbl_status.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 12px;")
        layout.addWidget(self.lbl_status, 1)

        # Stop Button
        self.btn_stop = QPushButton("⏹ Stop")
        self.btn_stop.setObjectName("btn_stop")
        self.btn_stop.setFixedSize(70, 30)
        self.btn_stop.clicked.connect(self.stop_requested.emit)
        layout.addWidget(self.btn_stop)

    def set_status(self, text: str, is_active: bool = False, is_error: bool = False) -> None:
        color = "#ef4444" if is_error else ("#10b981" if is_active else "#38bdf8")
        dot = "🔴" if is_error else ("🟢" if is_active else "⚪")
        self.lbl_status.setText(f"{dot} {text}")
        self.lbl_status.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 12px;")
        self.btn_stop.setEnabled(is_active)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and not self._drag_pos.isNull():
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Glassmorphic rounded pill background
        painter.setBrush(QColor(18, 20, 24, 235))
        painter.setPen(QPen(QColor(44, 51, 64), 1.5))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 22, 22)
