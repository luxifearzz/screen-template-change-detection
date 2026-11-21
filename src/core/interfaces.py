"""
Abstract base classes (interfaces) for the automation pipeline.

These interfaces define the contracts that concrete implementations must satisfy.
Following SOLID principles:
- ISP: Small, focused interfaces.
- DIP: High-level modules depend on abstractions, not concretions.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np


@dataclass(frozen=True)
class TemplateMatchResult:
    """Result of a template matching operation."""

    found: bool
    score: float
    bbox: Optional[Tuple[int, int, int, int]]  # (x, y, width, height)
    center: Optional[Tuple[int, int]]  # (cx, cy)


@dataclass(frozen=True)
class ChangeResult:
    """Result of comparing a current frame against a baseline."""

    changed: bool
    score: float
    confirmed: bool
    count: int


class IScreenCapturer(ABC):
    """Captures screen images (full screen or ROI)."""

    @abstractmethod
    def capture_full_screen(self) -> np.ndarray:
        """Capture the full primary screen as a grayscale numpy array."""
        ...

    @abstractmethod
    def capture_roi(
        self, left: int, top: int, width: int, height: int
    ) -> np.ndarray:
        """Capture a region of interest as a grayscale numpy array."""
        ...

    @abstractmethod
    def get_monitor_offset(self) -> Tuple[int, int]:
        """Return the (left, top) offset of the primary monitor."""
        ...


class ITemplateMatcher(ABC):
    """Matches a template image inside a scene image."""

    @abstractmethod
    def match(self, scene: np.ndarray, template: np.ndarray) -> TemplateMatchResult:
        """Return the best match result for *template* inside *scene*."""
        ...


class IChangeDetector(ABC):
    """Detects changes between a baseline frame and subsequent frames."""

    @abstractmethod
    def set_baseline(self, image: np.ndarray) -> None:
        """Store the reference (baseline) image."""
        ...

    @abstractmethod
    def compare(self, current: np.ndarray) -> ChangeResult:
        """Compare *current* against the baseline and return change info."""
        ...

    @abstractmethod
    def reset(self) -> None:
        """Reset internal state (baseline and counters)."""
        ...


class IMouseController(ABC):
    """Controls the physical mouse (click, position)."""

    @abstractmethod
    def click_at_current_position(self) -> None:
        """Click once at the mouse's current screen position."""
        ...

    @abstractmethod
    def click_at(self, x: int, y: int) -> None:
        """Click once at the absolute screen position (x, y)."""
        ...

    @abstractmethod
    def get_position(self) -> Tuple[int, int]:
        """Return the current mouse position as (x, y)."""
        ...


class IStage(ABC):
    """A pipeline stage. Each stage runs until it yields a transition result."""

    @abstractmethod
    def execute(self) -> str:
        """Run the stage logic.

        Returns:
            The name of the next stage to execute, or ``"STOP"`` to terminate.
        """
        ...

    @abstractmethod
    def cleanup(self) -> None:
        """Release resources held by this stage."""
        ...