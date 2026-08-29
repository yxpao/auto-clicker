"""High-performance Windows Input Injection using Win32 SendInput."""

from __future__ import annotations
import ctypes
from ctypes import wintypes
import time
from typing import Optional

from src.core.models import MouseButton, ClickType

# Windows API Constants
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

# Mouse Flags
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_XDOWN = 0x0080
MOUSEEVENTF_XUP = 0x0100
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_HWHEEL = 0x1000
MOUSEEVENTF_ABSOLUTE = 0x8000

# Keyboard Flags
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_SCANCODE = 0x0008

# Virtual Key Mapping
VK_MAP = {
    "backspace": 0x08,
    "tab": 0x09,
    "clear": 0x0C,
    "enter": 0x0D,
    "return": 0x0D,
    "shift": 0x10,
    "ctrl": 0x11,
    "control": 0x11,
    "alt": 0x12,
    "pause": 0x13,
    "caps_lock": 0x14,
    "capslock": 0x14,
    "esc": 0x1B,
    "escape": 0x1B,
    "space": 0x20,
    "page_up": 0x21,
    "page_down": 0x22,
    "end": 0x23,
    "home": 0x24,
    "left": 0x25,
    "up": 0x26,
    "right": 0x27,
    "down": 0x28,
    "print_screen": 0x2C,
    "insert": 0x2D,
    "delete": 0x2E,
    "cmd": 0x5B,
    "win": 0x5B,
    "windows": 0x5B,
    "numpad0": 0x60,
    "numpad1": 0x61,
    "numpad2": 0x62,
    "numpad3": 0x63,
    "numpad4": 0x64,
    "numpad5": 0x65,
    "numpad6": 0x66,
    "numpad7": 0x67,
    "numpad8": 0x68,
    "numpad9": 0x69,
    "multiply": 0x6A,
    "add": 0x6B,
    "subtract": 0x6D,
    "decimal": 0x6E,
    "divide": 0x6F,
    "num_lock": 0x90,
    "scroll_lock": 0x91,
}
# Add F1 - F24
for i in range(1, 25):
    VK_MAP[f"f{i}"] = 0x6F + i

# Ctypes Structure Definitions
ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class _INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("u", _INPUT_UNION),
    ]


LPINPUT = ctypes.POINTER(INPUT)
SendInput = ctypes.windll.user32.SendInput
SendInput.argtypes = (wintypes.UINT, LPINPUT, ctypes.c_int)
SendInput.restype = wintypes.UINT

SetCursorPos = ctypes.windll.user32.SetCursorPos
SetCursorPos.argtypes = (ctypes.c_int, ctypes.c_int)
SetCursorPos.restype = wintypes.BOOL

GetCursorPos = ctypes.windll.user32.GetCursorPos
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
GetCursorPos.argtypes = [ctypes.POINTER(POINT)]

VkKeyScanW = ctypes.windll.user32.VkKeyScanW
VkKeyScanW.argtypes = [wintypes.WCHAR]
VkKeyScanW.restype = wintypes.SHORT


