"""Main Application Window for Auto Clicker & Macro Studio Pro."""

from __future__ import annotations
from typing import Dict
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QLabel,
    QStatusBar,
    QApplication,
)

from src.core.autoclicker import AutoClicker
from src.core.recorder import Recorder
from src.core.player import Player
from src.core.hotkey_manager import HotkeyManager
from src.ui.autoclicker_tab import AutoClickerTab
from src.ui.macro_studio_tab import MacroStudioTab
from src.ui.settings_tab import SettingsTab
from src.ui.floating_hud import FloatingHUD
from src.ui.styles import MAIN_STYLE


class MainWindow(QMainWindow):
    """Primary application window hosting tabs, global state, and hotkeys."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoClicker & Macro Studio Pro")
        self.resize(820, 720)
        self.setMinimumSize(720, 600)
        self.setStyleSheet(MAIN_STYLE)

        # Core Engines
        self.autoclicker = AutoClicker()
        self.recorder = Recorder()
        self.player = Player()
        self.hotkey_manager = HotkeyManager()

        # Floating HUD
        self.floating_hud = FloatingHUD()
        self.floating_hud.stop_requested.connect(self._stop_all_active)

        self._init_ui()
        self._setup_hotkeys({
            "autoclick": "F6",
            "record": "F7",
            "pick": "F8",
            "play": "F9",
        })

    def _init_ui(self) -> None:
        central = QWidget(self)
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 16, 20, 12)
        layout.setSpacing(14)

        # Header Title Banner
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 4)
        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(2)
        lbl_title = QLabel("AutoClicker & Macro Studio")
        lbl_title.setObjectName("lbl_heading")
        lbl_sub = QLabel("Precision clicks  ·  Macro recording  ·  Batch editing")
        lbl_sub.setObjectName("lbl_subheading")
        title_vbox.addWidget(lbl_title)
        title_vbox.addWidget(lbl_sub)
        header.addLayout(title_vbox)
        header.addStretch()

        lbl_version = QLabel("v1.0")
        lbl_version.setObjectName("lbl_subheading")
        header.addWidget(lbl_version)
        layout.addLayout(header)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tab_autoclicker = AutoClickerTab(self.autoclicker, self)
        self.tab_studio = MacroStudioTab(self.recorder, self.player, self)
        self.tab_settings = SettingsTab(self.tab_studio, self._setup_hotkeys, self)

        self.tab_autoclicker.status_changed.connect(self._on_autoclicker_status)
        self.tab_studio.status_changed.connect(self._on_studio_status)

        self.tabs.addTab(self.tab_autoclicker, "Auto Clicker")
        self.tabs.addTab(self.tab_studio, "Macro Studio")
        self.tabs.addTab(self.tab_settings, "Settings && Presets")
        layout.addWidget(self.tabs, 1)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready  —  F6 Click  ·  F7 Record  ·  F8 Pick  ·  F9 Play")

    def _setup_hotkeys(self, hk_map: Dict[str, str]) -> None:
        self.hotkey_manager.clear()

        # F6: Toggle AutoClicker
        if hk_map.get("autoclick"):
            self.hotkey_manager.register("autoclick", hk_map["autoclick"], self._on_hotkey_autoclick)

        # F7: Toggle Record
        if hk_map.get("record"):
            self.hotkey_manager.register("record", hk_map["record"], self._on_hotkey_record)

        # F8: Pick Coordinate
        if hk_map.get("pick"):
            self.hotkey_manager.register("pick", hk_map["pick"], self._on_hotkey_pick)

        # F9: Toggle Play
        if hk_map.get("play"):
            self.hotkey_manager.register("play", hk_map["play"], self._on_hotkey_play)

        self.hotkey_manager.start()

    def _on_hotkey_autoclick(self) -> None:
        self.tab_autoclicker.toggle_clicking()

    def _on_hotkey_record(self) -> None:
        self.tab_studio.toggle_recording()

    def _on_hotkey_pick(self) -> None:
        self.tab_autoclicker.start_picking_coords()

    def _on_hotkey_play(self) -> None:
        self.tab_studio.toggle_playback()

    def _on_autoclicker_status(self, is_running: bool, text: str) -> None:
        self.status_bar.showMessage(f"AutoClicker: {text}")
        if is_running:
            if self.tab_settings.chk_show_hud.isChecked():
                self._show_hud(text, is_active=True)
            if self.tab_settings.chk_minimize_on_start.isChecked():
                self.showMinimized()
        else:
            self._hide_hud_if_idle()

    def _on_studio_status(self, is_active: bool, text: str) -> None:
        self.status_bar.showMessage(f"Macro Studio: {text}")
        if is_active:
            if self.tab_settings.chk_show_hud.isChecked():
                self._show_hud(text, is_active=True)
            if self.tab_settings.chk_minimize_on_start.isChecked() and self.player.is_playing:
                self.showMinimized()
        else:
            self._hide_hud_if_idle()

    def _show_hud(self, text: str, is_active: bool) -> None:
        self.floating_hud.set_status(text, is_active=is_active)
        if not self.floating_hud.isVisible():
            # Position at top right of primary screen
            screen_geo = QApplication.primaryScreen().geometry()
            self.floating_hud.move(screen_geo.width() - 320, 40)
            self.floating_hud.show()

    def _hide_hud_if_idle(self) -> None:
        if not self.autoclicker.is_running and not self.recorder.is_recording and not self.player.is_playing:
            self.floating_hud.hide()

    def _stop_all_active(self) -> None:
        self.autoclicker.stop()
        self.tab_studio.stop_all()

    def closeEvent(self, event):
        self.hotkey_manager.stop()
        self.autoclicker.stop()
        self.recorder.stop()
        self.player.stop()
        self.floating_hud.close()
        event.accept()
