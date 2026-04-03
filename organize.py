#!/usr/bin/env python3
"""Organize loose movie files into 'Movie Name (Year)' folders.

Usage:
    python3 organize.py /path/to/Films [--apply]
    Without --apply, runs in dry-run mode (preview only).
"""

import os
import re
import sys

VIDEO_EXT = {".mkv", ".mp4", ".avi", ".m4v", ".wmv", ".flv", ".mov"}
SUB_EXT = {".srt", ".sub", ".ass", ".ssa", ".idx"}
YEAR_MIN, YEAR_MAX = 1920, 2030

# Release keywords that can appear before the year in some naming formats
NOISE_RE = re.compile(
    r"\b(MULTi|MULTI|VFF|VFQ|VFI|VF2|VOSTFR|VOSTF|FRENCH|TRUEFRENCH|FANSUB|REPACK)\b",
    re.IGNORECASE,
)


def clean_name(raw):
    """Clean extracted movie name: remove tags, brackets, dots."""
    # Remove bracketed content [1080p], [FR-EN], etc.
    raw = re.sub(r"\[.*?\]", "", raw)
    # Remove parenthetical content (alt titles, audio tags, etc.)
    raw = re.sub(r"\(.*?\)", "", raw)
    # Replace dots with spaces if the name is dot-separated
    if raw.count(".") >= raw.count(" "):
        raw = raw.replace(".", " ")
    # Strip release keywords
    raw = NOISE_RE.sub("", raw)
    # Collapse whitespace and trim junk
    return re.sub(r"\s+", " ", raw).strip(" -.")


def extract_folder_name(filename):
    """Return 'Movie Name (Year)' or just 'Movie Name' from a filename."""
    stem = os.path.splitext(filename)[0]

    # 1. Year in parentheses: "Title (YYYY) ..."
    m = re.search(r"^(.*?)\s*\((\d{4})\)", stem)
    if m and YEAR_MIN <= int(m.group(2)) <= YEAR_MAX:
        return f"{clean_name(m.group(1))} ({m.group(2)})"

    # 2. Year after a separator: "Title.YYYY." or "Title YYYY "
    m = re.search(r"[.\s\-](\d{4})(?=[.\s\-]|$)(?!p|i)", stem)
    if m and YEAR_MIN <= int(m.group(1)) <= YEAR_MAX:
        return f"{clean_name(stem[: m.start()])} ({m.group(1)})"

    # 3. Year glued to text: "RRRrrrr!!!2004"
    m = re.search(r"(\D)(\d{4})(?=[.\s\-]|$)(?!p|i)", stem)
    if m and YEAR_MIN <= int(m.group(2)) <= YEAR_MAX:
        return f"{clean_name(stem[: m.start() + 1])} ({m.group(2)})"

    # No year found — just clean the name
    return clean_name(stem)


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(f"Usage: {sys.argv[0]} /path/to/Films [--apply]")
        sys.exit(0)

    target = sys.argv[1]
    apply = "--apply" in sys.argv

    if not os.path.isdir(target):
        print(f"Error: {target} is not a directory")
        sys.exit(1)

    # Collect loose files at the root level only
    videos, subs = [], []
    for entry in os.listdir(target):
        if not os.path.isfile(os.path.join(target, entry)):
            continue
        ext = os.path.splitext(entry)[1].lower()
        if ext in VIDEO_EXT:
            videos.append(entry)
        elif ext in SUB_EXT:
            subs.append(entry)

    videos.sort()
    count = 0

    for video in videos:
        folder = extract_folder_name(video)
        dest = os.path.join(target, folder)

        print(f"[MOVE] {video}\n    -> {folder}/")

        if apply:
            os.makedirs(dest, exist_ok=True)
            os.rename(os.path.join(target, video), os.path.join(dest, video))

        # Move matching subtitles (same base name)
        base = os.path.splitext(video)[0]
        for sub in subs[:]:
            if sub.startswith(base):
                print(f"  [SUB] {sub} -> {folder}/")
                if apply:
                    os.rename(os.path.join(target, sub), os.path.join(dest, sub))
                subs.remove(sub)

        count += 1

    print(f"\n{count} movie(s) to organize.")
    if not apply:
        print("Dry run. Run with --apply to execute.")


if __name__ == "__main__":
    main()
