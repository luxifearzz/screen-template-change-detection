"""
Template matching implementation using OpenCV.

Responsibility: locate a template image inside a scene image.
(Single Responsibility Principle)
"""

from typing import Optional, Tuple

import cv2
import numpy as np

from .interfaces import ITemplateMatcher, TemplateMatchResult


class OpenCvTemplateMatcher(ITemplateMatcher):
    """Match templates using cv2.matchTemplate (TM_CCOEFF_NORMED)."""

    def __init__(self, threshold: float = 0.92) -> None:
        self.threshold = threshold

    def match(
        self, scene: np.ndarray, template: np.ndarray
    ) -> TemplateMatchResult:
        """Return the best match for *template* inside *scene*.

        Args:
            scene: Grayscale scene image.
            template: Grayscale template image.

        Returns:
            TemplateMatchResult with found/score/bbox/center.
        """
        scene_h, scene_w = scene.shape[:2]
        template_h, template_w = template.shape[:2]

        # Guard against template larger than scene.
        if template_h > scene_h or template_w > scene_w:
            return TemplateMatchResult(
                found=False,
                score=0.0,
                bbox=None,
                center=None,
            )

        result = cv2.matchTemplate(
            scene,
            template,
            cv2.TM_CCOEFF_NORMED,
        )
        _, max_score, _, location = cv2.minMaxLoc(result)

        x, y = int(location[0]), int(location[1])
        bbox = (x, y, template_w, template_h)
        center = (x + template_w // 2, y + template_h // 2)

        found = bool(max_score >= self.threshold)

        return TemplateMatchResult(
            found=found,
            score=float(max_score),
            bbox=bbox if found else None,
            center=center if found else None,
        )