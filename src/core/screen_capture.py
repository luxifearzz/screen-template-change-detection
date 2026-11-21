"""
Real screen capture implementation using the ``mss`` library.

Responsibility: capture images from the physical screen only.
(Single Responsibility Principle)
"""

from typing import Tuple

import cv2
import mss
import numpy as np

from .interfaces import IScreenCapturer


class MssScreenCapturer(IScreenCapturer):
    """Capture full screen or ROI using mss."""

    def __init__(self, monitor_index: int = 1) -> None:
        self._sct = mss.mss()
        self._monitor = self._sct.monitors[monitor_index]

    def capture_full_screen(self) -> np.ndarray:
        """Capture the full primary screen as grayscale."""
        frame = np.array(self._sct.grab(self._monitor))
        return cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)

    def capture_roi(
        self, left: int, top: int, width: int, height: int
    ) -> np.ndarray:
        """Capture a region of interest as grayscale."""
        roi = {
            "left": self._monitor["left"] + left,
            "top": self._monitor["top"] + top,
            "width": width,
            "height": height,
        }
        frame = np.array(self._sct.grab(roi))
        return cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)

    def get_monitor_offset(self) -> Tuple[int, int]:
        """Return the (left, top) offset of the primary monitor."""
        return self._monitor["left"], self._monitor["top"]

    def close(self) -> None:
        """Release the mss capture resource."""
        self._sct.close()