"""Build the README animation from two real report screenshots.

Usage:
  python scripts/make-readme-demo-gif.py change.png software.png demo.gif
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image


def main() -> int:
    if len(sys.argv) != 4:
        raise SystemExit("usage: make-readme-demo-gif.py <change.png> <software.png> <output.gif>")
    change_path, software_path, output_path = map(Path, sys.argv[1:])
    change = Image.open(change_path).convert("P", palette=Image.Palette.ADAPTIVE, colors=256)
    software = Image.open(software_path).convert("P", palette=Image.Palette.ADAPTIVE, colors=256)
    if change.size != software.size:
        raise SystemExit("screenshots must have the same dimensions")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    change.save(
        output_path,
        save_all=True,
        append_images=[software],
        duration=[4000, 4000],
        loop=0,
        disposal=2,
        optimize=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
