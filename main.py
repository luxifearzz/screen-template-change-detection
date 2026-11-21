"""
ChangeAndClick - Entry point.

Wires together all dependencies (Composition Root) and starts the
automation pipeline.  The pipeline runs on the REAL screen using mss
for capture and pyautogui for mouse clicks.
"""

import sys
from pathlib import Path

# Ensure the project root is on sys.path so `src` is importable.
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.config.settings import load_config  # noqa: E402
from src.core.change_detector import PixelChangeDetector  # noqa: E402
from src.core.mouse_controller import PyAutoGuiMouseController  # noqa: E402
from src.core.screen_capture import MssScreenCapturer  # noqa: E402
from src.core.template_matcher import OpenCvTemplateMatcher  # noqa: E402
from src.orchestrator import ScreenAutomationOrchestrator  # noqa: E402
from src.stages.stage1 import Stage1InitialDetection  # noqa: E402
from src.stages.stage2 import Stage2OptionDetection  # noqa: E402


def build_pipeline(config) -> ScreenAutomationOrchestrator:
    """Assemble all components and return a configured orchestrator.

    This is the Composition Root — the only place where concrete
    implementations are instantiated and injected.
    """
    # --- Low-level dependencies -------------------------------------
    screen_capturer = MssScreenCapturer(monitor_index=1)
    template_matcher = OpenCvTemplateMatcher(
        threshold=config.MATCH_THRESHOLD
    )
    change_detector = PixelChangeDetector(
        change_threshold=config.CHANGE_THRESHOLD,
        confirm_frames=config.CONFIRM_FRAMES,
    )
    mouse_controller = PyAutoGuiMouseController()

    # --- Stages ------------------------------------------------------
    stage1 = Stage1InitialDetection(
        config=config,
        screen_capturer=screen_capturer,
        template_matcher=template_matcher,
        change_detector=change_detector,
        mouse_controller=mouse_controller,
    )

    stage2 = Stage2OptionDetection(
        config=config,
        screen_capturer=screen_capturer,
        template_matcher=template_matcher,
        mouse_controller=mouse_controller,
    )

    # --- Orchestrator ------------------------------------------------
    orchestrator = ScreenAutomationOrchestrator(config=config)
    orchestrator.register_stage("STAGE_1", stage1)
    orchestrator.register_stage("STAGE_2", stage2)
    orchestrator.set_initial_stage("STAGE_1")

    return orchestrator, screen_capturer


def main() -> None:
    """Application entry point."""
    print("ChangeAndClick starting...")
    print("Real screen capture + mouse click mode.")

    config = load_config()

    # Validate that template files exist before starting.
    required_templates = [
        config.INITIAL_TEMPLATE_PATH,
        config.OPTION_A_TEMPLATE_PATH,
        config.OPTION_B_TEMPLATE_PATH,
        config.FINISHED_TEMPLATE_PATH,
    ]
    for path in required_templates:
        if not path.exists():
            print(f"ERROR: Template not found: {path}")
            sys.exit(1)

    print("All templates found. Starting pipeline...")

    orchestrator, screen_capturer = build_pipeline(config)

    try:
        orchestrator.run()
    except KeyboardInterrupt:
        print("\nStopped by user (Ctrl+C).")
    finally:
        screen_capturer.close()
        print("Cleanup complete.")


if __name__ == "__main__":
    main()