"""
Pipeline orchestrator.

Coordinates the execution flow between stages.
Depends only on abstractions (Dependency Inversion Principle).
"""

from typing import Dict, Optional

from src.config.settings import AppConfig
from src.core.interfaces import IStage


class ScreenAutomationOrchestrator:
    """Runs stages in sequence until a stop signal is received."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._stages: Dict[str, IStage] = {}
        self._current_stage: Optional[str] = None

    def register_stage(self, name: str, stage: IStage) -> None:
        """Register a stage under *name*."""
        self._stages[name] = stage

    def set_initial_stage(self, name: str) -> None:
        """Set the stage to start from."""
        if name not in self._stages:
            raise ValueError(f"Stage '{name}' is not registered.")
        self._current_stage = name

    def run(self) -> None:
        """Execute stages until one returns 'STOP'."""
        if self._current_stage is None:
            raise RuntimeError("No initial stage has been set.")

        try:
            while self._current_stage:
                stage = self._stages[self._current_stage]
                print(f"\n=== Entering stage: {self._current_stage} ===")

                next_stage = stage.execute()

                if next_stage == "STOP":
                    print("\n=== Stop signal received. Terminating. ===")
                    break

                self._current_stage = next_stage
        finally:
            # Cleanup all stages.
            for stage in self._stages.values():
                stage.cleanup()
