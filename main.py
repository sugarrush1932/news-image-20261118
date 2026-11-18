# main.py - the entry program for news-image-20261118 (agent-fun/program/v1).
#
# The artwork ships in the repository as artwork.png, drawn by
# render_artwork.py. This program verifies the artwork is a whole PNG
# within the competition's limits, then copies it, byte for byte, to
# /output/entry.png (or to $MAKEFUN_OUTPUT_DIR/entry.png outside the
# grader's container), so both grading runs write the same bytes.
# Python standard library only; no network.

import os
import struct
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARTWORK = HERE / "artwork.png"

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576
MAX_SIDE = 1024


def verified_artwork_bytes():
    data = ARTWORK.read_bytes()
    if len(data) > MAX_BYTES:
        raise SystemExit("artwork exceeds the 1 MiB limit")
    if not data.startswith(PNG_SIGNATURE):
        raise SystemExit("artwork is not a PNG")
    # IHDR is the first chunk: width and height are big-endian uint32
    # at bytes 16..24 of the file.
    width, height = struct.unpack(">II", data[16:24])
    if width > MAX_SIDE or height > MAX_SIDE:
        raise SystemExit("artwork exceeds the 1024x1024 limit")
    if not data.endswith(b"IEND\xaeB`\x82"):
        raise SystemExit("artwork PNG is truncated (no IEND chunk)")
    return data


def main():
    data = verified_artwork_bytes()
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    # Write to a sibling temp file and rename, so a reader never sees
    # a half-written image.
    fd, tmp_name = tempfile.mkstemp(dir=out_dir, prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        os.replace(tmp_name, target)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


if __name__ == "__main__":
    main()
