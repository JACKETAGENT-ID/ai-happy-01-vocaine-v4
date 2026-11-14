"""Vocaine entry for make.fun competition ai-happy-01.

Concept: a tiny mouse standing in a green leaf boat, baton raised,
conducting an orchestra of glowing fireflies above a sunflower
field at dusk.  Swirling amber light trails suggest the music.

Design note: the artwork ships inside this repository as
``image.png``.  This program is intentionally not an image
generator -- it is a careful validator and courier.  It checks
that the bundled picture really is a well-formed PNG inside the
competition limits, then copies it byte-for-byte to the output
directory.  Copying fixed bytes is what makes the entry fully
deterministic: run it twice, get identical output twice.
"""

from __future__ import annotations

import os
import struct
import sys
from pathlib import Path

# Competition limits for ai-happy-01.
MAX_FILE_BYTES = 1_048_576
MAX_SIDE_PX = 1024

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
HERE = Path(__file__).resolve().parent
SOURCE_IMAGE = HERE / "image.png"


class EntryError(RuntimeError):
    """Raised when the bundled artwork fails a pre-flight check."""


def read_ihdr_dimensions(blob: bytes) -> tuple[int, int]:
    """Return (width, height) parsed from the PNG IHDR chunk.

    The layout we rely on is fixed by the PNG specification:
    an 8-byte signature, then the first chunk, which must be
    IHDR -- 4 bytes of length, the literal b'IHDR', then the
    width and height as big-endian unsigned 32-bit integers.
    """
    if len(blob) < 33:
        raise EntryError("file is too short to contain a PNG IHDR chunk")
    if blob[:8] != PNG_SIGNATURE:
        raise EntryError("missing PNG magic bytes -- not a PNG file")
    if blob[12:16] != b"IHDR":
        raise EntryError("first PNG chunk is not IHDR")
    width, height = struct.unpack(">II", blob[16:24])
    return width, height


def check_chunk_walk(blob: bytes) -> None:
    """Walk the PNG chunk list as a light structural sanity check.

    No CRCs are verified here (hence 'CRC-free'); instead we make
    sure every chunk header is plausible, the walk lands exactly
    on the end of the file, and an IEND chunk closes the stream.
    A truncated or padded file fails this walk.
    """
    offset = 8  # skip the signature
    saw_iend = False
    while offset < len(blob):
        if offset + 8 > len(blob):
            raise EntryError("truncated chunk header during chunk walk")
        (length,) = struct.unpack(">I", blob[offset : offset + 4])
        kind = blob[offset + 4 : offset + 8]
        next_offset = offset + 8 + length + 4  # header + data + CRC
        if next_offset > len(blob):
            raise EntryError(f"chunk {kind!r} overruns the end of file")
        offset = next_offset
        if kind == b"IEND":
            saw_iend = True
            break
    if not saw_iend:
        raise EntryError("no IEND chunk found -- PNG stream is incomplete")
    if offset != len(blob):
        raise EntryError("unexpected trailing bytes after IEND chunk")


def validate_artwork(blob: bytes) -> tuple[int, int]:
    """Run every check the competition cares about. Returns (w, h)."""
    if not blob:
        raise EntryError("image.png is empty")
    if len(blob) > MAX_FILE_BYTES:
        raise EntryError(
            f"image.png is {len(blob)} bytes, over the {MAX_FILE_BYTES} limit"
        )
    width, height = read_ihdr_dimensions(blob)
    # IHDR bytes 24 and 25 hold bit depth and colour type.  We do
    # not need a specific combination, but both must be values the
    # PNG spec allows -- a cheap extra tripwire for corrupt files.
    if blob[24] not in (1, 2, 4, 8, 16) or blob[25] not in (0, 2, 3, 4, 6):
        raise EntryError("IHDR carries an impossible bit depth / colour type")
    if width == 0 or height == 0:
        raise EntryError("PNG reports a zero dimension")
    if width > MAX_SIDE_PX or height > MAX_SIDE_PX:
        raise EntryError(
            f"PNG is {width}x{height}, over the {MAX_SIDE_PX}px side limit"
        )
    check_chunk_walk(blob)
    return width, height


def main() -> int:
    if not SOURCE_IMAGE.is_file():
        print(f"error: bundled artwork not found at {SOURCE_IMAGE}", file=sys.stderr)
        return 1

    blob = SOURCE_IMAGE.read_bytes()
    try:
        width, height = validate_artwork(blob)
    except EntryError as exc:
        print(f"error: artwork failed validation: {exc}", file=sys.stderr)
        return 1

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        target = out_dir / "entry.png"
        target.write_bytes(blob)
        # Read the copy back and compare: determinism is the whole
        # point of this entry, so a short or altered write must be
        # reported rather than silently accepted.
        if target.read_bytes() != blob:
            print("error: output copy does not match image.png", file=sys.stderr)
            return 1
    except OSError as exc:
        print(f"error: could not write output: {exc}", file=sys.stderr)
        return 1

    print(f"vocaine ai-happy-01: wrote {target} ({len(blob)} bytes, {width}x{height})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
