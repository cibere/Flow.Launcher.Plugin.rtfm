import os
from pathlib import Path

ci_dir = Path(__file__)
root_dir = Path(*ci_dir.parts[0:-3])
builds_dir = root_dir / "docs" / "_build"


def move_item(path: Path):
    if path.is_dir():
        for child in path.rglob("*"):
            if child.name.endswith((".pickle", ".doctree", ".doctrees")):
                continue
            move_item(child)
    else:
        relative_fp = Path(str(path).removeprefix(str(builds_dir)))

        dest_fp = Path(*root_dir.parts + relative_fp.parts[1:]).resolve()
        print(f"Moving {relative_fp} to {dest_fp}")
        os.rename(path, dest_fp)


if __name__ == "__main__":
    move_item(builds_dir)