class InputSender:
    """Provides fast, hardware-level Windows input generation via SendInput."""

    @staticmethod
    def get_cursor_position() -> tuple[int, int]:
        pt = POINT()
        GetCursorPos(ctypes.byref(pt))
        return pt.x, pt.y

    @staticmethod
    def move_cursor(x: int, y: int) -> None:
        SetCursorPos(int(x), int(y))

    @staticmethod
    def _send_inputs(inputs: list[INPUT]) -> int:
        if not inputs:
            return 0
        n = len(inputs)
        arr = (INPUT * n)(*inputs)
        return SendInput(n, arr, ctypes.sizeof(INPUT))

    @staticmethod
    def _mouse_input(flags: int, data: int = 0, dx: int = 0, dy: int = 0) -> INPUT:
        inp = INPUT()
        inp.type = INPUT_MOUSE
        inp.u.mi.dx = dx
        inp.u.mi.dy = dy
        inp.u.mi.mouseData = data
        inp.u.mi.dwFlags = flags
        inp.u.mi.time = 0
        inp.u.mi.dwExtraInfo = 0
        return inp

    @classmethod
    def mouse_down(cls, button: MouseButton = MouseButton.LEFT, x: Optional[int] = None, y: Optional[int] = None) -> None:
        if x is not None and y is not None:
            cls.move_cursor(x, y)

        flag = MOUSEEVENTF_LEFTDOWN
        data = 0
        if button == MouseButton.RIGHT:
            flag = MOUSEEVENTF_RIGHTDOWN
        elif button == MouseButton.MIDDLE:
            flag = MOUSEEVENTF_MIDDLEDOWN
        elif button == MouseButton.X1:
            flag = MOUSEEVENTF_XDOWN
            data = 1
        elif button == MouseButton.X2:
            flag = MOUSEEVENTF_XDOWN
            data = 2

        inp = cls._mouse_input(flag, data)
        cls._send_inputs([inp])

    @classmethod
    def mouse_up(cls, button: MouseButton = MouseButton.LEFT, x: Optional[int] = None, y: Optional[int] = None) -> None:
        if x is not None and y is not None:
            cls.move_cursor(x, y)

        flag = MOUSEEVENTF_LEFTUP
        data = 0
        if button == MouseButton.RIGHT:
            flag = MOUSEEVENTF_RIGHTUP
        elif button == MouseButton.MIDDLE:
            flag = MOUSEEVENTF_MIDDLEUP
        elif button == MouseButton.X1:
            flag = MOUSEEVENTF_XUP
            data = 1
        elif button == MouseButton.X2:
            flag = MOUSEEVENTF_XUP
            data = 2

        inp = cls._mouse_input(flag, data)
        cls._send_inputs([inp])

    @classmethod
    def click(cls, button: MouseButton = MouseButton.LEFT, click_type: ClickType = ClickType.SINGLE, x: Optional[int] = None, y: Optional[int] = None) -> None:
        if x is not None and y is not None:
            cls.move_cursor(x, y)

        if click_type == ClickType.HOLD:
            cls.mouse_down(button)
            return

        cls.mouse_down(button)
        cls.mouse_up(button)

        if click_type == ClickType.DOUBLE:
            time.sleep(0.04)  # Small realistic gap between double-clicks
            cls.mouse_down(button)
            cls.mouse_up(button)

    @classmethod
    def mouse_wheel(cls, dy: int = 0, dx: int = 0) -> None:
        inputs = []
        if dy != 0:
            # 120 units per notch in Win32
            inputs.append(cls._mouse_input(MOUSEEVENTF_WHEEL, data=int(dy * 120)))
        if dx != 0:
            inputs.append(cls._mouse_input(MOUSEEVENTF_HWHEEL, data=int(dx * 120)))
        if inputs:
            cls._send_inputs(inputs)

    @classmethod
    def _key_input(cls, vk: int = 0, scan: int = 0, flags: int = 0) -> INPUT:
        inp = INPUT()
        inp.type = INPUT_KEYBOARD
        inp.u.ki.wVk = vk
        inp.u.ki.wScan = scan
        inp.u.ki.dwFlags = flags
        inp.u.ki.time = 0
        inp.u.ki.dwExtraInfo = 0
        return inp

    @classmethod
    def _resolve_vk(cls, key: str) -> tuple[int, int, int]:
        """Resolves key string to (vk, scan, flags)."""
        key_lower = key.lower()
        if key_lower in VK_MAP:
            vk = VK_MAP[key_lower]
            flags = KEYEVENTF_EXTENDEDKEY if vk in (0x5B, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x2D, 0x2E) else 0
            return vk, 0, flags

        if len(key) == 1:
            res = VkKeyScanW(key)
            if res != -1:
                vk = res & 0xFF
                return vk, 0, 0

        # Fallback: scan code / char code
        return ord(key[0].upper()) if key else 0, 0, 0

    @classmethod
    def key_down(cls, key: str) -> None:
        vk, scan, flags = cls._resolve_vk(key)
        inp = cls._key_input(vk=vk, scan=scan, flags=flags)
        cls._send_inputs([inp])

    @classmethod
    def key_up(cls, key: str) -> None:
        vk, scan, flags = cls._resolve_vk(key)
        inp = cls._key_input(vk=vk, scan=scan, flags=flags | KEYEVENTF_KEYUP)
        cls._send_inputs([inp])

    @classmethod
    def key_tap(cls, key: str) -> None:
        cls.key_down(key)
        cls.key_up(key)

    @classmethod
    def type_text(cls, text: str) -> None:
        """Type Unicode text cleanly without virtual key conversion glitches."""
        if not text:
            return
        inputs = []
        for char in text:
            code = ord(char)
            # Unicode key down
            inputs.append(cls._key_input(vk=0, scan=code, flags=KEYEVENTF_UNICODE))
            # Unicode key up
            inputs.append(cls._key_input(vk=0, scan=code, flags=KEYEVENTF_UNICODE | KEYEVENTF_KEYUP))
        cls._send_inputs(inputs)
