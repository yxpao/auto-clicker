"""Macro Studio Tab: Record, Select, Edit, and Playback Sequences."""

from __future__ import annotations
from typing import Optional, List
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
    QLabel,
    QSpinBox,
    QDoubleSpinBox,
    QSlider,
    QGroupBox,
    QCheckBox,
    QProgressBar,
    QFileDialog,
    QMessageBox,
    QFrame,
)

from src.core.models import MacroSequence, Action, ActionType, MouseButton, ClickType
from src.core.recorder import Recorder
from src.core.player import Player
from src.core.storage import StorageManager
from src.ui.action_dialog import ActionDialog
from src.ui.batch_edit_dialog import BatchEditDialog


class MacroStudioTab(QWidget):
    """Studio interface for recording, inspecting, editing, and playing macros."""

    status_changed = pyqtSignal(bool, str)  # is_active, status_text

    def __init__(self, recorder: Recorder, player: Player, parent=None):
        super().__init__(parent)
        self.recorder = recorder
        self.player = player
        self.macro = MacroSequence(name="New Macro")

        # Connect core callbacks
        self.recorder.on_action_recorded = self._on_action_recorded
        self.recorder.on_status_change = self._on_recorder_status_change

        self.player.on_step_start = self._on_play_step_start
        self.player.on_step_finished = self._on_play_step_finished
        self.player.on_loop_finished = self._on_play_loop_finished
        self.player.on_status_change = self._on_player_status_change

        self._active_play_row = -1
        self._init_ui()
        self._refresh_table()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(14, 14, 14, 14)

        # 1. Top Global Control Bar
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)

        self.btn_record = QPushButton("RECORD  (F7)")
        self.btn_record.setObjectName("btn_record")
        self.btn_record.setFixedHeight(36)
        self.btn_record.clicked.connect(self.toggle_recording)

        self.btn_play_all = QPushButton("PLAY ALL  (F9)")
        self.btn_play_all.setObjectName("btn_play")
        self.btn_play_all.setFixedHeight(36)
        self.btn_play_all.clicked.connect(self.play_all)

        self.btn_play_sel = QPushButton("Play Selected")
        self.btn_play_sel.setFixedHeight(36)
        self.btn_play_sel.clicked.connect(self.play_selected)

        self.btn_pause = QPushButton("Pause")
        self.btn_pause.setFixedHeight(36)
        self.btn_pause.setEnabled(False)
        self.btn_pause.clicked.connect(self.toggle_pause)

        self.btn_stop = QPushButton("STOP")
        self.btn_stop.setObjectName("btn_stop")
        self.btn_stop.setFixedHeight(36)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_all)

        self.btn_clear = QPushButton("Clear")
        self.btn_clear.setFixedHeight(36)
        self.btn_clear.clicked.connect(self.clear_macro)

        top_bar.addWidget(self.btn_record)
        top_bar.addWidget(self.btn_play_all)
        top_bar.addWidget(self.btn_play_sel)
        top_bar.addWidget(self.btn_pause)
        top_bar.addWidget(self.btn_stop)
        top_bar.addSpacing(10)
        top_bar.addWidget(self.btn_clear)
        main_layout.addLayout(top_bar)

        # 2. Main Middle Area: Action Table + Right Action Tools
        mid_layout = QHBoxLayout()
        mid_layout.setSpacing(12)

        # Action Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["#", "Type", "Details", "Delay", "Duration", "✓"])
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.table.cellDoubleClicked.connect(self._on_table_double_click)
        mid_layout.addWidget(self.table, 4)

        # Right Action Tool Sidebar
        sidebar = QVBoxLayout()
        sidebar.setSpacing(8)

        lbl_tools = QLabel("STEP ACTIONS")
        lbl_tools.setObjectName("lbl_stat_label")
        sidebar.addWidget(lbl_tools)

        self.btn_add_action = QPushButton("Insert Action")
        self.btn_add_action.clicked.connect(self.insert_action)
        sidebar.addWidget(self.btn_add_action)

        self.btn_edit_action = QPushButton("Edit Selected")
        self.btn_edit_action.clicked.connect(self.edit_selected_action)
        sidebar.addWidget(self.btn_edit_action)

        self.btn_duplicate = QPushButton("Duplicate")
        self.btn_duplicate.clicked.connect(self.duplicate_selected)
        sidebar.addWidget(self.btn_duplicate)

        self.btn_delete = QPushButton("Delete")
        self.btn_delete.clicked.connect(self.delete_selected)
        sidebar.addWidget(self.btn_delete)

        sidebar.addSpacing(10)
        lbl_order = QLabel("REORDER")
        lbl_order.setObjectName("lbl_stat_label")
        sidebar.addWidget(lbl_order)

        self.btn_move_up = QPushButton("Move Up")
        self.btn_move_up.clicked.connect(self.move_selected_up)
        sidebar.addWidget(self.btn_move_up)

        self.btn_move_down = QPushButton("Move Down")
        self.btn_move_down.clicked.connect(self.move_selected_down)
        sidebar.addWidget(self.btn_move_down)

        sidebar.addSpacing(10)
        self.btn_batch = QPushButton("Batch Edit...")
        self.btn_batch.setObjectName("btn_accent")
        self.btn_batch.clicked.connect(self.open_batch_edit)
        sidebar.addWidget(self.btn_batch)

        sidebar.addStretch()
        mid_layout.addLayout(sidebar, 1)
        main_layout.addLayout(mid_layout, 1)

        # 3. Bottom Playback & Recording Settings Area
        bottom_box = QGroupBox("Playback && Recording Options")
        bot_layout = QHBoxLayout(bottom_box)
        bot_layout.setSpacing(20)

        # Speed Multiplier Control
        speed_vbox = QVBoxLayout()
        self.lbl_speed = QLabel("Speed: 1.0x")
        self.lbl_speed.setObjectName("lbl_stat_label")
        self.slider_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_speed.setRange(1, 50)  # 0.1x to 5.0x (val / 10)
        self.slider_speed.setValue(10)
        self.slider_speed.valueChanged.connect(self._on_speed_slider_changed)
        speed_vbox.addWidget(self.lbl_speed)
        speed_vbox.addWidget(self.slider_speed)
        bot_layout.addLayout(speed_vbox, 2)

        # Loop Controls
        loop_vbox = QVBoxLayout()
        loop_row1 = QHBoxLayout()
        loop_row1.addWidget(QLabel("Repeat:"))
        self.spin_loops = QSpinBox()
        self.spin_loops.setRange(0, 99999)
        self.spin_loops.setValue(1)
        self.spin_loops.setSpecialValueText("Infinite (0)")
        loop_row1.addWidget(self.spin_loops)
        loop_vbox.addLayout(loop_row1)

        loop_row2 = QHBoxLayout()
        loop_row2.addWidget(QLabel("Loop Gap:"))
        self.spin_loop_delay = QDoubleSpinBox()
        self.spin_loop_delay.setRange(0.0, 999999.0)
        self.spin_loop_delay.setValue(100.0)
        self.spin_loop_delay.setSuffix(" ms")
        loop_row2.addWidget(self.spin_loop_delay)
        loop_vbox.addLayout(loop_row2)
        bot_layout.addLayout(loop_vbox, 2)

        # Recording Filters
        filter_vbox = QVBoxLayout()
        filter_row1 = QHBoxLayout()
        self.chk_rec_clicks = QCheckBox("Record Clicks")
        self.chk_rec_clicks.setChecked(True)
        self.chk_rec_moves = QCheckBox("Record Moves")
        self.chk_rec_moves.setChecked(False)
        filter_row1.addWidget(self.chk_rec_clicks)
        filter_row1.addWidget(self.chk_rec_moves)

        filter_row2 = QHBoxLayout()
        self.chk_rec_wheel = QCheckBox("Record Wheel")
        self.chk_rec_wheel.setChecked(True)
        self.chk_rec_keys = QCheckBox("Record Keys")
        self.chk_rec_keys.setChecked(True)
        filter_row2.addWidget(self.chk_rec_wheel)
        filter_row2.addWidget(self.chk_rec_keys)

        filter_vbox.addLayout(filter_row1)
        filter_vbox.addLayout(filter_row2)
        bot_layout.addLayout(filter_vbox, 2)

        main_layout.addWidget(bottom_box)

        # 4. Progress & Status Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(18)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Ready (%p%)")
        main_layout.addWidget(self.progress_bar)

    def _on_speed_slider_changed(self, val: int) -> None:
        speed = val / 10.0
        self.macro.speed_multiplier = speed
        self.lbl_speed.setText(f"Speed: {speed:.1f}x")

    def _get_badge_style(self, atype: ActionType) -> tuple[str, str]:
        """Returns badge text and color for action type."""
        mapping = {
            ActionType.CLICK: ("Click", "#6366f1"),
            ActionType.MOUSE_DOWN: ("Down", "#818cf8"),
            ActionType.MOUSE_UP: ("Up", "#818cf8"),
            ActionType.MOVE: ("Move", "#2dd4bf"),
            ActionType.WHEEL: ("Wheel", "#a78bfa"),
            ActionType.KEY_PRESS: ("Key Tap", "#c084fc"),
            ActionType.KEY_DOWN: ("Key Down", "#a855f7"),
            ActionType.KEY_UP: ("Key Up", "#a855f7"),
            ActionType.DELAY: ("Delay", "#f59e0b"),
            ActionType.TEXT: ("Text", "#22c55e"),
        }
        return mapping.get(atype, ("Action", "#9ba1b0"))

    def _refresh_table(self) -> None:
        self.table.setRowCount(len(self.macro.actions))

        for idx, action in enumerate(self.macro.actions):
            # 0: Index
            item_idx = QTableWidgetItem(f"{idx + 1}")
            item_idx.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(idx, 0, item_idx)

            # 1: Badge / Action Type
            badge_text, badge_color = self._get_badge_style(action.action_type)
            item_type = QTableWidgetItem(badge_text)
            item_type.setForeground(QColor(badge_color))
            font = item_type.font()
            font.setBold(True)
            item_type.setFont(font)
            self.table.setItem(idx, 1, item_type)

            # 2: Summary / Details
            item_details = QTableWidgetItem(action.summary())
            self.table.setItem(idx, 2, item_details)

            # 3: Delay
            item_delay = QTableWidgetItem(f"{action.delay_ms:.1f}")
            item_delay.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(idx, 3, item_delay)

            # 4: Duration
            dur_str = f"{action.duration_ms:.1f}" if action.duration_ms > 0 else "-"
            item_dur = QTableWidgetItem(dur_str)
            item_dur.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(idx, 4, item_dur)

            # 5: Enabled / Active
            chk_active = QTableWidgetItem("✓" if action.enabled else "✕")
            chk_active.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            chk_active.setForeground(QColor("#10b981" if action.enabled else "#ef4444"))
            self.table.setItem(idx, 5, chk_active)

    def _on_table_double_click(self, row: int, col: int) -> None:
        if 0 <= row < len(self.macro.actions):
            self.edit_action_at(row)

    def insert_action(self) -> None:
        dlg = ActionDialog(self)
        if dlg.exec():
            new_action = dlg.get_action()
            selected = self._get_selected_rows()
            insert_pos = (selected[0] + 1) if selected else len(self.macro.actions)
            self.macro.actions.insert(insert_pos, new_action)
            self._refresh_table()
            self.table.selectRow(insert_pos)

    def edit_action_at(self, row: int) -> None:
        if 0 <= row < len(self.macro.actions):
            dlg = ActionDialog(self, action=self.macro.actions[row])
            if dlg.exec():
                self.macro.actions[row] = dlg.get_action()
                self._refresh_table()
                self.table.selectRow(row)

    def edit_selected_action(self) -> None:
        selected = self._get_selected_rows()
        if selected:
            self.edit_action_at(selected[0])

    def duplicate_selected(self) -> None:
        selected = self._get_selected_rows()
        if not selected:
            return
        for row in reversed(selected):
            orig = self.macro.actions[row]
            cloned = Action.from_dict(orig.to_dict())
            cloned.id = Action().id
            self.macro.actions.insert(row + 1, cloned)
        self._refresh_table()

    def delete_selected(self) -> None:
        selected = self._get_selected_rows()
        if not selected:
            return
        for row in reversed(selected):
            del self.macro.actions[row]
        self._refresh_table()

    def move_selected_up(self) -> None:
        selected = self._get_selected_rows()
        if not selected or selected[0] == 0:
            return
        for row in selected:
            self.macro.actions[row - 1], self.macro.actions[row] = (
                self.macro.actions[row],
                self.macro.actions[row - 1],
            )
        self._refresh_table()
        for row in selected:
            self.table.selectRow(row - 1)

    def move_selected_down(self) -> None:
        selected = self._get_selected_rows()
        if not selected or selected[-1] >= len(self.macro.actions) - 1:
            return
        for row in reversed(selected):
            self.macro.actions[row + 1], self.macro.actions[row] = (
                self.macro.actions[row],
                self.macro.actions[row + 1],
            )
        self._refresh_table()
        for row in selected:
            self.table.selectRow(row + 1)

    def open_batch_edit(self) -> None:
        if not self.macro.actions:
            QMessageBox.information(self, "Batch Edit", "Macro contains no actions to edit.")
            return
        selected = self._get_selected_rows()
        indices = selected if selected else None
        dlg = BatchEditDialog(self.macro, selected_indices=indices, parent=self)
        if dlg.exec():
            self._refresh_table()

    def clear_macro(self) -> None:
        if not self.macro.actions:
            return
        res = QMessageBox.question(
            self,
            "Clear Macro",
            "Are you sure you want to clear all actions?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if res == QMessageBox.StandardButton.Yes:
            self.macro.actions.clear()
            self._refresh_table()
            self.progress_bar.setValue(0)

    def _get_selected_rows(self) -> List[int]:
        indexes = self.table.selectionModel().selectedRows()
        return sorted([idx.row() for idx in indexes])

    # Recording Control
    def start_recording(self) -> None:
        if self.player.is_playing:
            return
        self.recorder.record_clicks = self.chk_rec_clicks.isChecked()
        self.recorder.record_moves = self.chk_rec_moves.isChecked()
        self.recorder.record_wheel = self.chk_rec_wheel.isChecked()
        self.recorder.record_keyboard = self.chk_rec_keys.isChecked()

        self.recorder.start()

    def stop_recording(self) -> None:
        new_macro = self.recorder.stop()
        if new_macro.actions:
            self.macro = new_macro
            self._refresh_table()

    def toggle_recording(self) -> None:
        if self.recorder.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def _on_action_recorded(self, action: Action, count: int) -> None:
        # Real-time incremental table addition
        self.macro.actions.append(action)
        self._refresh_table()
        self.table.scrollToBottom()

    def _on_recorder_status_change(self, is_recording: bool) -> None:
        self.btn_record.setText("STOP RECORD" if is_recording else "RECORD  (F7)")
        self.btn_record.setEnabled(True)
        self.btn_play_all.setEnabled(not is_recording)
        self.btn_play_sel.setEnabled(not is_recording)
        self.btn_stop.setEnabled(is_recording)

        txt = f"Recording ({len(self.macro.actions)} actions)" if is_recording else "Ready"
        self.status_changed.emit(is_recording, txt)

    # Playback Control
    def play_all(self) -> None:
        if not self.macro.actions:
            return
        self._start_playback(selected_only=False)

    def play_selected(self) -> None:
        selected = self._get_selected_rows()
        if not selected:
            QMessageBox.information(self, "Play Selected", "Please select one or more actions to play.")
            return
        self._start_playback(selected_only=True, selected_indices=selected)

    def _start_playback(self, selected_only: bool = False, selected_indices: Optional[List[int]] = None) -> None:
        if self.recorder.is_recording or self.player.is_playing:
            return

        self.macro.speed_multiplier = self.slider_speed.value() / 10.0
        self.macro.repeat_count = self.spin_loops.value()
        self.macro.delay_between_loops_ms = self.spin_loop_delay.value()

        self.player.play(
            macro=self.macro,
            selected_indices=selected_indices if selected_only else None,
            speed_multiplier=self.macro.speed_multiplier,
            repeat_count=self.macro.repeat_count,
            delay_between_loops_ms=self.macro.delay_between_loops_ms,
        )

    def toggle_pause(self) -> None:
        if not self.player.is_playing:
            return
        if self.player.is_paused:
            self.player.resume()
            self.btn_pause.setText("Pause")
        else:
            self.player.pause()
            self.btn_pause.setText("Resume")

    def stop_all(self) -> None:
        if self.recorder.is_recording:
            self.stop_recording()
        if self.player.is_playing:
            self.player.stop()

    def toggle_playback(self) -> None:
        if self.player.is_playing:
            self.player.stop()
        else:
            self.play_all()

    def _on_play_step_start(self, step_idx: int, action: Action, current_loop: int, total_loops: int) -> None:
        self._active_play_row = step_idx
        # Visual Playhead highlight
        self.table.selectRow(step_idx)

        total_actions = len(self.macro.actions)
        loop_info = f"Loop {current_loop}/{total_loops if total_loops > 0 else '∞'}"
        self.progress_bar.setFormat(f"Playing Step {step_idx + 1}/{total_actions} ({loop_info})")
        if total_actions > 0:
            self.progress_bar.setValue(int(((step_idx + 1) / total_actions) * 100))

    def _on_play_step_finished(self, step_idx: int, action: Action) -> None:
        pass

    def _on_play_loop_finished(self, current_loop: int, total_loops: int) -> None:
        pass

    def _on_player_status_change(self, is_playing: bool) -> None:
        self.btn_play_all.setEnabled(not is_playing)
        self.btn_play_sel.setEnabled(not is_playing)
        self.btn_record.setEnabled(not is_playing)
        self.btn_pause.setEnabled(is_playing)
        self.btn_pause.setText("Pause")
        self.btn_stop.setEnabled(is_playing)

        if not is_playing:
            self.progress_bar.setFormat("Ready (%p%)")
            self.progress_bar.setValue(100)

        status_txt = "Playing Macro Sequence..." if is_playing else "Ready"
        self.status_changed.emit(is_playing, status_txt)
