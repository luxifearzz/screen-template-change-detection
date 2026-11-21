"""
Stage 2: After action 01, scan full screen continuously for
OPTION_A, OPTION_B, or FINISHED templates.

- OPTION templates -> click once at detected center (action 02), keep scanning.
- FINISHED template -> stop the program.
"""

import time
from typing import Dict, Optional

import cv2
import numpy as np

from src.config.settings import AppConfig
from src.core.interfaces import (
    IMouseController,
    IScreenCapturer,
    ITemplateMatcher,
    TemplateMatchResult,
)
from src.stages.stage_base import StageBase


class Stage2OptionDetection(StageBase):
    """Stage 2 pipeline logic."""

    STAGE_NAME = "STAGE_2"
    STOP_SIGNAL = "STOP"

    def __init__(
        self,
        config: AppConfig,
        screen_capturer: IScreenCapturer,
        template_matcher: ITemplateMatcher,
        mouse_controller: IMouseController,
    ) -> None:
        super().__init__(config, screen_capturer, template_matcher, mouse_controller)
        self._option_a_template: Optional[np.ndarray] = None
        self._option_b_template: Optional[np.ndarray] = None
        self._finished_template: Optional[np.ndarray] = None

    def execute(self) -> str:
        """Run Stage 2 until FINISHED is detected.

        Returns:
            "STOP" when FINISHED is found.
        """
        self._option_a_template = self._load_template(
            self.config.OPTION_A_TEMPLATE_PATH
        )
        self._option_b_template = self._load_template(
            self.config.OPTION_B_TEMPLATE_PATH
        )
        self._finished_template = self._load_template(
            self.config.FINISHED_TEMPLATE_PATH
        )

        print("[Stage 2] Scanning full screen for OPTION / FINISHED templates...")

        while True:
            self._refresh_offset()
            scene = self.screen_capturer.capture_full_screen()

            # Match all three templates on the full scene.
            result_a = self.template_matcher.match(
                scene, self._option_a_template
            )
            result_b = self.template_matcher.match(
                scene, self._option_b_template
            )
            result_finished = self.template_matcher.match(
                scene, self._finished_template
            )

            # FINISHED takes priority -> stop program.
            if result_finished.found and result_finished.center is not None:
                sx, sy = self._to_screen_coords(
                    result_finished.center[0], result_finished.center[1]
                )
                print(
                    f"[Stage 2] FINISHED found at screen ({sx},{sy}) "
                    f"(score={result_finished.score:.3f}). Stopping."
                )
                return self.STOP_SIGNAL

            # Handle OPTION matches -> click at center (action 02).
            option_results: Dict[str, TemplateMatchResult] = {}
            if result_a.found and result_a.center is not None:
                option_results["OPTION_A"] = result_a
            if result_b.found and result_b.center is not None:
                option_results["OPTION_B"] = result_b

            if option_results:
                for label, match_result in option_results.items():
                    cx, cy = match_result.center
                    sx, sy = self._to_screen_coords(cx, cy)
                    print(
                        f"[Stage 2] {label} found at capture ({cx},{cy}) "
                        f"-> screen ({sx},{sy}) "
                        f"(score={match_result.score:.3f})"
                    )
                    # Action 02: click once at the detected center.
                    self.mouse_controller.click_at(sx, sy)
                    print(f"[Stage 2] Action 02: clicked {label} at ({sx},{sy})")

            time.sleep(self.config.SCAN_INTERVAL)

    def cleanup(self) -> None:
        """No resources to release for this stage."""
        pass