"""Classic Auto Clicker UI Tab."""

from __future__ import annotations
from typing import Optional
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
    QRadioButton,
    QButtonGroup,
    QCheckBox,
    QPushButton,
    QFrame,
)

from src.core.models import AutoClickerConfig, MouseButton, ClickType
from src.core.autoclicker import AutoClicker
from src.ui.coordinate_picker import CoordinatePickerOverlay


class AutoClickerTab(QWidget):
    """Tab component implementing classic Auto Clicker controls and real-time telemetry."""

    status_changed = pyqtSignal(bool, str)  # is_running, status_text

    def __init__(self, autoclicker: AutoClicker, parent=None):
        super().__init__(parent)
        self.autoclicker = autoclicker
        self.autoclicker.on_click_callback = self._on_click_update
        self.autoclicker.on_status_callback = self._on_status_update

        self._picker_overlay = CoordinatePickerOverlay()
        self._picker_overlay.coordinate_picked.connect(self._on_coordinate_picked)

        self._test_clicks = 0
        self._init_ui()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(14, 14, 14, 14)

        # Top row: Interval Settings & Click Options
        row1 = QHBoxLayout()
        row1.setSpacing(14)

        # 1. Click Interval Group
        grp_interval = QGroupBox("⏱️ Click Interval")
        grid_interval = QGridLayout(grp_interval)
        grid_interval.setSpacing(8)

        self.spin_hours = QSpinBox()
        self.spin_hours.setRange(0, 999)
        self.spin_hours.setValue(0)
        self.spin_hours.setSuffix(" hrs")

        self.spin_mins = QSpinBox()
        self.spin_mins.setRange(0, 59)
        self.spin_mins.setValue(0)
        self.spin_mins.setSuffix(" mins")

        self.spin_secs = QSpinBox()
        self.spin_secs.setRange(0, 59)
        self.spin_secs.setValue(0)
        self.spin_secs.setSuffix(" secs")

        self.spin_ms = QSpinBox()
        self.spin_ms.setRange(1, 999999)
        self.spin_ms.setValue(100)
        self.spin_ms.setSuffix(" ms")

        grid_interval.addWidget(QLabel("Hours:"), 0, 0)
        grid_interval.addWidget(self.spin_hours, 0, 1)
        grid_interval.addWidget(QLabel("Minutes:"), 0, 2)
        grid_interval.addWidget(self.spin_mins, 0, 3)

        grid_interval.addWidget(QLabel("Seconds:"), 1, 0)
        grid_interval.addWidget(self.spin_secs, 1, 1)
        grid_interval.addWidget(QLabel("Milliseconds:"), 1, 2)
        grid_interval.addWidget(self.spin_ms, 1, 3)

        row1.addWidget(grp_interval, 3)

        # 2. Click Options Group
        grp_options = QGroupBox("🖱️ Click Options")
        grid_options = QGridLayout(grp_options)
        grid_options.setSpacing(8)

        self.cb_btn = QComboBox()
        self.cb_btn.addItem("Left Button", MouseButton.LEFT)
        self.cb_btn.addItem("Right Button", MouseButton.RIGHT)
        self.cb_btn.addItem("Middle Button", MouseButton.MIDDLE)
        self.cb_btn.addItem("X1 (Side 1)", MouseButton.X1)
        self.cb_btn.addItem("X2 (Side 2)", MouseButton.X2)

        self.cb_type = QComboBox()
        self.cb_type.addItem("Single Click", ClickType.SINGLE)
        self.cb_type.addItem("Double Click", ClickType.DOUBLE)
        self.cb_type.addItem("Hold Down", ClickType.HOLD)

        grid_options.addWidget(QLabel("Mouse Button:"), 0, 0)
        grid_options.addWidget(self.cb_btn, 0, 1)
        grid_options.addWidget(QLabel("Click Type:"), 1, 0)
        grid_options.addWidget(self.cb_type, 1, 1)

        row1.addWidget(grp_options, 2)
        main_layout.addLayout(row1)

        # Middle row: Repeat & Position
        row2 = QHBoxLayout()
        row2.setSpacing(14)

        # 3. Click Repeat Group
        grp_repeat = QGroupBox("🔁 Click Repeat")
        vbox_repeat = QVBoxLayout(grp_repeat)
        vbox_repeat.setSpacing(8)

        self.rb_infinite = QRadioButton("Repeat until stopped (Infinite)")
        self.rb_infinite.setChecked(True)
        self.rb_count = QRadioButton("Repeat")

        self.btn_grp_repeat = QButtonGroup(self)
        self.btn_grp_repeat.addButton(self.rb_infinite, 1)
        self.btn_grp_repeat.addButton(self.rb_count, 2)

        count_row = QHBoxLayout()
        count_row.addWidget(self.rb_count)
        self.spin_count = QSpinBox()
        self.spin_count.setRange(1, 9999999)
        self.spin_count.setValue(100)
        self.spin_count.setSuffix(" times")
        count_row.addWidget(self.spin_count)
        count_row.addStretch()

        vbox_repeat.addWidget(self.rb_infinite)
        vbox_repeat.addLayout(count_row)
        row2.addWidget(grp_repeat, 1)

        # 4. Cursor Position Group
        grp_pos = QGroupBox("📍 Cursor Position")
        vbox_pos = QVBoxLayout(grp_pos)
        vbox_pos.setSpacing(8)

        self.rb_current_pos = QRadioButton("Current cursor location")
        self.rb_current_pos.setChecked(True)
        self.rb_fixed_pos = QRadioButton("Fixed coordinate:")

        self.btn_grp_pos = QButtonGroup(self)
        self.btn_grp_pos.addButton(self.rb_current_pos, 1)
        self.btn_grp_pos.addButton(self.rb_fixed_pos, 2)

        coord_row = QHBoxLayout()
        coord_row.addWidget(self.rb_fixed_pos)
        coord_row.addWidget(QLabel("X:"))
        self.spin_fixed_x = QSpinBox()
        self.spin_fixed_x.setRange(0, 99999)
        self.spin_fixed_x.setValue(500)
        coord_row.addWidget(self.spin_fixed_x)

        coord_row.addWidget(QLabel("Y:"))
        self.spin_fixed_y = QSpinBox()
        self.spin_fixed_y.setRange(0, 99999)
        self.spin_fixed_y.setValue(500)
        coord_row.addWidget(self.spin_fixed_y)

        self.btn_pick = QPushButton("🎯 Pick (F8)")
        self.btn_pick.setObjectName("btn_accent")
        self.btn_pick.clicked.connect(self.start_picking_coords)
        coord_row.addWidget(self.btn_pick)

        vbox_pos.addWidget(self.rb_current_pos)
        vbox_pos.addLayout(coord_row)
        row2.addWidget(grp_pos, 1)
        main_layout.addLayout(row2)

        # Anti-Detection / Humanizer Settings
        grp_anti = QGroupBox("🛡️ Anti-Detection & Humanizer (Optional)")
        anti_layout = QHBoxLayout(grp_anti)
        anti_layout.setSpacing(16)

        self.chk_rand_interval = QCheckBox("Randomize interval (± ms):")
        self.spin_rand_ms = QDoubleSpinBox()
        self.spin_rand_ms.setRange(1.0, 500.0)
        self.spin_rand_ms.setValue(10.0)
        self.spin_rand_ms.setSuffix(" ms")

        self.chk_rand_loc = QCheckBox("Randomize location (± px):")
        self.spin_rand_px = QSpinBox()
        self.spin_rand_px.setRange(1, 50)
        self.spin_rand_px.setValue(3)
        self.spin_rand_px.setSuffix(" px")

        anti_layout.addWidget(self.chk_rand_interval)
        anti_layout.addWidget(self.spin_rand_ms)
        anti_layout.addSpacing(16)
        anti_layout.addWidget(self.chk_rand_loc)
        anti_layout.addWidget(self.spin_rand_px)
        anti_layout.addStretch()
        main_layout.addWidget(grp_anti)

        # Telemetry Card & Stats
        telemetry_frame = QFrame()
        telemetry_frame.setObjectName("card_telemetry")
        tel_layout = QHBoxLayout(telemetry_frame)
        tel_layout.setSpacing(12)

        # CPS stat
        cps_col = QVBoxLayout()
        cps_col.setSpacing(1)
        lbl_cps_label = QLabel("CLICKS / SEC")
        lbl_cps_label.setObjectName("lbl_stat_label")
        self.lbl_cps = QLabel("0.0")
        self.lbl_cps.setObjectName("lbl_stat_primary")
        cps_col.addWidget(lbl_cps_label)
        cps_col.addWidget(self.lbl_cps)
        tel_layout.addLayout(cps_col)

        tel_layout.addStretch()

        # Total clicks stat
        clicks_col = QVBoxLayout()
        clicks_col.setSpacing(1)
        lbl_clicks_label = QLabel("TOTAL CLICKS")
        lbl_clicks_label.setObjectName("lbl_stat_label")
        self.lbl_clicks = QLabel("0")
        self.lbl_clicks.setObjectName("lbl_stat_value")
        clicks_col.addWidget(lbl_clicks_label)
        clicks_col.addWidget(self.lbl_clicks)
        tel_layout.addLayout(clicks_col)

        tel_layout.addStretch()

        # Elapsed time stat
        time_col = QVBoxLayout()
        time_col.setSpacing(1)
        lbl_time_label = QLabel("ELAPSED")
        lbl_time_label.setObjectName("lbl_stat_label")
        self.lbl_time = QLabel("00:00.0")
        self.lbl_time.setObjectName("lbl_stat_value")
        time_col.addWidget(lbl_time_label)
        time_col.addWidget(self.lbl_time)
        tel_layout.addLayout(time_col)

        tel_layout.addStretch()

        # In-app click test button
        self.btn_test = QPushButton("Test Click Counter (0)")
        self.btn_test.clicked.connect(self._on_test_button_clicked)
        tel_layout.addWidget(self.btn_test)

        main_layout.addWidget(telemetry_frame)

        # Bottom Action Control Bar
        ctrl_bar = QHBoxLayout()
        ctrl_bar.setSpacing(10)

        self.btn_start = QPushButton("START  (F6)")
        self.btn_start.setObjectName("btn_start")
        self.btn_start.setFixedHeight(42)
        self.btn_start.clicked.connect(self.start_clicking)

        self.btn_stop = QPushButton("STOP  (F6)")
        self.btn_stop.setObjectName("btn_stop")
        self.btn_stop.setFixedHeight(42)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_clicking)

        ctrl_bar.addWidget(self.btn_start, 1)
        ctrl_bar.addWidget(self.btn_stop, 1)
        main_layout.addLayout(ctrl_bar)

    def get_current_config(self) -> AutoClickerConfig:
        return AutoClickerConfig(
            hours=self.spin_hours.value(),
            minutes=self.spin_mins.value(),
            seconds=self.spin_secs.value(),
            milliseconds=self.spin_ms.value(),
            button=self.cb_btn.currentData(),
            click_type=self.cb_type.currentData(),
            repeat_type="infinite" if self.rb_infinite.isChecked() else "count",
            repeat_count=self.spin_count.value(),
            location_type="current" if self.rb_current_pos.isChecked() else "fixed",
            fixed_x=self.spin_fixed_x.value(),
            fixed_y=self.spin_fixed_y.value(),
            randomize_interval=self.chk_rand_interval.isChecked(),
            interval_jitter_ms=self.spin_rand_ms.value(),
            randomize_location=self.chk_rand_loc.isChecked(),
            location_jitter_px=self.spin_rand_px.value(),
        )

    def load_config(self, cfg: AutoClickerConfig) -> None:
        self.spin_hours.setValue(cfg.hours)
        self.spin_mins.setValue(cfg.minutes)
        self.spin_secs.setValue(cfg.seconds)
        self.spin_ms.setValue(cfg.milliseconds)

        b_idx = self.cb_btn.findData(cfg.button)
        if b_idx >= 0:
            self.cb_btn.setCurrentIndex(b_idx)

        c_idx = self.cb_type.findData(cfg.click_type)
        if c_idx >= 0:
            self.cb_type.setCurrentIndex(c_idx)

        if cfg.repeat_type == "infinite":
            self.rb_infinite.setChecked(True)
        else:
            self.rb_count.setChecked(True)
        self.spin_count.setValue(cfg.repeat_count)

        if cfg.location_type == "current":
            self.rb_current_pos.setChecked(True)
        else:
            self.rb_fixed_pos.setChecked(True)
        self.spin_fixed_x.setValue(cfg.fixed_x)
        self.spin_fixed_y.setValue(cfg.fixed_y)

        self.chk_rand_interval.setChecked(cfg.randomize_interval)
        self.spin_rand_ms.setValue(cfg.interval_jitter_ms)
        self.chk_rand_loc.setChecked(cfg.randomize_location)
        self.spin_rand_px.setValue(cfg.location_jitter_px)

    def start_clicking(self) -> None:
        cfg = self.get_current_config()
        self.autoclicker.start(cfg)

    def stop_clicking(self) -> None:
        self.autoclicker.stop()

    def toggle_clicking(self) -> None:
        if self.autoclicker.is_running:
            self.stop_clicking()
        else:
            self.start_clicking()

    def start_picking_coords(self) -> None:
        self._picker_overlay.start_picking()

    def _on_coordinate_picked(self, x: int, y: int) -> None:
        self.spin_fixed_x.setValue(x)
        self.spin_fixed_y.setValue(y)
        self.rb_fixed_pos.setChecked(True)

    def _on_click_update(self, total: int, cps: float, elapsed: float) -> None:
        mins, secs = divmod(elapsed, 60)
        time_str = f"{int(mins):02d}:{secs:04.1f}"
        # Thread-safe Qt signal / timer or direct text update
        self.lbl_cps.setText(f"{cps:.1f}")
        self.lbl_clicks.setText(f"{total:,}")
        self.lbl_time.setText(time_str)

    def _on_status_update(self, is_running: bool) -> None:
        self.btn_start.setEnabled(not is_running)
        self.btn_stop.setEnabled(is_running)
        status_txt = f"AutoClicker Running ({self.lbl_cps.text()})" if is_running else "Ready"
        self.status_changed.emit(is_running, status_txt)

    def _on_test_button_clicked(self) -> None:
        self._test_clicks += 1
        self.btn_test.setText(f"Test Click Counter ({self._test_clicks})")
