"""
Real mouse controller implementation using ``pyautogui``.

Responsibility: move/click the physical mouse only.
(Single Responsibility Principle)
"""

from typing import Tuple

import pyautogui

from .interfaces import IMouseController


class PyAutoGuiMouseController(IMouseController):
    """Control the physical mouse via pyautogui."""

    def click_at_current_position(self) -> None:
        """Click once at the mouse's current screen position."""
        pyautogui.click()

    def click_at(self, x: int, y: int) -> None:
        """Click once at the absolute screen position (x, y)."""
        pyautogui.click(x, y)

    def get_position(self) -> Tuple[int, int]:
        """Return the current mouse position as (x, y)."""
        x, y = pyautogui.position()
        return int(x), int(y)