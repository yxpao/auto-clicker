"""Global Hotkey Listener and Dispatcher."""

from __future__ import annotations
import threading
from typing import Callable, Dict, Optional
from pynput import keyboard


class HotkeyManager:
    """Manages system-wide global hotkeys across applications."""

    def __init__(self):
        self._listener: Optional[keyboard.GlobalHotKeys] = None
        self._bindings: Dict[str, Callable[[], None]] = {}
        self._running = False
        self._lock = threading.Lock()

    def format_key_for_pynput(self, hotkey_str: str) -> str:
        """Converts user-friendly hotkey (e.g., 'F6', 'Ctrl+Shift+R') to pynput format."""
        if not hotkey_str:
            return ""

        parts = [p.strip().lower() for p in hotkey_str.split("+")]
        formatted_parts = []

        special_map = {
            "ctrl": "<ctrl>",
            "control": "<ctrl>",
            "alt": "<alt>",
            "shift": "<shift>",
            "cmd": "<cmd>",
            "win": "<cmd>",
            "windows": "<cmd>",
            "space": "<space>",
            "enter": "<enter>",
            "tab": "<tab>",
            "esc": "<esc>",
            "escape": "<esc>",
        }

        for part in parts:
            if part in special_map:
                formatted_parts.append(special_map[part])
            elif part.startswith("f") and part[1:].isdigit():
                formatted_parts.append(f"<{part}>")
            else:
                formatted_parts.append(part)

        return "+".join(formatted_parts)

    def register(self, hotkey_name: str, key_combo: str, callback: Callable[[], None]) -> None:
        """Registers or updates a named hotkey binding."""
        with self._lock:
            pynput_key = self.format_key_for_pynput(key_combo)
            if not pynput_key:
                return
            self._bindings[pynput_key] = callback
            if self._running:
                self._restart_listener()

    def unregister(self, key_combo: str) -> None:
        with self._lock:
            pynput_key = self.format_key_for_pynput(key_combo)
            if pynput_key in self._bindings:
                del self._bindings[pynput_key]
                if self._running:
                    self._restart_listener()

    def clear(self) -> None:
        with self._lock:
            self._bindings.clear()
            if self._running:
                self._restart_listener()

    def start(self) -> None:
        with self._lock:
            if self._running:
                return
            self._running = True
            self._start_listener()

    def stop(self) -> None:
        with self._lock:
            self._running = False
            if self._listener:
                self._listener.stop()
                self._listener = None

    def _start_listener(self) -> None:
        if not self._bindings:
            return
        try:
            self._listener = keyboard.GlobalHotKeys(self._bindings)
            self._listener.daemon = True
            self._listener.start()
        except Exception as e:
            print(f"[HotkeyManager] Warning: failed to bind hotkeys: {e}")

    def _restart_listener(self) -> None:
        if self._listener:
            self._listener.stop()
            self._listener = None
        self._start_listener()
