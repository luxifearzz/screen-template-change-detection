"""
Stage 1: Find INITIAL template on full screen, monitor its ROI for changes,
then click once at the current mouse position (action 01).
"""

import time
from typing import Optional

import cv2
import numpy as np

from src.config.settings import AppConfig
from src.core.interfaces import (
    IChangeDetector,
    IMouseController,
    IScreenCapturer,
    ITemplateMatcher,
)
from src.stages.stage_base import StageBase


class Stage1InitialDetection(StageBase):
    """Stage 1 pipeline logic."""

    STAGE_NAME = "STAGE_1"
    NEXT_STAGE = "STAGE_2"

    def __init__(
        self,
        config: AppConfig,
        screen_capturer: IScreenCapturer,
        template_matcher: ITemplateMatcher,
        change_detector: IChangeDetector,
        mouse_controller: IMouseController,
    ) -> None:
        super().__init__(config, screen_capturer, template_matcher, mouse_controller)
        self.change_detector = change_detector
        self._initial_template: Optional[np.ndarray] = None

    def execute(self) -> str:
        """Run Stage 1 until a change is confirmed, then click at mouse position.

        Returns:
            The next stage name ("STAGE_2").
        """
        self._initial_template = self._load_template(
            self.config.INITIAL_TEMPLATE_PATH
        )

        print("[Stage 1] Scanning full screen for INITIAL template...")

        # ----------------------------------------------------------
        # Step A: Continuously scan full screen for INITIAL template.
        # ----------------------------------------------------------
        while True:
            result = self._match_on_full_screen(self._initial_template)

            if result.found and result.bbox is not None:
                print(
                    f"[Stage 1] INITIAL found at {result.bbox} "
                    f"(score={result.score:.3f})"
                )
                break
            else:
                print(
                    f"[Stage 1] Scanning... best match score={result.score:.3f}"
                )

            time.sleep(self.config.SCAN_INTERVAL)

        # ----------------------------------------------------------
        # Step B: Focus on the detected ROI and wait for changes.
        # ----------------------------------------------------------
        x, y, w, h = result.bbox

        # Capture baseline image of the ROI.
        baseline = self.screen_capturer.capture_roi(x, y, w, h)
        self.change_detector.set_baseline(baseline)

        print(
            f"[Stage 1] Monitoring ROI ({x},{y},{w}x{h}) for changes..."
        )

        while True:
            current = self.screen_capturer.capture_roi(x, y, w, h)
            change_report = self.change_detector.compare(current)

            # (ref1) Print change score every frame
            # print(
            #     f"[Stage 1] Change score={change_report.score:.2f} | "
            #     f"count={change_report.count}/{self.config.CONFIRM_FRAMES}"
            # )

            if change_report.confirmed:
                print(
                    f"[Stage 1] Change confirmed! "
                    # comment if uncomment above (ref1)
                    f"{change_report.count} frame(s) "
                    f"Final score={change_report.score:.2f}"
                )
                break

            time.sleep(self.config.MONITOR_INTERVAL)

        # ----------------------------------------------------------
        # Step C: Action 01 — click once at current mouse position.
        # ----------------------------------------------------------
        mx, my = self.mouse_controller.get_position()
        print(
            f"[Stage 1] Action 01: clicking at current mouse position ({mx},{my})")
        self.mouse_controller.click_at_current_position()

        self.change_detector.reset()
        return self.NEXT_STAGE

    def cleanup(self) -> None:
        """No resources to release for this stage."""
        pass
