Process all whiteboard images in the `whiteboards/` folder using the `scripts/clean_whiteboards.py` script.

Run the script with `python3 scripts/clean_whiteboards.py`. It will pick up the FAL_API_KEY from the environment or from `~/.config/nano-whiteboard-doctor/config.json`.

After processing completes, verify the output images were saved to `graphics/`. Report how many were processed and if any failed.

Then commit all new files (whiteboards and graphics) and push to GitHub.
