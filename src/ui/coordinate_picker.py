"""Full-screen interactive coordinate picker overlay."""

from __future__ import annotations
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QCursor
from PyQt6.QtWidgets import QWidget, QApplication


class CoordinatePickerOverlay(QWidget):
    """Full-screen transparent overlay for pinpointing screen coordinates."""

    coordinate_picked = pyqtSignal(int, int)
    cancelled = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)

        self._mouse_pos = QPoint(0, 0)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_cursor_pos)

    def start_picking(self) -> None:
        # Cover all connected virtual screens
        geo = QApplication.primaryScreen().virtualGeometry()
        self.setGeometry(geo)
        self._update_cursor_pos()
        self.showFullScreen()
        self.raise_()
        self.activateWindow()
        self._timer.start(16)  # ~60 fps cursor tracking

    def _update_cursor_pos(self) -> None:
        pos = QCursor.pos()
        if pos != self._mouse_pos:
            self._mouse_pos = pos
            self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._finish(self._mouse_pos.x(), self._mouse_pos.y())
        elif event.button() == Qt.MouseButton.RightButton:
            self._cancel()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self._finish(self._mouse_pos.x(), self._mouse_pos.y())
        elif event.key() == Qt.Key.Key_Escape:
            self._cancel()

    def _finish(self, x: int, y: int) -> None:
        self._timer.stop()
        self.hide()
        self.coordinate_picked.emit(x, y)

    def _cancel(self) -> None:
        self._timer.stop()
        self.hide()
        self.cancelled.emit()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Subtle dark tint over screen
        painter.fillRect(self.rect(), QColor(0, 0, 0, 40))

        mx, my = self._mouse_pos.x(), self._mouse_pos.y()

        # Crosshair lines
        pen = QPen(QColor(56, 189, 248, 200), 1, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawLine(0, my, self.width(), my)
        painter.drawLine(mx, 0, mx, self.height())

        # Target center ring
        pen_ring = QPen(QColor(56, 189, 248, 240), 2)
        painter.setPen(pen_ring)
        painter.drawEllipse(QPoint(mx, my), 18, 18)

        # Inner dot
        painter.setBrush(QColor(239, 68, 68, 220))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPoint(mx, my), 3, 3)

        # Coordinates info bubble
        info_text = f"X: {mx}   Y: {my}\n(Click or Press Space to Pick | Esc to Cancel)"
        font = QFont("Segoe UI", 10, QFont.Weight.Bold)
        painter.setFont(font)

        # Box dimensions
        box_w = 280
        box_h = 52
        box_x = mx + 25
        box_y = my + 25

        # Keep box inside screen bounds
        if box_x + box_w > self.width():
            box_x = mx - box_w - 25
        if box_y + box_h > self.height():
            box_y = my - box_h - 25

        # Draw HUD Box
        painter.setBrush(QColor(18, 20, 24, 230))
        painter.setPen(QPen(QColor(56, 189, 248), 1.5))
        painter.drawRoundedRect(box_x, box_y, box_w, box_h, 8, 8)

        # Text
        painter.setPen(QColor(241, 245, 249))
        painter.drawText(
            box_x + 12,
            box_y + 8,
            box_w - 24,
            box_h - 16,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            info_text,
        )
