"""Automated Unit Tests for Core Engine and Data Models."""

import os
import pytest
from src.core.models import (
    Action,
    ActionType,
    MouseButton,
    ClickType,
    MacroSequence,
    AutoClickerConfig,
)
from src.core.storage import StorageManager


class TestDataModels:
    def test_action_serialization(self):
        action = Action(
            action_type=ActionType.CLICK,
            x=100,
            y=200,
            button=MouseButton.RIGHT,
            click_type=ClickType.DOUBLE,
            delay_ms=120.5,
            duration_ms=10.0,
            comment="Test click",
        )
        d = action.to_dict()
        restored = Action.from_dict(d)

        assert restored.action_type == ActionType.CLICK
        assert restored.x == 100
        assert restored.y == 200
        assert restored.button == MouseButton.RIGHT
        assert restored.click_type == ClickType.DOUBLE
        assert restored.delay_ms == 120.5
        assert restored.duration_ms == 10.0
        assert restored.comment == "Test click"
        assert "Right Click (Double) @ (100, 200)" in restored.summary()

    def test_macro_sequence_serialization(self):
        macro = MacroSequence(
            name="Test Sequence",
            actions=[
                Action(action_type=ActionType.CLICK, x=50, y=50),
                Action(action_type=ActionType.KEY_PRESS, key="enter", delay_ms=100.0),
                Action(action_type=ActionType.TEXT, text="hello world", delay_ms=200.0),
            ],
            repeat_count=3,
            speed_multiplier=1.5,
            delay_between_loops_ms=500.0,
        )

        d = macro.to_dict()
        restored = MacroSequence.from_dict(d)

        assert restored.name == "Test Sequence"
        assert len(restored.actions) == 3
        assert restored.repeat_count == 3
        assert restored.speed_multiplier == 1.5
        assert restored.delay_between_loops_ms == 500.0
        assert restored.actions[1].key == "enter"
        assert restored.actions[2].text == "hello world"

    def test_autoclicker_config(self):
        config = AutoClickerConfig(
            hours=1,
            minutes=2,
            seconds=3,
            milliseconds=450,
            button=MouseButton.MIDDLE,
            click_type=ClickType.SINGLE,
            repeat_type="count",
            repeat_count=50,
        )
        expected_ms = (1 * 3600 + 2 * 60 + 3) * 1000 + 450
        assert config.total_interval_ms == expected_ms

        d = config.to_dict()
        restored = AutoClickerConfig.from_dict(d)
        assert restored.button == MouseButton.MIDDLE
        assert restored.repeat_count == 50
        assert restored.total_interval_ms == expected_ms


class TestMacroTransformations:
    def test_speed_scaling(self):
        macro = MacroSequence(
            actions=[
                Action(action_type=ActionType.CLICK, delay_ms=100.0),
                Action(action_type=ActionType.KEY_PRESS, delay_ms=200.0),
            ]
        )
        # 2x speed -> delays should be halved
        macro.scale_speed(2.0)
        assert macro.actions[0].delay_ms == 50.0
        assert macro.actions[1].delay_ms == 100.0

    def test_shift_coordinates(self):
        macro = MacroSequence(
            actions=[
                Action(action_type=ActionType.CLICK, x=100, y=200),
                Action(action_type=ActionType.MOVE, x=300, y=400),
                Action(action_type=ActionType.KEY_PRESS, key="a"),  # No coords
            ]
        )
        macro.shift_coordinates(dx=50, dy=-30)
        assert macro.actions[0].x == 150
        assert macro.actions[0].y == 170
        assert macro.actions[1].x == 350
        assert macro.actions[1].y == 370
        assert macro.actions[2].x is None

    def test_normalize_delays(self):
        macro = MacroSequence(
            actions=[
                Action(delay_ms=10.0),
                Action(delay_ms=500.0),
                Action(delay_ms=200.0),
            ]
        )
        macro.normalize_delays(75.0)
        assert all(a.delay_ms == 75.0 for a in macro.actions)

    def test_trim_pauses(self):
        macro = MacroSequence(
            actions=[
                Action(delay_ms=50.0),
                Action(delay_ms=3500.0),
                Action(delay_ms=1200.0),
            ]
        )
        macro.trim_pauses(1000.0)
        assert macro.actions[0].delay_ms == 50.0
        assert macro.actions[1].delay_ms == 1000.0
        assert macro.actions[2].delay_ms == 1000.0


class TestStorageAndPresets:
    def test_presets(self):
        presets = StorageManager.get_builtin_presets()
        assert "Anti-AFK Jiggler" in presets
        assert "Triple Click Burst" in presets
        assert len(presets["Triple Click Burst"].actions) == 3

    def test_standalone_export(self, tmp_path):
        macro = MacroSequence(
            name="Export Test",
            actions=[
                Action(action_type=ActionType.CLICK, x=100, y=100, delay_ms=50.0),
            ],
            repeat_count=2,
        )
        out_file = str(tmp_path / "test_export.py")
        success = StorageManager.export_standalone_python_script(macro, out_file)
        assert success
        assert os.path.exists(out_file)
        with open(out_file, "r", encoding="utf-8") as f:
            content = f.read()
        assert "run_macro" in content
        assert "SendInput" in content
