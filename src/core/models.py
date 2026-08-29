"""Data models for Auto Clicker and Macro Studio."""

from __future__ import annotations
import uuid
import random
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Optional, Dict, Any


class ActionType(str, Enum):
    CLICK = "click"
    MOUSE_DOWN = "mouse_down"
    MOUSE_UP = "mouse_up"
    MOVE = "move"
    WHEEL = "wheel"
    KEY_PRESS = "key_press"
    KEY_DOWN = "key_down"
    KEY_UP = "key_up"
    DELAY = "delay"
    TEXT = "text"


class MouseButton(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"
    X1 = "x1"
    X2 = "x2"


class ClickType(str, Enum):
    SINGLE = "single"
    DOUBLE = "double"
    HOLD = "hold"


@dataclass
class Action:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    action_type: ActionType = ActionType.CLICK
    x: Optional[int] = None
    y: Optional[int] = None
    button: Optional[MouseButton] = MouseButton.LEFT
    click_type: ClickType = ClickType.SINGLE
    key: Optional[str] = None
    text: Optional[str] = None
    wheel_dx: int = 0
    wheel_dy: int = 0
    delay_ms: float = 50.0  # Pause BEFORE executing this action
    duration_ms: float = 0.0  # Optional hold duration
    enabled: bool = True
    comment: str = ""

    def summary(self) -> str:
        """Returns a human-readable summary string for UI display."""
        if self.action_type == ActionType.CLICK:
            btn = (self.button.value.capitalize() if self.button else "Left")
            ctype = self.click_type.value.capitalize()
            pos = f"({self.x}, {self.y})" if self.x is not None and self.y is not None else "Current Pos"
            return f"{btn} Click ({ctype}) @ {pos}"
        elif self.action_type == ActionType.MOUSE_DOWN:
            btn = (self.button.value.capitalize() if self.button else "Left")
            pos = f"({self.x}, {self.y})" if self.x is not None and self.y is not None else "Current Pos"
            return f"{btn} Mouse Down @ {pos}"
        elif self.action_type == ActionType.MOUSE_UP:
            btn = (self.button.value.capitalize() if self.button else "Left")
            pos = f"({self.x}, {self.y})" if self.x is not None and self.y is not None else "Current Pos"
            return f"{btn} Mouse Up @ {pos}"
        elif self.action_type == ActionType.MOVE:
            return f"Move Cursor to ({self.x}, {self.y})"
        elif self.action_type == ActionType.WHEEL:
            direction = "Up" if self.wheel_dy > 0 else "Down" if self.wheel_dy < 0 else "H-Scroll"
            return f"Mouse Wheel {direction} ({self.wheel_dy or self.wheel_dx})"
        elif self.action_type == ActionType.KEY_PRESS:
            return f"Key Tap: [{self.key}]"
        elif self.action_type == ActionType.KEY_DOWN:
            return f"Key Down: [{self.key}]"
        elif self.action_type == ActionType.KEY_UP:
            return f"Key Up: [{self.key}]"
        elif self.action_type == ActionType.DELAY:
            return f"Wait {self.delay_ms:.1f} ms"
        elif self.action_type == ActionType.TEXT:
            preview = (self.text[:20] + "...") if self.text and len(self.text) > 20 else (self.text or "")
            return f'Type Text: "{preview}"'
        return f"Action: {self.action_type.value}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "action_type": self.action_type.value,
            "x": self.x,
            "y": self.y,
            "button": self.button.value if self.button else None,
            "click_type": self.click_type.value if self.click_type else None,
            "key": self.key,
            "text": self.text,
            "wheel_dx": self.wheel_dx,
            "wheel_dy": self.wheel_dy,
            "delay_ms": self.delay_ms,
            "duration_ms": self.duration_ms,
            "enabled": self.enabled,
            "comment": self.comment,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Action:
        action_type = ActionType(data.get("action_type", ActionType.CLICK.value))
        button_val = data.get("button")
        button = MouseButton(button_val) if button_val else None
        click_type_val = data.get("click_type")
        click_type = ClickType(click_type_val) if click_type_val else ClickType.SINGLE

        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            action_type=action_type,
            x=data.get("x"),
            y=data.get("y"),
            button=button,
            click_type=click_type,
            key=data.get("key"),
            text=data.get("text"),
            wheel_dx=data.get("wheel_dx", 0),
            wheel_dy=data.get("wheel_dy", 0),
            delay_ms=float(data.get("delay_ms", 50.0)),
            duration_ms=float(data.get("duration_ms", 0.0)),
            enabled=data.get("enabled", True),
            comment=data.get("comment", ""),
        )


