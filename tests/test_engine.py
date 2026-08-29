"""Tests for AutoClicker, Player, Recorder, and HotkeyManager."""

import time
from unittest.mock import patch
from src.core.models import (
    Action,
    ActionType,
    MouseButton,
    ClickType,
    MacroSequence,
    AutoClickerConfig,
)
from src.core.autoclicker import AutoClicker
from src.core.player import Player
from src.core.recorder import Recorder
from src.core.hotkey_manager import HotkeyManager


class TestAutoClicker:
    @patch("src.core.input_sender.InputSender.click")
    def test_autoclicker_count(self, mock_click):
        cfg = AutoClickerConfig(
            milliseconds=10,
            repeat_type="count",
            repeat_count=5,
        )
        clicker = AutoClicker(cfg)

        clicks_recorded = []
        clicker.on_click_callback = lambda count, cps, elapsed: clicks_recorded.append(count)

        clicker.start(cfg)
        # Wait for thread to finish 5 clicks
        time.sleep(0.2)
        clicker.stop()

        assert mock_click.call_count >= 5
        assert len(clicks_recorded) >= 5


class TestMacroPlayer:
    @patch("src.core.input_sender.InputSender.click")
    @patch("src.core.input_sender.InputSender.key_tap")
    def test_player_execution(self, mock_key, mock_click):
        macro = MacroSequence(
            name="Test Play",
            actions=[
                Action(action_type=ActionType.CLICK, delay_ms=1.0),
                Action(action_type=ActionType.KEY_PRESS, key="a", delay_ms=1.0),
            ],
            repeat_count=2,
            delay_between_loops_ms=1.0,
        )

        player = Player()
        steps_executed = []
        player.on_step_start = lambda idx, act, loop, total: steps_executed.append((idx, act.action_type, loop))

        player.play(macro)
        time.sleep(0.2)
        player.stop()

        assert mock_click.call_count >= 2
        assert mock_key.call_count >= 2
        assert len(steps_executed) >= 4  # 2 actions * 2 loops = 4 steps

    @patch("src.core.input_sender.InputSender.click")
    def test_player_selected_indices(self, mock_click):
        macro = MacroSequence(
            name="Test Selective",
            actions=[
                Action(action_type=ActionType.CLICK, button=MouseButton.LEFT, delay_ms=1.0),
                Action(action_type=ActionType.CLICK, button=MouseButton.RIGHT, delay_ms=1.0),
                Action(action_type=ActionType.CLICK, button=MouseButton.MIDDLE, delay_ms=1.0),
            ],
            repeat_count=1,
        )

        player = Player()
        steps_executed = []
        player.on_step_start = lambda idx, act, loop, total: steps_executed.append(idx)

        # Only play action at index 1 (Right click)
        player.play(macro, selected_indices=[1])
        time.sleep(0.1)
        player.stop()

        assert steps_executed == [1]


class TestHotkeyFormatting:
    def test_format_keys(self):
        hm = HotkeyManager()
        assert hm.format_key_for_pynput("F6") == "<f6>"
        assert hm.format_key_for_pynput("Ctrl+Shift+R") == "<ctrl>+<shift>+r"
        assert hm.format_key_for_pynput("Alt+F4") == "<alt>+<f4>"
