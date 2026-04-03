#!/bin/bash
# Organize loose movie files into individual folders.
# Usage: ./organize.sh /path/to/Films [--apply]
# Without --apply, runs in dry-run mode (preview only).

set -euo pipefail

TARGET_DIR="${1:?Usage: $0 /path/to/Films [--apply]}"
DRY_RUN=true

if [[ "${2:-}" == "--apply" ]]; then
    DRY_RUN=false
fi

if [[ ! -d "$TARGET_DIR" ]]; then
    echo "Error: $TARGET_DIR is not a directory"
    exit 1
fi

VIDEO_EXT="mkv|mp4|avi|m4v|wmv|flv|mov"
SUB_EXT="srt|sub|ass|ssa|idx"
COUNT=0

# Move loose video files into folders
find "$TARGET_DIR" -maxdepth 1 -type f -regextype posix-extended \
    -iregex ".*\.($VIDEO_EXT)$" | sort | while read -r file; do
    filename=$(basename "$file")
    folder_name="${filename%.*}"
    dest_dir="$TARGET_DIR/$folder_name"

    echo "[MOVE] $filename -> $folder_name/"

    if [[ "$DRY_RUN" == false ]]; then
        mkdir -p "$dest_dir"
        mv "$file" "$dest_dir/"
    fi

    # Find matching subtitle files (e.g. Movie.fr.srt, Movie.en.srt)
    base_name="${filename%.*}"
    find "$TARGET_DIR" -maxdepth 1 -type f -regextype posix-extended \
        -iregex ".*\.($SUB_EXT)$" -name "$base_name*" | while read -r sub; do
        sub_name=$(basename "$sub")
        echo "  [SUB] $sub_name -> $folder_name/"
        if [[ "$DRY_RUN" == false ]]; then
            mv "$sub" "$dest_dir/"
        fi
    done

    COUNT=$((COUNT + 1))
done

if [[ "$DRY_RUN" == true ]]; then
    echo ""
    echo "Dry run complete. Run with --apply to execute."
fi
