"""Smoke test for UI components and MainWindow initialization."""

import os
import sys
import pytest
from PyQt6.QtWidgets import QApplication

# Run Qt offscreen in headless test environment if needed
os.environ["QT_QPA_PLATFORM"] = "offscreen"


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_ui_components(qapp):
    from src.ui.main_window import MainWindow
    from src.ui.action_dialog import ActionDialog
    from src.ui.batch_edit_dialog import BatchEditDialog
    from src.core.models import Action, MacroSequence

    window = MainWindow()
    assert window.windowTitle() == "AutoClicker & Macro Studio Pro"
    assert window.tabs.count() == 3

    # Test Action Dialog
    action = Action(x=100, y=200, delay_ms=50.0)
    dlg = ActionDialog(window, action=action)
    assert dlg.spin_x.value() == 100
    assert dlg.spin_y.value() == 200

    # Test Batch Edit Dialog
    macro = MacroSequence(actions=[action])
    batch_dlg = BatchEditDialog(macro, parent=window)
    assert batch_dlg.macro == macro

    window.close()
