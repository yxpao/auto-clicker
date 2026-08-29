"""Global Event Recorder for Mouse and Keyboard Actions."""

from __future__ import annotations
import time
import math
from typing import Optional, Callable, List
from pynput import mouse, keyboard

from src.core.models import Action, ActionType, MouseButton, ClickType, MacroSequence


class Recorder:
    """Captures global mouse and keyboard events with precision timestamps."""

    def __init__(
        self,
        record_clicks: bool = True,
        record_moves: bool = False,
        record_wheel: bool = True,
        record_keyboard: bool = True,
        min_move_distance: int = 10,
        min_move_interval_ms: float = 30.0,
    ):
        self.record_clicks = record_clicks
        self.record_moves = record_moves
        self.record_wheel = record_wheel
        self.record_keyboard = record_keyboard
        self.min_move_distance = min_move_distance
        self.min_move_interval_ms = min_move_interval_ms

        self._recording = False
        self._actions: List[Action] = []
        self._last_event_time: Optional[float] = None
        self._last_move_pos: Optional[tuple[int, int]] = None
        self._last_move_time: float = 0.0

        self._mouse_listener: Optional[mouse.Listener] = None
        self._keyboard_listener: Optional[keyboard.Listener] = None

        # Callbacks
        self.on_action_recorded: Optional[Callable[[Action, int], None]] = None
        self.on_status_change: Optional[Callable[[bool], None]] = None

    @property
    def is_recording(self) -> bool:
        return self._recording

    @property
    def recorded_actions(self) -> List[Action]:
        return list(self._actions)

    def start(self) -> None:
        if self._recording:
            return

        self._recording = True
        self._actions.clear()
        self._last_event_time = time.perf_counter()
        self._last_move_pos = None
        self._last_move_time = 0.0

        # Start pynput listeners
        self._mouse_listener = mouse.Listener(
            on_click=self._on_mouse_click,
            on_move=self._on_mouse_move,
            on_scroll=self._on_mouse_scroll,
        )
        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
        )

        self._mouse_listener.start()
        self._keyboard_listener.start()

        if self.on_status_change:
            self.on_status_change(True)

    def stop(self) -> MacroSequence:
        if not self._recording:
            return MacroSequence(actions=list(self._actions))

        self._recording = False

        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None
        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None

        if self.on_status_change:
            self.on_status_change(False)

        return MacroSequence(
            name=f"Recorded Macro ({len(self._actions)} steps)",
            actions=list(self._actions),
        )

    def _get_delta_ms(self) -> float:
        now = time.perf_counter()
        if self._last_event_time is None:
            self._last_event_time = now
            return 50.0
        delta = (now - self._last_event_time) * 1000.0
        self._last_event_time = now
        return max(1.0, round(delta, 1))

    def _add_action(self, action: Action) -> None:
        self._actions.append(action)
        if self.on_action_recorded:
            self.on_action_recorded(action, len(self._actions))

    def _on_mouse_click(self, x: int, y: int, button: mouse.Button, pressed: bool) -> None:
        if not self._recording or not self.record_clicks:
            return

        btn_map = {
            mouse.Button.left: MouseButton.LEFT,
            mouse.Button.right: MouseButton.RIGHT,
            mouse.Button.middle: MouseButton.MIDDLE,
            mouse.Button.x1: MouseButton.X1,
            mouse.Button.x2: MouseButton.X2,
        }
        btn = btn_map.get(button, MouseButton.LEFT)
        delay = self._get_delta_ms()

        action_type = ActionType.MOUSE_DOWN if pressed else ActionType.MOUSE_UP
        action = Action(
            action_type=action_type,
            x=int(x),
            y=int(y),
            button=btn,
            delay_ms=delay,
        )
        self._add_action(action)

    def _on_mouse_move(self, x: int, y: int) -> None:
        if not self._recording or not self.record_moves:
            return

        now = time.perf_counter()
        # Rate limit move events
        if (now - self._last_move_time) * 1000.0 < self.min_move_interval_ms:
            return

        if self._last_move_pos:
            dx = x - self._last_move_pos[0]
            dy = y - self._last_move_pos[1]
            dist = math.hypot(dx, dy)
            if dist < self.min_move_distance:
                return

        self._last_move_pos = (int(x), int(y))
        self._last_move_time = now
        delay = self._get_delta_ms()

        action = Action(
            action_type=ActionType.MOVE,
            x=int(x),
            y=int(y),
            delay_ms=delay,
        )
        self._add_action(action)

    def _on_mouse_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        if not self._recording or not self.record_wheel:
            return

        delay = self._get_delta_ms()
        action = Action(
            action_type=ActionType.WHEEL,
            x=int(x),
            y=int(y),
            wheel_dx=int(dx),
            wheel_dy=int(dy),
            delay_ms=delay,
        )
        self._add_action(action)

    def _format_key(self, key: keyboard.Key | keyboard.KeyCode) -> str:
        if isinstance(key, keyboard.Key):
            return key.name
        elif hasattr(key, "char") and key.char:
            return key.char
        elif hasattr(key, "vk") and key.vk:
            return f"vk_{key.vk}"
        return str(key)

    def _on_key_press(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        if not self._recording or not self.record_keyboard:
            return

        key_str = self._format_key(key)
        delay = self._get_delta_ms()
        action = Action(
            action_type=ActionType.KEY_DOWN,
            key=key_str,
            delay_ms=delay,
        )
        self._add_action(action)

    def _on_key_release(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        if not self._recording or not self.record_keyboard:
            return

        key_str = self._format_key(key)
        delay = self._get_delta_ms()
        action = Action(
            action_type=ActionType.KEY_UP,
            key=key_str,
            delay_ms=delay,
        )
        self._add_action(action)
