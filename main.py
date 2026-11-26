"""news-image-20261126 entry runner.

Copies the pre-rendered front-page image (entry.png, bundled next to this
file) to the grader's output location. Pure standard library, deterministic,
no network access: the output bytes are always identical to the bundled file.
"""

import os
import shutil
import sys

IMAGE_NAME = "entry.png"


def bundled_image_path():
    """Absolute path of the entry.png sitting beside this script."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, IMAGE_NAME)


def pick_output_dir():
    """Choose where the image goes, in priority order.

    1. $MAKEFUN_OUTPUT_DIR, when it names an existing directory.
    2. /output, when it exists.
    3. The current working directory.
    """
    env_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env_dir and os.path.isdir(env_dir):
        return env_dir
    if os.path.isdir("/output"):
        return "/output"
    return os.getcwd()


def main():
    source = bundled_image_path()
    if not os.path.isfile(source):
        print("error: bundled image not found: %s" % source, file=sys.stderr)
        return 1
    target_dir = pick_output_dir()
    os.makedirs(target_dir, exist_ok=True)
    target = os.path.join(target_dir, IMAGE_NAME)
    shutil.copyfile(source, target)
    # Integrity check: a truncated copy must never pass as a good run.
    if os.path.getsize(target) != os.path.getsize(source):
        print("error: copied image size mismatch: %s" % target, file=sys.stderr)
        return 1
    print("wrote %s" % target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
