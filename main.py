#!/usr/bin/env python3
"""Two Lines to Your Past Self -- writes the two-line warning to entry.txt.

The gate (sealed scorer): /output/entry.txt must be UTF-8 text of 1 to 280
characters, not only whitespace. The entry itself is exactly two lines:
line 1 warns the writer's past self about one specific moment in a single
sentence; line 2 says in one sentence why that moment mattered and what
changed because of it.
"""

import os

LINE_1 = (
    "On the night of 14 March, don't delete the voicemail from your father "
    "just because his voice sounds tired."
)
LINE_2 = (
    "It was the last recording of him, and every birthday since, you've "
    "dialled a number that no longer answers to hear nothing at all."
)

MAX_CHARS = 280


def resolve_output_dir():
    """Return the harness output dir, falling back to ./output."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or "./output"


def build_entry():
    """Return the two-line entry text (no trailing newline)."""
    return LINE_1 + "\n" + LINE_2


def validate(text):
    """Enforce the entry format exactly as the requirements state."""
    if not isinstance(text, str):
        raise ValueError("entry must be text")
    if not text.strip():
        raise ValueError("entry must not be empty or whitespace only")
    # UTF-8 round trip: the gate reads the file as UTF-8 text.
    text.encode("utf-8").decode("utf-8")
    if len(text) > MAX_CHARS:
        raise ValueError(
            "entry is %d characters, over the %d limit" % (len(text), MAX_CHARS)
        )
    lines = text.split("\n")
    if len(lines) != 2:
        raise ValueError("entry must be exactly two lines, got %d" % len(lines))
    for i, line in enumerate(lines, 1):
        if not line.strip():
            raise ValueError("line %d must not be empty" % i)
        if line != line.strip():
            raise ValueError("line %d must not have leading/trailing space" % i)
        # Exactly one sentence per line: one terminator, and it closes the line.
        terminators = sum(line.count(mark) for mark in (".", "!", "?"))
        if terminators != 1 or not line.endswith((".", "!", "?")):
            raise ValueError(
                "line %d must be exactly one sentence, got %d terminators"
                % (i, terminators)
            )
        if len(line) > MAX_CHARS:
            raise ValueError("line %d exceeds the character limit" % i)
    return True


def check_entry():
    """Validate the entry without writing anything; print a per-line report."""
    text = build_entry()
    validate(text)
    lines = text.split("\n")
    for i, line in enumerate(lines, 1):
        print("line %d: %d characters" % (i, len(line)))
    print("total: %d characters (limit %d), 2 lines, valid" % (len(text), MAX_CHARS))
    return 0


def main(argv=None):
    if argv and "--check" in argv:
        return check_entry()
    text = build_entry()
    validate(text)
    out_dir = resolve_output_dir()
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    # Determinism guard: render the file bytes twice and require equality,
    # so two grading runs can never disagree about the entry.
    payload = (text + "\n").encode("utf-8")
    if payload != (build_entry() + "\n").encode("utf-8"):
        raise ValueError("entry is not deterministic")
    with open(path, "wb") as f:
        f.write(payload)
    with open(path, "r", encoding="utf-8") as f:
        written = f.read()
    validate(written.rstrip("\n"))
    if len(written) > MAX_CHARS:
        raise ValueError("written file exceeds %d characters" % MAX_CHARS)
    lines = text.split("\n")
    print(
        "wrote %s (%d characters incl. trailing newline; "
        "line 1: %d, line 2: %d)" % (path, len(written), len(lines[0]), len(lines[1]))
    )
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv[1:]))
