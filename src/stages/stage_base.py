"""
Base class for pipeline stages.

Provides shared helpers for loading templates and converting
capture-relative coordinates to absolute screen coordinates.
"""

from pathlib import Path
from typing import Dict, Optional, Tuple

import cv2
import numpy as np

from src.config.settings import AppConfig
from src.core.interfaces import (
    IChangeDetector,
    IMouseController,
    IScreenCapturer,
    ITemplateMatcher,
    TemplateMatchResult,
)


class StageBase:
    """Base helper for all stages."""

    def __init__(
        self,
        config: AppConfig,
        screen_capturer: IScreenCapturer,
        template_matcher: ITemplateMatcher,
        mouse_controller: IMouseController,
    ) -> None:
        self.config = config
        self.screen_capturer = screen_capturer
        self.template_matcher = template_matcher
        self.mouse_controller = mouse_controller
        self._monitor_offset: Tuple[int, int] = (0, 0)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _load_template(self, path: Path) -> np.ndarray:
        """Load a grayscale template from *path*."""
        image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise FileNotFoundError(f"Cannot load template: {path}")
        return image

    def _refresh_offset(self) -> None:
        """Update the monitor offset used for coordinate conversion."""
        self._monitor_offset = self.screen_capturer.get_monitor_offset()

    def _to_screen_coords(
        self, capture_x: int, capture_y: int
    ) -> Tuple[int, int]:
        """Convert capture-relative coordinates to absolute screen coordinates."""
        offset_x, offset_y = self._monitor_offset
        return offset_x + capture_x, offset_y + capture_y

    def _match_on_full_screen(
        self, template: np.ndarray
    ) -> TemplateMatchResult:
        """Capture full screen and run template matching on it."""
        self._refresh_offset()
        scene = self.screen_capturer.capture_full_screen()
        return self.template_matcher.match(scene, template)