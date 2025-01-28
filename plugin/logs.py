import logging
import logging.handlers
import os
from pathlib import Path


class Logs:
    def __init__(self) -> None:
        self.logger: logging.Logger | None = logging.getLogger()
        self.handler: logging.Handler | None = None
        self.check_for_override()

    def check_for_override(self) -> None:
        dir = Path(os.getcwd())

        file = dir / ".flogin.prod"

        if file.exists():
            if self.handler and self.logger:
                self.handler.close()
                self.logger.removeHandler(self.handler)
            self.handler = None
            self.logger = None

    @property
    def level(self) -> int:
        if self.logger:
            return self.logger.level
        return 0

    @level.setter
    def level(self, new_level: int) -> None:
        if self.logger:
            self.logger.setLevel(new_level)

    def update_debug(self, debug_mode: bool) -> None:
        if debug_mode:
            self.level = logging.DEBUG
        else:
            self.level = logging.INFO

    def setup(self) -> None:
        """Modified from flogin.utils.setup_logging"""

        if self.logger is None:
            return

        handler = logging.handlers.RotatingFileHandler(
            "flogin.log", maxBytes=1000000, encoding="UTF-8", backupCount=1
        )

        dt_fmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(
            "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{"
        )

        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.handler = handler
