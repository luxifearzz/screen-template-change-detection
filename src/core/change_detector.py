"""
Pixel-difference change detection implementation.

Responsibility: detect whether a region has changed compared to a baseline.
(Single Responsibility Principle)
"""

from typing import Optional

import cv2
import numpy as np

from .interfaces import IChangeDetector, ChangeResult


class PixelChangeDetector(IChangeDetector):
    """Compare frames using absolute pixel difference and frame confirmation."""

    def __init__(
        self,
        change_threshold: float = 12.0,
        confirm_frames: int = 3,
    ) -> None:
        self.change_threshold = change_threshold
        self.confirm_frames = confirm_frames
        self._baseline: Optional[np.ndarray] = None
        self._changed_count = 0

    def set_baseline(self, image: np.ndarray) -> None:
        """Store the reference (baseline) image."""
        self._baseline = image.copy()
        self._changed_count = 0

    def compare(self, current: np.ndarray) -> ChangeResult:
        """Compare *current* against the baseline.

        Returns:
            ChangeResult with changed/score/confirmed/count.
        """
        if self._baseline is None:
            raise RuntimeError("Baseline has not been initialized.")

        if current.shape != self._baseline.shape:
            raise ValueError(
                "Current image and baseline must have the same dimensions."
            )

        diff = cv2.absdiff(self._baseline, current)
        change_score = float(np.mean(diff))

        is_changed = change_score > self.change_threshold

        if is_changed:
            self._changed_count += 1
        else:
            self._changed_count = 0

        confirmed = self._changed_count >= self.confirm_frames

        return ChangeResult(
            changed=is_changed,
            score=change_score,
            confirmed=confirmed,
            count=self._changed_count,
        )

    def reset(self) -> None:
        """Reset internal state."""
        self._baseline = None
        self._changed_count = 0