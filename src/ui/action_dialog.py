"""Dialog for adding or editing an individual action."""

from __future__ import annotations
from typing import Optional
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QGroupBox,
    QStackedWidget,
    QWidget,
)

from src.core.models import Action, ActionType, MouseButton, ClickType
from src.ui.coordinate_picker import CoordinatePickerOverlay


class ActionDialog(QDialog):
    """Dialog to create or modify an Action step."""

    def __init__(self, parent=None, action: Optional[Action] = None):
        super().__init__(parent)
        self.setWindowTitle("Edit Action" if action else "Add New Action")
        self.setMinimumWidth(440)
        self.setModal(True)

        self._action = action
        self._picker_overlay = CoordinatePickerOverlay()
        self._picker_overlay.coordinate_picked.connect(self._on_coord_picked)

        self._init_ui()
        if action:
            self._load_action_data(action)
        else:
            self._on_type_changed(0)

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Action Type Selector
        type_group = QGroupBox("Action Type")
        type_layout = QVBoxLayout(type_group)

        self.cb_type = QComboBox()
        self.cb_type.addItem("🖱️ Mouse Click", ActionType.CLICK)
        self.cb_type.addItem("🖱️ Mouse Down (Press)", ActionType.MOUSE_DOWN)
        self.cb_type.addItem("🖱️ Mouse Up (Release)", ActionType.MOUSE_UP)
        self.cb_type.addItem("📍 Move Cursor", ActionType.MOVE)
        self.cb_type.addItem("⚙️ Mouse Wheel", ActionType.WHEEL)
        self.cb_type.addItem("⌨️ Key Tap", ActionType.KEY_PRESS)
        self.cb_type.addItem("⌨️ Key Down", ActionType.KEY_DOWN)
        self.cb_type.addItem("⌨️ Key Up", ActionType.KEY_UP)
        self.cb_type.addItem("⏳ Delay / Wait", ActionType.DELAY)
        self.cb_type.addItem("📝 Type Text", ActionType.TEXT)
        self.cb_type.currentIndexChanged.connect(self._on_type_changed)
        type_layout.addWidget(self.cb_type)
        layout.addWidget(type_group)

        # Contextual Config Area (Stacked Widget)
        self.stack = QStackedWidget()

        # Page 0: Mouse Click / Mouse Down / Mouse Up
        self.page_mouse_click = QWidget()
        mc_layout = QFormLayout(self.page_mouse_click)
        self.cb_mouse_btn = QComboBox()
        self.cb_mouse_btn.addItem("Left Button", MouseButton.LEFT)
        self.cb_mouse_btn.addItem("Right Button", MouseButton.RIGHT)
        self.cb_mouse_btn.addItem("Middle Button", MouseButton.MIDDLE)
        self.cb_mouse_btn.addItem("X1 (Side 1)", MouseButton.X1)
        self.cb_mouse_btn.addItem("X2 (Side 2)", MouseButton.X2)

        self.cb_click_type = QComboBox()
        self.cb_click_type.addItem("Single Click", ClickType.SINGLE)
        self.cb_click_type.addItem("Double Click", ClickType.DOUBLE)
        self.cb_click_type.addItem("Hold Down", ClickType.HOLD)

        pos_row = QHBoxLayout()
        self.spin_x = QSpinBox()
        self.spin_x.setRange(0, 99999)
        self.spin_x.setValue(500)
        self.spin_y = QSpinBox()
        self.spin_y.setRange(0, 99999)
        self.spin_y.setValue(500)
        self.btn_pick_pos = QPushButton("🎯 Pick Location")
        self.btn_pick_pos.setObjectName("btn_accent")
        self.btn_pick_pos.clicked.connect(self._open_picker)

        pos_row.addWidget(QLabel("X:"))
        pos_row.addWidget(self.spin_x)
        pos_row.addWidget(QLabel("Y:"))
        pos_row.addWidget(self.spin_y)
        pos_row.addWidget(self.btn_pick_pos)

        mc_layout.addRow("Button:", self.cb_mouse_btn)
        mc_layout.addRow("Click Type:", self.cb_click_type)
        mc_layout.addRow("Position:", pos_row)
        self.stack.addWidget(self.page_mouse_click)

        # Page 1: Move Cursor
        self.page_move = QWidget()
        move_layout = QFormLayout(self.page_move)
        move_pos_row = QHBoxLayout()
        self.spin_move_x = QSpinBox()
        self.spin_move_x.setRange(0, 99999)
        self.spin_move_x.setValue(500)
        self.spin_move_y = QSpinBox()
        self.spin_move_y.setRange(0, 99999)
        self.spin_move_y.setValue(500)
        self.btn_move_pick = QPushButton("🎯 Pick Location")
        self.btn_move_pick.setObjectName("btn_accent")
        self.btn_move_pick.clicked.connect(self._open_picker)
        move_pos_row.addWidget(QLabel("X:"))
        move_pos_row.addWidget(self.spin_move_x)
        move_pos_row.addWidget(QLabel("Y:"))
        move_pos_row.addWidget(self.spin_move_y)
        move_pos_row.addWidget(self.btn_move_pick)
        move_layout.addRow("Target Position:", move_pos_row)
        self.stack.addWidget(self.page_move)

        # Page 2: Wheel
        self.page_wheel = QWidget()
        wheel_layout = QFormLayout(self.page_wheel)
        self.spin_wheel_dy = QSpinBox()
        self.spin_wheel_dy.setRange(-100, 100)
        self.spin_wheel_dy.setValue(1)
        self.spin_wheel_dx = QSpinBox()
        self.spin_wheel_dx.setRange(-100, 100)
        self.spin_wheel_dx.setValue(0)
        wheel_layout.addRow("Vertical Scroll (Steps):", self.spin_wheel_dy)
        wheel_layout.addRow("Horizontal Scroll (Steps):", self.spin_wheel_dx)
        self.stack.addWidget(self.page_wheel)

        # Page 3: Key Press / Down / Up
        self.page_key = QWidget()
        key_layout = QFormLayout(self.page_key)
        self.txt_key = QLineEdit()
        self.txt_key.setPlaceholderText("e.g. 'a', 'enter', 'ctrl', 'shift', 'f5'")
        key_layout.addRow("Key Name:", self.txt_key)
        self.stack.addWidget(self.page_key)

        # Page 4: Text
        self.page_text = QWidget()
        text_layout = QFormLayout(self.page_text)
        self.txt_text = QLineEdit()
        self.txt_text.setPlaceholderText("Enter string to type...")
        text_layout.addRow("Text String:", self.txt_text)
        self.stack.addWidget(self.page_text)

        # Page 5: Delay (Empty, handled by general timing box)
        self.page_delay = QWidget()
        self.stack.addWidget(self.page_delay)

        layout.addWidget(self.stack)

        # Timing Settings Group
        timing_group = QGroupBox("Timing Settings")
        timing_layout = QFormLayout(timing_group)
        self.spin_delay = QDoubleSpinBox()
        self.spin_delay.setRange(0.0, 999999.0)
        self.spin_delay.setValue(50.0)
        self.spin_delay.setSuffix(" ms")

        self.spin_duration = QDoubleSpinBox()
        self.spin_duration.setRange(0.0, 999999.0)
        self.spin_duration.setValue(0.0)
        self.spin_duration.setSuffix(" ms")

        timing_layout.addRow("Pre-Action Delay:", self.spin_delay)
        timing_layout.addRow("Hold Duration:", self.spin_duration)
        layout.addWidget(timing_group)

        # Buttons
        btn_box = QHBoxLayout()
        self.btn_save = QPushButton("Save Action")
        self.btn_save.setObjectName("btn_start")
        self.btn_save.clicked.connect(self.accept)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)

        btn_box.addStretch()
        btn_box.addWidget(self.btn_cancel)
        btn_box.addWidget(self.btn_save)
        layout.addLayout(btn_box)

    def _on_type_changed(self, index: int) -> None:
        atype = self.cb_type.currentData()
        if atype in (ActionType.CLICK, ActionType.MOUSE_DOWN, ActionType.MOUSE_UP):
            self.stack.setCurrentIndex(0)
            self.cb_click_type.setEnabled(atype == ActionType.CLICK)
        elif atype == ActionType.MOVE:
            self.stack.setCurrentIndex(1)
        elif atype == ActionType.WHEEL:
            self.stack.setCurrentIndex(2)
        elif atype in (ActionType.KEY_PRESS, ActionType.KEY_DOWN, ActionType.KEY_UP):
            self.stack.setCurrentIndex(3)
        elif atype == ActionType.TEXT:
            self.stack.setCurrentIndex(4)
        elif atype == ActionType.DELAY:
            self.stack.setCurrentIndex(5)

    def _open_picker(self) -> None:
        self.hide()
        self._picker_overlay.start_picking()

    def _on_coord_picked(self, x: int, y: int) -> None:
        self.spin_x.setValue(x)
        self.spin_y.setValue(y)
        self.spin_move_x.setValue(x)
        self.spin_move_y.setValue(y)
        self.show()
        self.raise_()
        self.activateWindow()

    def _load_action_data(self, a: Action) -> None:
        idx = self.cb_type.findData(a.action_type)
        if idx >= 0:
            self.cb_type.setCurrentIndex(idx)

        if a.button:
            b_idx = self.cb_mouse_btn.findData(a.button)
            if b_idx >= 0:
                self.cb_mouse_btn.setCurrentIndex(b_idx)

        c_idx = self.cb_click_type.findData(a.click_type)
        if c_idx >= 0:
            self.cb_click_type.setCurrentIndex(c_idx)

        if a.x is not None:
            self.spin_x.setValue(a.x)
            self.spin_move_x.setValue(a.x)
        if a.y is not None:
            self.spin_y.setValue(a.y)
            self.spin_move_y.setValue(a.y)

        self.spin_wheel_dx.setValue(a.wheel_dx)
        self.spin_wheel_dy.setValue(a.wheel_dy)

        if a.key:
            self.txt_key.setText(a.key)
        if a.text:
            self.txt_text.setText(a.text)

        self.spin_delay.setValue(a.delay_ms)
        self.spin_duration.setValue(a.duration_ms)

    def get_action(self) -> Action:
        atype = self.cb_type.currentData()
        action_id = self._action.id if self._action else None

        action = Action(
            id=action_id or Action().id,
            action_type=atype,
            delay_ms=self.spin_delay.value(),
            duration_ms=self.spin_duration.value(),
        )

        if atype in (ActionType.CLICK, ActionType.MOUSE_DOWN, ActionType.MOUSE_UP):
            action.button = self.cb_mouse_btn.currentData()
            action.click_type = self.cb_click_type.currentData()
            action.x = self.spin_x.value()
            action.y = self.spin_y.value()
        elif atype == ActionType.MOVE:
            action.x = self.spin_move_x.value()
            action.y = self.spin_move_y.value()
        elif atype == ActionType.WHEEL:
            action.wheel_dx = self.spin_wheel_dx.value()
            action.wheel_dy = self.spin_wheel_dy.value()
        elif atype in (ActionType.KEY_PRESS, ActionType.KEY_DOWN, ActionType.KEY_UP):
            action.key = self.txt_key.text().strip()
        elif atype == ActionType.TEXT:
            action.text = self.txt_text.text()

        return action
