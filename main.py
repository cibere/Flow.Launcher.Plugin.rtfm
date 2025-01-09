import os
import sys

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)

is_prod = os.path.exists("lib")

libs_path = (
    os.path.join(parent_folder_path, "lib")
    if is_prod
    else os.path.join(parent_folder_path, "venv", "lib", "site-packages")
)

sys.path.append(libs_path)

from plugin.plugin import RtfmPlugin  # noqa: E402

# Since msgspec is primarily written in C and uses pyd files, the pyd files need to be generated for the user's system
# So if msgspec._core can not be imported, force reinstall the package on the user's system so that the proper pyd files are generated.

try:
    import msgspec._core  # noqa: F401
except ImportError:
    import subprocess

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--force-reinstall",
            "-U",
            "msgspec",
            "-t",
            libs_path,
        ]
    )

if __name__ == "__main__":
    RtfmPlugin().run()
