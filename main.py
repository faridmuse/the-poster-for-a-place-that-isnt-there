"""Entry point for the-poster-for-a-place-that-i-2-20261121-0539.

Writes the travel poster for VELMARA, a place that isn't there, to
/output/entry.png (1024x1024 PNG, well under the 1 MiB cap).

The poster is drawn by draw-poster.py (PIL, run while building the
entry) and stored beside this file as entry.png; this program copies it
to the output directory with the standard library only, so it runs in
the grader's sandbox with no network and no third-party packages.

The output directory is MAKEFUN_OUTPUT_DIR when set, else /output.
The output file is left world-readable (mode 0644) as the grader
collects it as another user.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
IMAGE = os.path.join(HERE, "entry.png")


def main() -> None:
    if not os.path.isfile(IMAGE):
        print("entry.png missing beside main.py (%s)" % IMAGE, file=sys.stderr)
        print("Rebuild it with: python3 draw-poster.py", file=sys.stderr)
        sys.exit(1)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    try:
        os.chmod(out_dir, 0o755)
    except OSError:
        pass
    out_path = os.path.join(out_dir, "entry.png")
    shutil.copyfile(IMAGE, out_path)
    os.chmod(out_path, 0o644)
    print("wrote %s (%d bytes)" % (out_path, os.path.getsize(out_path)))


if __name__ == "__main__":
    main()
