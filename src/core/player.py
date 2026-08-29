"""High-precision Macro Playback Engine."""

from __future__ import annotations
import threading
import time
from typing import Optional, Callable, List

from src.core.models import Action, ActionType, MacroSequence, ClickType
from src.core.input_sender import InputSender


class Player:
    """Threaded macro playback engine with precision timing, speed scaling, and loop management."""

    def __init__(self):
        self._playing = False
        self._paused = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()  # Not paused by default

        self.current_macro: Optional[MacroSequence] = None
        self.selected_indices: Optional[List[int]] = None
        self.speed_multiplier: float = 1.0
        self.repeat_count: int = 1  # 0 = infinite
        self.delay_between_loops_ms: float = 100.0

        # Callbacks
        self.on_step_start: Optional[Callable[[int, Action, int, int], None]] = None  # (index, action, loop, total_loops)
        self.on_step_finished: Optional[Callable[[int, Action], None]] = None
        self.on_loop_finished: Optional[Callable[[int, int], None]] = None
        self.on_playback_finished: Optional[Callable[[], None]] = None
        self.on_status_change: Optional[Callable[[bool], None]] = None

    @property
    def is_playing(self) -> bool:
        return self._playing

    @property
    def is_paused(self) -> bool:
        return self._paused

    def play(
        self,
        macro: MacroSequence,
        selected_indices: Optional[List[int]] = None,
        speed_multiplier: Optional[float] = None,
        repeat_count: Optional[int] = None,
        delay_between_loops_ms: Optional[float] = None,
    ) -> bool:
        if self._playing:
            return False

        if not macro.actions:
            return False

        self.current_macro = macro
        self.selected_indices = selected_indices
        self.speed_multiplier = max(0.01, speed_multiplier if speed_multiplier is not None else macro.speed_multiplier)
        self.repeat_count = repeat_count if repeat_count is not None else macro.repeat_count
        self.delay_between_loops_ms = (
            delay_between_loops_ms if delay_between_loops_ms is not None else macro.delay_between_loops_ms
        )

        self._playing = True
        self._paused = False
        self._stop_event.clear()
        self._pause_event.set()

        self._thread = threading.Thread(target=self._run_playback, daemon=True, name="MacroPlayerThread")
        self._thread.start()

        if self.on_status_change:
            self.on_status_change(True)
        return True

    def stop(self) -> None:
        if not self._playing:
            return

        self._playing = False
        self._stop_event.set()
        self._pause_event.set()  # Unblock if paused so thread can exit

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.5)

        if self.on_status_change:
            self.on_status_change(False)
        if self.on_playback_finished:
            self.on_playback_finished()

    def pause(self) -> None:
        if not self._playing or self._paused:
            return
        self._paused = True
        self._pause_event.clear()

    def resume(self) -> None:
        if not self._playing or not self._paused:
            return
        self._paused = False
        self._pause_event.set()

    def _sleep_interruptible(self, duration_ms: float) -> bool:
        """Sleep with speed scaling, break immediately if stop requested."""
        scaled_ms = max(0.0, duration_ms / self.speed_multiplier)
        duration_sec = scaled_ms / 1000.0
        if duration_sec <= 0:
            return True

        target = time.perf_counter() + duration_sec
        # Sleep in small chunks to remain responsive to stop/pause
        while time.perf_counter() < target:
            if self._stop_event.is_set():
                return False
            self._pause_event.wait()

            remaining = target - time.perf_counter()
            if remaining <= 0:
                break
            # Use small step sleeps for sub-10ms responsiveness
            time.sleep(min(0.01, remaining))

        return not self._stop_event.is_set()

    def _execute_action(self, action: Action) -> None:
        if not action.enabled:
            return

        atype = action.action_type
        if atype == ActionType.CLICK:
            InputSender.click(
                button=action.button or MouseButton.LEFT,
                click_type=action.click_type,
                x=action.x,
                y=action.y,
            )
        elif atype == ActionType.MOUSE_DOWN:
            InputSender.mouse_down(
                button=action.button or MouseButton.LEFT,
                x=action.x,
                y=action.y,
            )
        elif atype == ActionType.MOUSE_UP:
            InputSender.mouse_up(
                button=action.button or MouseButton.LEFT,
                x=action.x,
                y=action.y,
            )
        elif atype == ActionType.MOVE:
            if action.x is not None and action.y is not None:
                InputSender.move_cursor(action.x, action.y)
        elif atype == ActionType.WHEEL:
            InputSender.mouse_wheel(dy=action.wheel_dy, dx=action.wheel_dx)
        elif atype == ActionType.KEY_PRESS:
            if action.key:
                InputSender.key_tap(action.key)
        elif atype == ActionType.KEY_DOWN:
            if action.key:
                InputSender.key_down(action.key)
        elif atype == ActionType.KEY_UP:
            if action.key:
                InputSender.key_up(action.key)
        elif atype == ActionType.TEXT:
            if action.text:
                InputSender.type_text(action.text)
        elif atype == ActionType.DELAY:
            # Explicit delay action
            pass

        # If action has a hold duration, sleep then release if needed
        if action.duration_ms > 0:
            self._sleep_interruptible(action.duration_ms)

    def _run_playback(self) -> None:
        macro = self.current_macro
        if not macro:
            return

        all_actions = macro.actions
        if self.selected_indices is not None and len(self.selected_indices) > 0:
            active_items = [(idx, all_actions[idx]) for idx in self.selected_indices if 0 <= idx < len(all_actions)]
        else:
            active_items = list(enumerate(all_actions))

        current_loop = 0
        total_loops = self.repeat_count  # 0 means infinite

        while not self._stop_event.is_set():
            current_loop += 1

            for orig_idx, action in active_items:
                if self._stop_event.is_set():
                    break
                self._pause_event.wait()

                # Pre-action delay
                if action.delay_ms > 0:
                    if not self._sleep_interruptible(action.delay_ms):
                        break

                if self._stop_event.is_set():
                    break

                if self.on_step_start:
                    self.on_step_start(orig_idx, action, current_loop, total_loops)

                self._execute_action(action)

                if self.on_step_finished:
                    self.on_step_finished(orig_idx, action)

            if self.on_loop_finished:
                self.on_loop_finished(current_loop, total_loops)

            # Check if total loops reached
            if total_loops > 0 and current_loop >= total_loops:
                break

            # Delay between loops
            if not self._stop_event.is_set() and self.delay_between_loops_ms > 0:
                if not self._sleep_interruptible(self.delay_between_loops_ms):
                    break

        self._playing = False
        if self.on_status_change:
            self.on_status_change(False)
        if self.on_playback_finished:
            self.on_playback_finished()
