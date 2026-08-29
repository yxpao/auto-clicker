"""Settings, Hotkeys, Presets, and Script Export Tab."""

from __future__ import annotations
from typing import Callable, Optional
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QCheckBox,
    QFileDialog,
    QMessageBox,
)

from src.core.storage import StorageManager
from src.core.models import MacroSequence, AutoClickerConfig
from src.ui.macro_studio_tab import MacroStudioTab


class SettingsTab(QWidget):
    """Settings Tab for hotkeys, profile management, and script export."""

    def __init__(self, studio_tab: MacroStudioTab, on_hotkeys_updated: Callable[[dict], None], parent=None):
        super().__init__(parent)
        self.studio_tab = studio_tab
        self.on_hotkeys_updated = on_hotkeys_updated
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(14, 14, 14, 14)

        # 1. Global Hotkeys Configuration
        grp_hotkeys = QGroupBox("GLOBAL HOTKEYS")
        hk_layout = QFormLayout(grp_hotkeys)
        hk_layout.setSpacing(8)

        self.txt_hk_autoclick = QLineEdit("F6")
        self.txt_hk_record = QLineEdit("F7")
        self.txt_hk_pick = QLineEdit("F8")
        self.txt_hk_play = QLineEdit("F9")

        hk_layout.addRow("Auto Clicker (Start / Stop):", self.txt_hk_autoclick)
        hk_layout.addRow("Macro Record (Start / Stop):", self.txt_hk_record)
        hk_layout.addRow("Pick Screen Coordinate:", self.txt_hk_pick)
        hk_layout.addRow("Macro Playback (Play / Stop):", self.txt_hk_play)

        btn_apply_hk = QPushButton("Apply Hotkey Bindings")
        btn_apply_hk.setObjectName("btn_accent")
        btn_apply_hk.clicked.connect(self._apply_hotkeys)
        hk_layout.addRow("", btn_apply_hk)

        layout.addWidget(grp_hotkeys)

        # 2. Preset Library & Import / Export
        grp_presets = QGroupBox("PRESET LIBRARY && STORAGE")
        pre_layout = QVBoxLayout(grp_presets)
        pre_layout.setSpacing(10)

        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("Built-in Presets:"))
        self.cb_presets = QComboBox()
        for name in StorageManager.get_builtin_presets().keys():
            self.cb_presets.addItem(name)
        preset_row.addWidget(self.cb_presets, 1)

        self.btn_load_preset = QPushButton("Load Preset")
        self.btn_load_preset.clicked.connect(self._load_preset)
        preset_row.addWidget(self.btn_load_preset)
        pre_layout.addLayout(preset_row)

        io_row = QHBoxLayout()
        self.btn_save_json = QPushButton("Save Macro (.json)")
        self.btn_save_json.clicked.connect(self._save_macro_json)

        self.btn_load_json = QPushButton("Load Macro (.json)")
        self.btn_load_json.clicked.connect(self._load_macro_json)

        self.btn_export_py = QPushButton("Export Script (.py)")
        self.btn_export_py.setObjectName("btn_start")
        self.btn_export_py.clicked.connect(self._export_python_script)

        io_row.addWidget(self.btn_save_json)
        io_row.addWidget(self.btn_load_json)
        io_row.addWidget(self.btn_export_py)
        pre_layout.addLayout(io_row)

        layout.addWidget(grp_presets)

        # 3. HUD & Behavior Preferences
        grp_hud = QGroupBox("OVERLAY && WINDOW PREFERENCES")
        hud_layout = QVBoxLayout(grp_hud)
        hud_layout.setSpacing(8)

        self.chk_show_hud = QCheckBox("Show Mini Floating HUD during playback / autoclicking")
        self.chk_show_hud.setChecked(True)

        self.chk_minimize_on_start = QCheckBox("Minimize main window when playback starts")
        self.chk_minimize_on_start.setChecked(False)

        hud_layout.addWidget(self.chk_show_hud)
        hud_layout.addWidget(self.chk_minimize_on_start)
        layout.addWidget(grp_hud)

        layout.addStretch()

    def _apply_hotkeys(self) -> None:
        hk_map = {
            "autoclick": self.txt_hk_autoclick.text().strip(),
            "record": self.txt_hk_record.text().strip(),
            "pick": self.txt_hk_pick.text().strip(),
            "play": self.txt_hk_play.text().strip(),
        }
        self.on_hotkeys_updated(hk_map)
        QMessageBox.information(self, "Hotkeys", "Global hotkeys updated successfully!")

    def _load_preset(self) -> None:
        name = self.cb_presets.currentText()
        presets = StorageManager.get_builtin_presets()
        if name in presets:
            preset = presets[name]
            self.studio_tab.macro = preset
            self.studio_tab._refresh_table()
            QMessageBox.information(self, "Preset Loaded", f"Loaded '{name}' into Macro Studio tab!")

    def _save_macro_json(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save Macro", "macro.json", "JSON Files (*.json)")
        if path:
            if StorageManager.save_macro_to_file(self.studio_tab.macro, path):
                QMessageBox.information(self, "Saved", f"Macro successfully saved to:\n{path}")
            else:
                QMessageBox.critical(self, "Error", "Failed to save macro to file.")

    def _load_macro_json(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Load Macro", "", "JSON Files (*.json)")
        if path:
            loaded = StorageManager.load_macro_from_file(path)
            if loaded:
                self.studio_tab.macro = loaded
                self.studio_tab._refresh_table()
                QMessageBox.information(self, "Loaded", f"Loaded macro '{loaded.name}' ({len(loaded.actions)} actions)")
            else:
                QMessageBox.critical(self, "Error", "Failed to load macro from file.")

    def _export_python_script(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Export Standalone Script", "run_macro.py", "Python Files (*.py)")
        if path:
            if StorageManager.export_standalone_python_script(self.studio_tab.macro, path):
                QMessageBox.information(
                    self,
                    "Script Exported",
                    f"Standalone script generated!\nYou can run this script directly with Python without needing this application.",
                )
            else:
                QMessageBox.critical(self, "Error", "Failed to export standalone script.")
