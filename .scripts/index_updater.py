from __future__ import annotations

import errno
import os
import re
from pathlib import Path
from typing import Literal, NamedTuple

import jinja2

VERSION_RE = re.compile(
    r"(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<micro>[0-9]+)(?:(?P<level>[ab])(?P<serial>[0-9]*))?"
)
ci_dir = Path(os.path.dirname(__file__))
root_dir = Path(*ci_dir.parts[:-1])

index_fp = root_dir / "index.html"


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    level: Literal["f", "a"]
    serial: int

    @classmethod
    def from_str(cls, match: re.Match) -> VersionInfo:
        return cls(
            major=int(match["major"]),
            minor=int(match["minor"]),
            micro=int(match["micro"]),
            level=match.group("level") or "f",
            serial=int(match.group("serial")),
        )

    def match_str(self) -> int:
        return int(f"{self.major}{self.minor}{self.micro}")

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.micro}{self.level if self.level != 'f' else ''}{self.serial if self.serial != 0 else ''}"


def symlink_force(target, link_name):
    try:
        os.symlink(target, link_name)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(link_name)
            os.symlink(target, link_name)
        else:
            print(e.errno)
            raise e


def update_latest_symlink(versions: list[VersionInfo]):
    newest: VersionInfo = versions[0]

    for ver in versions:
        if ver.level == "f":
            continue

        if ver.match_str() > newest.match_str():
            newest = ver
        elif ver.match_str() == newest.match_str():
            if ver.serial > newest.serial:
                newest = ver
            else:
                ver = newest

    temp_path = root_dir / "latest-temp"
    actual_path = root_dir / "latest"
    symlink_force(temp_path, root_dir / str(newest))
    # with open(temp_path, "w") as f:
    #     f.write(str(newest))
    actual_path.unlink(missing_ok=True)
    os.replace(temp_path, actual_path)
    print(f"Latest symlink now links to {newest}")


def main():
    versions = [
        VersionInfo.from_str(match)
        for folder in root_dir.glob("*")
        if folder.is_dir and (match := VERSION_RE.fullmatch(folder.name))
    ]
    print(f"Versions: {', '.join([str(v) for v in versions])}")
    update_latest_symlink(versions)

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(ci_dir))
    template = env.get_template("template.html")
    code = template.render(versions=versions + ["latest"])

    with index_fp.open("w", encoding="UTF-8") as f:
        f.write(code)

    print(f"Wrote to {index_fp!r}")
    print(code)


if __name__ == "__main__":
    main()
