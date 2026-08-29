"""Dialog for batch transformations and bulk timing adjustments."""

from __future__ import annotations
from typing import List, Optional
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QGroupBox,
    QRadioButton,
    QButtonGroup,
)

from src.core.models import MacroSequence


class BatchEditDialog(QDialog):
    """Dialog for performing batch edits across multiple or all macro actions."""

    def __init__(self, macro: MacroSequence, selected_indices: Optional[List[int]] = None, parent=None):
        super().__init__(parent)
        self.macro = macro
        self.selected_indices = selected_indices
        self.setWindowTitle("Batch Edit / Playback Transformation")
        self.setMinimumWidth(420)
        self.setModal(True)

        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Target Scope Info
        scope_count = len(self.selected_indices) if self.selected_indices else len(self.macro.actions)
        scope_desc = f"Applying to: <b>{scope_count} actions</b> ({'Selected rows only' if self.selected_indices else 'All rows'})"
        lbl_scope = QLabel(scope_desc)
        lbl_scope.setStyleSheet("color: #38bdf8; font-size: 13px;")
        layout.addWidget(lbl_scope)

        # Transformation Options Group
        group = QGroupBox("Select Transformation")
        grp_layout = QVBoxLayout(group)
        self.btn_grp = QButtonGroup(self)

        # Option 1: Scale Speed
        self.rb_speed = QRadioButton("Scale Speed (Multiply Delays)")
        self.rb_speed.setChecked(True)
        self.btn_grp.addButton(self.rb_speed, 1)
        grp_layout.addWidget(self.rb_speed)

        speed_row = QHBoxLayout()
        speed_row.addSpacing(24)
        speed_row.addWidget(QLabel("Multiplier:"))
        self.spin_multiplier = QDoubleSpinBox()
        self.spin_multiplier.setRange(0.1, 100.0)
        self.spin_multiplier.setValue(2.0)
        self.spin_multiplier.setSingleStep(0.5)
        self.spin_multiplier.setSuffix(" x")
        speed_row.addWidget(self.spin_multiplier)
        grp_layout.addLayout(speed_row)

        # Option 2: Shift Coordinates
        self.rb_shift = QRadioButton("Shift Coordinates (Offset X, Y)")
        self.btn_grp.addButton(self.rb_shift, 2)
        grp_layout.addWidget(self.rb_shift)

        shift_row = QHBoxLayout()
        shift_row.addSpacing(24)
        shift_row.addWidget(QLabel("ΔX:"))
        self.spin_dx = QSpinBox()
        self.spin_dx.setRange(-9999, 9999)
        self.spin_dx.setValue(0)
        shift_row.addWidget(self.spin_dx)
        shift_row.addWidget(QLabel("ΔY:"))
        self.spin_dy = QSpinBox()
        self.spin_dy.setRange(-9999, 9999)
        self.spin_dy.setValue(0)
        shift_row.addWidget(self.spin_dy)
        grp_layout.addLayout(shift_row)

        # Option 3: Normalize Delays
        self.rb_norm = QRadioButton("Set Uniform Delay (All steps)")
        self.btn_grp.addButton(self.rb_norm, 3)
        grp_layout.addWidget(self.rb_norm)

        norm_row = QHBoxLayout()
        norm_row.addSpacing(24)
        norm_row.addWidget(QLabel("Delay (ms):"))
        self.spin_norm = QDoubleSpinBox()
        self.spin_norm.setRange(0.0, 999999.0)
        self.spin_norm.setValue(50.0)
        self.spin_norm.setSuffix(" ms")
        norm_row.addWidget(self.spin_norm)
        grp_layout.addLayout(norm_row)

        # Option 4: Randomize / Humanize Delays
        self.rb_rand = QRadioButton("Humanize Delays (Random Jitter %)")
        self.btn_grp.addButton(self.rb_rand, 4)
        grp_layout.addWidget(self.rb_rand)

        rand_row = QHBoxLayout()
        rand_row.addSpacing(24)
        rand_row.addWidget(QLabel("Jitter Variance:"))
        self.spin_rand = QDoubleSpinBox()
        self.spin_rand.setRange(1.0, 100.0)
        self.spin_rand.setValue(20.0)
        self.spin_rand.setSuffix(" %")
        rand_row.addWidget(self.spin_rand)
        grp_layout.addLayout(rand_row)

        # Option 5: Trim Long Pauses
        self.rb_trim = QRadioButton("Trim / Cap Idle Pauses")
        self.btn_grp.addButton(self.rb_trim, 5)
        grp_layout.addWidget(self.rb_trim)

        trim_row = QHBoxLayout()
        trim_row.addSpacing(24)
        trim_row.addWidget(QLabel("Max Allowed Delay:"))
        self.spin_trim = QDoubleSpinBox()
        self.spin_trim.setRange(10.0, 999999.0)
        self.spin_trim.setValue(500.0)
        self.spin_trim.setSuffix(" ms")
        trim_row.addWidget(self.spin_trim)
        grp_layout.addLayout(trim_row)

        layout.addWidget(group)

        # Buttons
        btn_box = QHBoxLayout()
        self.btn_apply = QPushButton("Apply Changes")
        self.btn_apply.setObjectName("btn_start")
        self.btn_apply.clicked.connect(self._apply_transform)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)

        btn_box.addStretch()
        btn_box.addWidget(self.btn_cancel)
        btn_box.addWidget(self.btn_apply)
        layout.addLayout(btn_box)

    def _apply_transform(self) -> None:
        selected_id = self.btn_grp.checkedId()
        indices = self.selected_indices

        if selected_id == 1:
            self.macro.scale_speed(self.spin_multiplier.value(), selected_indices=indices)
        elif selected_id == 2:
            self.macro.shift_coordinates(self.spin_dx.value(), self.spin_dy.value(), selected_indices=indices)
        elif selected_id == 3:
            self.macro.normalize_delays(self.spin_norm.value(), selected_indices=indices)
        elif selected_id == 4:
            self.macro.randomize_delays(self.spin_rand.value(), selected_indices=indices)
        elif selected_id == 5:
            self.macro.trim_pauses(self.spin_trim.value(), selected_indices=indices)

        self.accept()
