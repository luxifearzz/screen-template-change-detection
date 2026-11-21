"""
Application configuration.

Centralizes all settings in one place (Single Responsibility Principle).
Values can be overridden via environment variables or a config file in the future.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    """Immutable application configuration."""

    # ------------------------------------------------------------------
    # Paths
    # ------------------------------------------------------------------
    ROOT_DIR: Path
    TEMPLATE_DIR: Path

    INITIAL_TEMPLATE_PATH: Path
    OPTION_A_TEMPLATE_PATH: Path
    OPTION_B_TEMPLATE_PATH: Path
    FINISHED_TEMPLATE_PATH: Path

    # ------------------------------------------------------------------
    # Template matching
    # ------------------------------------------------------------------
    MATCH_THRESHOLD: float = 0.92

    # ------------------------------------------------------------------
    # Change detection
    # ------------------------------------------------------------------
    CHANGE_THRESHOLD: float = 6.0
    CONFIRM_FRAMES: int = 3

    # ------------------------------------------------------------------
    # Timing (seconds)
    # ------------------------------------------------------------------
    SCAN_INTERVAL: float = 0.5
    MONITOR_INTERVAL: float = 0.15

    # ------------------------------------------------------------------
    # Display / Debug
    # ------------------------------------------------------------------
    SHOW_DEBUG: bool = True


def load_config() -> AppConfig:
    """Load configuration from defaults.

    Returns:
        AppConfig: Frozen configuration instance.
    """
    root_dir = Path(__file__).resolve().parents[2]  # project root
    template_dir = root_dir / "images" / "templates"

    return AppConfig(
        ROOT_DIR=root_dir,
        TEMPLATE_DIR=template_dir,
        INITIAL_TEMPLATE_PATH=template_dir / "initial.png",
        OPTION_A_TEMPLATE_PATH=template_dir / "option_a.png",
        OPTION_B_TEMPLATE_PATH=template_dir / "option_b.png",
        FINISHED_TEMPLATE_PATH=template_dir / "finished.png",
    )