@dataclass
class MacroSequence:
    name: str = "New Macro"
    actions: List[Action] = field(default_factory=list)
    repeat_count: int = 1  # 0 = infinite
    speed_multiplier: float = 1.0
    delay_between_loops_ms: float = 100.0

    def total_duration_ms(self) -> float:
        """Calculate total estimated playback duration for 1 loop."""
        base_ms = sum(a.delay_ms + a.duration_ms for a in self.actions if a.enabled)
        if self.speed_multiplier > 0:
            return base_ms / self.speed_multiplier
        return base_ms

    def scale_speed(self, multiplier: float, selected_indices: Optional[List[int]] = None) -> None:
        """
        Scale delays by multiplier factor.
        multiplier = 2.0 means macro runs 2x faster (delays halved).
        """
        if multiplier <= 0:
            return
        indices = selected_indices if selected_indices is not None else list(range(len(self.actions)))
        for idx in indices:
            if 0 <= idx < len(self.actions):
                self.actions[idx].delay_ms = max(1.0, round(self.actions[idx].delay_ms / multiplier, 2))
                if self.actions[idx].duration_ms > 0:
                    self.actions[idx].duration_ms = max(1.0, round(self.actions[idx].duration_ms / multiplier, 2))

    def shift_coordinates(self, dx: int, dy: int, selected_indices: Optional[List[int]] = None) -> None:
        """Offset coordinates for mouse actions."""
        indices = selected_indices if selected_indices is not None else list(range(len(self.actions)))
        for idx in indices:
            if 0 <= idx < len(self.actions):
                action = self.actions[idx]
                if action.x is not None:
                    action.x = max(0, action.x + dx)
                if action.y is not None:
                    action.y = max(0, action.y + dy)

    def normalize_delays(self, target_delay_ms: float, selected_indices: Optional[List[int]] = None) -> None:
        """Set a uniform delay across actions."""
        indices = selected_indices if selected_indices is not None else list(range(len(self.actions)))
        for idx in indices:
            if 0 <= idx < len(self.actions):
                self.actions[idx].delay_ms = max(0.0, float(target_delay_ms))

    def randomize_delays(self, jitter_pct: float = 20.0, selected_indices: Optional[List[int]] = None) -> None:
        """Add randomized jitter (+/- jitter_pct%) to delays for human-like replay."""
        factor_max = jitter_pct / 100.0
        indices = selected_indices if selected_indices is not None else list(range(len(self.actions)))
        for idx in indices:
            if 0 <= idx < len(self.actions):
                current = self.actions[idx].delay_ms
                factor = 1.0 + random.uniform(-factor_max, factor_max)
                self.actions[idx].delay_ms = max(1.0, round(current * factor, 1))

    def trim_pauses(self, max_delay_ms: float = 1000.0, selected_indices: Optional[List[int]] = None) -> None:
        """Cap any delay exceeding max_delay_ms down to max_delay_ms."""
        indices = selected_indices if selected_indices is not None else list(range(len(self.actions)))
        for idx in indices:
            if 0 <= idx < len(self.actions):
                if self.actions[idx].delay_ms > max_delay_ms:
                    self.actions[idx].delay_ms = float(max_delay_ms)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "actions": [a.to_dict() for a in self.actions],
            "repeat_count": self.repeat_count,
            "speed_multiplier": self.speed_multiplier,
            "delay_between_loops_ms": self.delay_between_loops_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MacroSequence:
        actions_raw = data.get("actions", [])
        actions = [Action.from_dict(a) for a in actions_raw]
        return cls(
            name=data.get("name", "Untitled Macro"),
            actions=actions,
            repeat_count=data.get("repeat_count", 1),
            speed_multiplier=float(data.get("speed_multiplier", 1.0)),
            delay_between_loops_ms=float(data.get("delay_between_loops_ms", 100.0)),
        )


@dataclass
class AutoClickerConfig:
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    milliseconds: int = 100
    button: MouseButton = MouseButton.LEFT
    click_type: ClickType = ClickType.SINGLE
    repeat_type: str = "infinite"  # "infinite" | "count"
    repeat_count: int = 100
    location_type: str = "current"  # "current" | "fixed"
    fixed_x: int = 0
    fixed_y: int = 0
    randomize_interval: bool = False
    interval_jitter_ms: float = 10.0
    randomize_location: bool = False
    location_jitter_px: int = 3
    hotkey_start_stop: str = "F6"

    @property
    def total_interval_ms(self) -> float:
        return (
            self.hours * 3600 * 1000
            + self.minutes * 60 * 1000
            + self.seconds * 1000
            + self.milliseconds
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hours": self.hours,
            "minutes": self.minutes,
            "seconds": self.seconds,
            "milliseconds": self.milliseconds,
            "button": self.button.value,
            "click_type": self.click_type.value,
            "repeat_type": self.repeat_type,
            "repeat_count": self.repeat_count,
            "location_type": self.location_type,
            "fixed_x": self.fixed_x,
            "fixed_y": self.fixed_y,
            "randomize_interval": self.randomize_interval,
            "interval_jitter_ms": self.interval_jitter_ms,
            "randomize_location": self.randomize_location,
            "location_jitter_px": self.location_jitter_px,
            "hotkey_start_stop": self.hotkey_start_stop,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AutoClickerConfig:
        return cls(
            hours=data.get("hours", 0),
            minutes=data.get("minutes", 0),
            seconds=data.get("seconds", 0),
            milliseconds=data.get("milliseconds", 100),
            button=MouseButton(data.get("button", MouseButton.LEFT.value)),
            click_type=ClickType(data.get("click_type", ClickType.SINGLE.value)),
            repeat_type=data.get("repeat_type", "infinite"),
            repeat_count=data.get("repeat_count", 100),
            location_type=data.get("location_type", "current"),
            fixed_x=data.get("fixed_x", 0),
            fixed_y=data.get("fixed_y", 0),
            randomize_interval=data.get("randomize_interval", False),
            interval_jitter_ms=float(data.get("interval_jitter_ms", 10.0)),
            randomize_location=data.get("randomize_location", False),
            location_jitter_px=int(data.get("location_jitter_px", 3)),
            hotkey_start_stop=data.get("hotkey_start_stop", "F6"),
        )
