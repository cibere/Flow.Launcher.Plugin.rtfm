from pathlib import Path
import os
import re
import jinja2

VERSION_RE = re.compile(
    r"(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<micro>[0-9]+)(?:(?P<level>[ab])(?P<serial>[0-9]*))?"
)


def main():
    ci_dir = Path(os.path.dirname(__file__))
    root_dir = Path(*ci_dir.parts[:-2])

    index_fp = root_dir / "index.html"

    versions = [
        folder.name
        for folder in root_dir.glob("*")
        if folder.is_dir and VERSION_RE.fullmatch(folder.name)
    ]

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(ci_dir))
    template = env.get_template("index_template.html")

    with index_fp.open("w", encoding="UTF-8") as f:
        f.write(template.render(versions=versions))


if __name__ == "__main__":
    main()