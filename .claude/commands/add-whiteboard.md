The user wants to add a new whiteboard photo to the repo and process it.

Ask the user for the path to the whiteboard image file (or check if they provided it as an argument: $ARGUMENTS).

1. Copy the image into `whiteboards/`.
2. Run `python3 scripts/clean_whiteboards.py` to process all unprocessed whiteboards. The script only processes images that don't already have a corresponding `_cleaned.png` in `graphics/`, so previously processed images won't be re-run.
3. After processing, verify the cleaned output appeared in `graphics/`.
4. Commit all new files (the original whiteboard and the cleaned graphic) and push to GitHub.
