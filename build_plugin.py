import sys
import tempfile
import zipfile
from pathlib import Path


def main():
    files = [
        Path(fp)
        for fp in (
            "SettingsTemplate.yaml",
            "plugin.json",
            "main.py",
            "assets/app.png",
        )
    ]
    ignore_exts = (".dist-info", ".pyc", "__pycache__")
    plugin_include_exts = ("py", "html", "css", "js")

    plugin_dir = Path("plugin")
    for ext in plugin_include_exts:
        files.extend(plugin_dir.rglob(f"*.{ext}"))

    lib_dir = Path("lib")
    files.extend(
        [
            file
            for file in lib_dir.rglob("*")
            if not file.parent.parent.name.endswith(
                ignore_exts  # some deps include a licenses dir inside of their dist-info dir
            )
            and not file.parent.name.endswith(ignore_exts)
            and not file.name.endswith(ignore_exts)
        ]
    )

    for file in files:
        print(file.as_posix())


if __name__ == "__main__":
    main()
