# ruff: noqa: E402, F401

import sys
from pathlib import Path

root = Path(__file__).parent
prod_dir = root / "lib"
dev_dir = root / "venv" / "lib" / "site-packages"

lib_dir = prod_dir if prod_dir.exists() else dev_dir

sys.path.extend([root.as_posix(), lib_dir.as_posix()])

from flogin import Pip
from flogin.utils import setup_logging

setup_logging()

with Pip(lib_dir) as pip:
    pip.ensure_installed("msgspec==0.19.0", module="msgspec._core")

from plugin.plugin import RtfmPlugin

if __name__ == "__main__":
    RtfmPlugin().run(setup_default_log_handler=False)
