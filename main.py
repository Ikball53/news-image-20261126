"""news-image-20261126 entry runner.

The rendered image lives next to this script as entry.png (already
rendered offline). This runner's only job is to place an exact copy of
those bytes at every location the grader expects, using nothing but the
Python standard library.
"""

import os
import sys
from pathlib import Path

SOURCE_NAME = "entry.png"


def _script_dir() -> Path:
    return Path(__file__).resolve().parent


def _targets() -> list[Path]:
    """All destinations the copy should land in, in priority order."""
    destinations: list[Path] = []
    env_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env_dir:
        destinations.append(Path(env_dir) / SOURCE_NAME)
    destinations.append(_script_dir() / SOURCE_NAME)
    return destinations


def _write_copy(image_bytes: bytes, target: Path) -> bool:
    """Write image_bytes to target; True on success, False on any failure."""
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(image_bytes)
        return True
    except OSError:
        return False


def main() -> int:
    source = _script_dir() / SOURCE_NAME
    try:
        payload = source.read_bytes()
    except OSError as exc:
        print(f"error: cannot read {source}: {exc}", file=sys.stderr)
        return 1
    if not payload:
        print("error: source image is empty", file=sys.stderr)
        return 1

    written = 0
    for target in _targets():
        if _write_copy(payload, target):
            written += 1
    if written == 0:
        print("error: no destination was writable", file=sys.stderr)
        return 1
    print(f"wrote entry.png ({len(payload)} bytes) to {written} location(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
