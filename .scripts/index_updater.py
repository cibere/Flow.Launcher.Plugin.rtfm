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
            serial=int(match.group("serial") or 0),
        )

    def to_float(self) -> float:
        return float(
            f"{self.major}{self.minor}{self.micro}.{99999999999 if self.level == 'f' else self.serial}"
        )

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


def update_dev_symlink(versions: list[VersionInfo]):
    newest: VersionInfo = versions[0]

    temp_path = root_dir / "dev-temp"
    actual_path = root_dir / "dev"

    symlink_force(str(newest), temp_path)

    actual_path.unlink(missing_ok=True)
    os.replace(temp_path, actual_path)

    print(f"dev symlink now links to {newest}")


def update_stable_symlink(versions: list[VersionInfo]):
    for version in versions:
        if version.level == "a":
            continue

        temp_path = root_dir / "stable-temp"
        actual_path = root_dir / "stable"

        symlink_force(str(version), temp_path)

        actual_path.unlink(missing_ok=True)
        os.replace(temp_path, actual_path)

        print(f"Stable symlink now links to {version}")


def main():
    unsorted_versions = [
        VersionInfo.from_str(match)
        for folder in root_dir.glob("*")
        if folder.is_dir and (match := VERSION_RE.fullmatch(folder.name))
    ]
    versions = sorted(unsorted_versions, key=lambda ver: ver.to_float(), reverse=True)
    print(f"Versions: {', '.join([str(v) for v in versions])}")

    update_dev_symlink(versions)
    update_stable_symlink(versions)

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(ci_dir))
    template = env.get_template("template.html")
    code = template.render(versions=["dev", "stable", *versions])

    with index_fp.open("w", encoding="UTF-8") as f:
        f.write(code)

    print(f"Wrote to {index_fp!r}")
    print(code)


if __name__ == "__main__":
    main()
