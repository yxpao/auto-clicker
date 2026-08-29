"""High-precision Auto Clicker Engine."""

from __future__ import annotations
import threading
import time
import random
from typing import Callable, Optional
from collections import deque

from src.core.models import AutoClickerConfig, MouseButton, ClickType
from src.core.input_sender import InputSender


class AutoClicker:
    """Threaded high-speed auto clicker with precision timing and CPS metering."""

    def __init__(self, config: Optional[AutoClickerConfig] = None):
        self.config = config or AutoClickerConfig()
        self._running = False
        self._paused = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._click_timestamps = deque()  # Rolling window for CPS calculation
        self._total_clicks = 0
        self._start_time = 0.0

        # Callbacks
        self.on_click_callback: Optional[Callable[[int, float, float], None]] = None  # (clicks, cps, elapsed)
        self.on_status_callback: Optional[Callable[[bool], None]] = None  # is_running
        self.on_finish_callback: Optional[Callable[[], None]] = None

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def total_clicks(self) -> int:
        return self._total_clicks

    def start(self, config: Optional[AutoClickerConfig] = None) -> bool:
        if self._running:
            return False

        if config:
            self.config = config

        self._running = True
        self._paused = False
        self._stop_event.clear()
        self._total_clicks = 0
        self._click_timestamps.clear()
        self._start_time = time.perf_counter()

        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="AutoClickerThread")
        self._thread.start()

        if self.on_status_callback:
            self.on_status_callback(True)
        return True

    def stop(self) -> None:
        if not self._running:
            return

        self._running = False
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.5)

        if self.on_status_callback:
            self.on_status_callback(False)
        if self.on_finish_callback:
            self.on_finish_callback()

    def toggle(self, config: Optional[AutoClickerConfig] = None) -> bool:
        """Toggle running state. Returns current running state."""
        if self._running:
            self.stop()
            return False
        else:
            self.start(config)
            return True

    def _precision_sleep(self, duration_seconds: float) -> None:
        """High-precision sleep using coarse sleep + perf_counter spin."""
        if duration_seconds <= 0:
            return
        target = time.perf_counter() + duration_seconds
        # Sleep for bulk of time to avoid 100% CPU usage
        if duration_seconds > 0.016:
            time.sleep(duration_seconds - 0.015)
        # Spin wait the last fraction of a millisecond for sub-millisecond precision
        while time.perf_counter() < target:
            if self._stop_event.is_set():
                break

    def _calculate_cps(self, now: float) -> float:
        """Calculates clicks per second within a 1.0 second rolling window."""
        self._click_timestamps.append(now)
        # Remove timestamps older than 1 second
        while self._click_timestamps and (now - self._click_timestamps[0]) > 1.0:
            self._click_timestamps.popleft()
        count = len(self._click_timestamps)
        if count <= 1:
            return float(count)
        time_span = now - self._click_timestamps[0]
        return round(count / time_span, 1) if time_span > 0 else float(count)

    def _run_loop(self) -> None:
        target_clicks = self.config.repeat_count if self.config.repeat_type == "count" else None
        base_interval_sec = max(0.001, self.config.total_interval_ms / 1000.0)

        while not self._stop_event.is_set():
            now = time.perf_counter()

            # Determine target coordinates
            target_x = None
            target_y = None
            if self.config.location_type == "fixed":
                target_x = self.config.fixed_x
                target_y = self.config.fixed_y
                if self.config.randomize_location and self.config.location_jitter_px > 0:
                    r = self.config.location_jitter_px
                    target_x += random.randint(-r, r)
                    target_y += random.randint(-r, r)

            # Perform the click
            InputSender.click(
                button=self.config.button,
                click_type=self.config.click_type,
                x=target_x,
                y=target_y,
            )

            self._total_clicks += 1
            cps = self._calculate_cps(now)
            elapsed = now - self._start_time

            if self.on_click_callback:
                self.on_click_callback(self._total_clicks, cps, elapsed)

            # Check if repeat count reached
            if target_clicks is not None and self._total_clicks >= target_clicks:
                break

            # Calculate next sleep interval with optional jitter
            interval_sec = base_interval_sec
            if self.config.randomize_interval and self.config.interval_jitter_ms > 0:
                jitter = random.uniform(-self.config.interval_jitter_ms, self.config.interval_jitter_ms) / 1000.0
                interval_sec = max(0.001, interval_sec + jitter)

            self._precision_sleep(interval_sec)

        self._running = False
        if self.on_status_callback:
            self.on_status_callback(False)
        if self.on_finish_callback:
            self.on_finish_callback()
