"""Serialization, Presets, and Script Export for Macros and Autoclicker."""

from __future__ import annotations
import json
import os
from typing import Dict, Any, List, Optional
from src.core.models import MacroSequence, Action, ActionType, MouseButton, ClickType, AutoClickerConfig


class StorageManager:
    """Manages saving, loading, presets, and standalone script exporting."""

    @staticmethod
    def save_macro_to_file(macro: MacroSequence, filepath: str) -> bool:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(macro.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"[StorageManager] Error saving macro: {e}")
            return False

    @staticmethod
    def load_macro_from_file(filepath: str) -> Optional[MacroSequence]:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return MacroSequence.from_dict(data)
        except Exception as e:
            print(f"[StorageManager] Error loading macro: {e}")
            return None

    @staticmethod
    def save_config_to_file(config: AutoClickerConfig, filepath: str) -> bool:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(config.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"[StorageManager] Error saving config: {e}")
            return False

    @staticmethod
    def load_config_from_file(filepath: str) -> Optional[AutoClickerConfig]:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return AutoClickerConfig.from_dict(data)
        except Exception as e:
            print(f"[StorageManager] Error loading config: {e}")
            return None

    @staticmethod
    def get_builtin_presets() -> Dict[str, MacroSequence]:
        """Provides useful ready-to-use macro presets."""
        presets = {}

        # 1. Anti-AFK Mouse Jiggler
        presets["Anti-AFK Jiggler"] = MacroSequence(
            name="Anti-AFK Jiggler",
            actions=[
                Action(action_type=ActionType.MOVE, x=500, y=500, delay_ms=1000.0),
                Action(action_type=ActionType.MOVE, x=550, y=520, delay_ms=2000.0),
                Action(action_type=ActionType.CLICK, button=MouseButton.RIGHT, click_type=ClickType.SINGLE, delay_ms=500.0),
                Action(action_type=ActionType.MOVE, x=500, y=500, delay_ms=2000.0),
            ],
            repeat_count=0,  # Infinite
            delay_between_loops_ms=3000.0,
        )

        # 2. Triple Left Click Burst
        presets["Triple Click Burst"] = MacroSequence(
            name="Triple Click Burst",
            actions=[
                Action(action_type=ActionType.CLICK, button=MouseButton.LEFT, click_type=ClickType.SINGLE, delay_ms=20.0),
                Action(action_type=ActionType.CLICK, button=MouseButton.LEFT, click_type=ClickType.SINGLE, delay_ms=20.0),
                Action(action_type=ActionType.CLICK, button=MouseButton.LEFT, click_type=ClickType.SINGLE, delay_ms=20.0),
            ],
            repeat_count=1,
            delay_between_loops_ms=100.0,
        )

        # 3. Copy & Paste Hotkey Chain
        presets["Copy & Paste Combo"] = MacroSequence(
            name="Copy & Paste Combo",
            actions=[
                Action(action_type=ActionType.KEY_DOWN, key="ctrl", delay_ms=50.0),
                Action(action_type=ActionType.KEY_PRESS, key="c", delay_ms=30.0),
                Action(action_type=ActionType.KEY_UP, key="ctrl", delay_ms=30.0),
                Action(action_type=ActionType.DELAY, delay_ms=300.0),
                Action(action_type=ActionType.KEY_DOWN, key="ctrl", delay_ms=50.0),
                Action(action_type=ActionType.KEY_PRESS, key="v", delay_ms=30.0),
                Action(action_type=ActionType.KEY_UP, key="ctrl", delay_ms=30.0),
            ],
            repeat_count=1,
            delay_between_loops_ms=100.0,
        )

        # 4. Text Typer Demo
        presets["Quick Text Typer"] = MacroSequence(
            name="Quick Text Typer",
            actions=[
                Action(action_type=ActionType.TEXT, text="Hello from AutoClicker & Macro Studio!", delay_ms=200.0),
                Action(action_type=ActionType.KEY_PRESS, key="enter", delay_ms=100.0),
            ],
            repeat_count=1,
            delay_between_loops_ms=100.0,
        )

        return presets

    @staticmethod
    def export_standalone_python_script(macro: MacroSequence, output_path: str) -> bool:
        """Exports the macro as a standalone runnable Python script using ctypes."""
        try:
            lines = [
                '"""Standalone Generated Macro Script."""',
                "import ctypes",
                "import time",
                "from ctypes import wintypes",
                "",
                "# Win32 Constants",
                "INPUT_MOUSE = 0",
                "INPUT_KEYBOARD = 1",
                "KEYEVENTF_KEYUP = 0x0002",
                "KEYEVENTF_UNICODE = 0x0004",
                "MOUSEEVENTF_LEFTDOWN = 0x0002",
                "MOUSEEVENTF_LEFTUP = 0x0004",
                "MOUSEEVENTF_RIGHTDOWN = 0x0008",
                "MOUSEEVENTF_RIGHTUP = 0x0010",
                "MOUSEEVENTF_MIDDLEDOWN = 0x0020",
                "MOUSEEVENTF_MIDDLEUP = 0x0040",
                "",
                "SendInput = ctypes.windll.user32.SendInput",
                "SetCursorPos = ctypes.windll.user32.SetCursorPos",
                "",
                "print('Macro starting in 3 seconds... Switch to target window!')",
                "time.sleep(3)",
                f"# Playing macro: {macro.name}",
                f"# Repeat Count: {macro.repeat_count}",
                "",
                "def run_macro():",
            ]

            indent = "    "
            loop_header = (
                f"{indent}for loop in range({macro.repeat_count}):"
                if macro.repeat_count > 0
                else f"{indent}while True:"
            )
            lines.append(loop_header)
            inner = indent + "    "

            for action in macro.actions:
                if not action.enabled:
                    continue
                scaled_delay = max(0.001, (action.delay_ms / macro.speed_multiplier) / 1000.0)
                lines.append(f"{inner}time.sleep({scaled_delay:.4f})")

                if action.action_type == ActionType.CLICK:
                    if action.x is not None and action.y is not None:
                        lines.append(f"{inner}SetCursorPos({action.x}, {action.y})")
                    btn_down = "MOUSEEVENTF_LEFTDOWN"
                    btn_up = "MOUSEEVENTF_LEFTUP"
                    if action.button == MouseButton.RIGHT:
                        btn_down = "MOUSEEVENTF_RIGHTDOWN"
                        btn_up = "MOUSEEVENTF_RIGHTUP"
                    elif action.button == MouseButton.MIDDLE:
                        btn_down = "MOUSEEVENTF_MIDDLEDOWN"
                        btn_up = "MOUSEEVENTF_MIDDLEUP"

                    lines.append(f"{inner}ctypes.windll.user32.mouse_event({btn_down}, 0, 0, 0, 0)")
                    lines.append(f"{inner}ctypes.windll.user32.mouse_event({btn_up}, 0, 0, 0, 0)")
                    if action.click_type == ClickType.DOUBLE:
                        lines.append(f"{inner}time.sleep(0.05)")
                        lines.append(f"{inner}ctypes.windll.user32.mouse_event({btn_down}, 0, 0, 0, 0)")
                        lines.append(f"{inner}ctypes.windll.user32.mouse_event({btn_up}, 0, 0, 0, 0)")

                elif action.action_type == ActionType.MOVE:
                    if action.x is not None and action.y is not None:
                        lines.append(f"{inner}SetCursorPos({action.x}, {action.y})")

                elif action.action_type == ActionType.TEXT:
                    lines.append(f"{inner}# Type: {action.text}")
                    # Basic print statement or SendKeys
                    for char in (action.text or ""):
                        lines.append(f"{inner}# char: {char}")

            if macro.delay_between_loops_ms > 0:
                lines.append(f"{inner}time.sleep({macro.delay_between_loops_ms / 1000.0:.3f})")

            lines.append("")
            lines.append("if __name__ == '__main__':")
            lines.append("    try:")
            lines.append("        run_macro()")
            lines.append("        print('Macro finished successfully!')")
            lines.append("    except KeyboardInterrupt:")
            lines.append("        print('Macro stopped by user.')")

            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            return True
        except Exception as e:
            print(f"[StorageManager] Error exporting script: {e}")
            return False
