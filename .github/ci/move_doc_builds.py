import os
from pathlib import Path


def main():
    ci_dir = Path(__file__)
    root_dir = Path(*ci_dir.parts[0:-3])
    builds_dir = root_dir / "docs" / "_build"
    # print(root_dir.parts)
    for file in builds_dir.rglob("*"):
        relative_fp = Path(str(file).removeprefix(str(builds_dir)))
        # print(relative_fp.parts)
        dest_fp = Path(*root_dir.parts + relative_fp.parts[1:]).resolve()
        print(f"Moving {relative_fp} to {dest_fp}")
        os.rename(file, dest_fp)


if __name__ == "__main__":
    main()
