# ruff: noqa: E402, F401

import os
import sys

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)
sys.path.append(os.path.join(parent_folder_path, "lib"))
sys.path.append(os.path.join(parent_folder_path, "venv", "lib", "site-packages"))

from flogin.utils import print, setup_logging

setup_logging()

# Since msgspec is primarily written in C and uses pyd files, the pyd files need to be generated for the user's system
# So if msgspec._core can not be imported, force reinstall the package on the user's system so that the proper pyd files are generated.

try:
    import msgspec._core
except ModuleNotFoundError:
    import subprocess  # nosec

    libs = (
        os.path.join("venv", "lib", "site-packages")
        if os.path.exists("venv")
        else "lib"
    )

    subprocess.run(  # nosec
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--force-reinstall",
            "-U",
            "msgspec",
            "-t",
            libs,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"Installed msgspec at {libs!r}")

from plugin.plugin import RtfmPlugin

if __name__ == "__main__":
    RtfmPlugin().run(setup_default_log_handler=False)
