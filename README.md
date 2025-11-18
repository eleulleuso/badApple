# played-on-GitHub

Bad Apple on the GitHub contribution graph 🎮🕹️

This repository contains tools to convert image/GIF frames into 52x7 (weeks x days)
pixel data and then generate historical commits to draw patterns on the GitHub contribution
graph.

IMPORTANT: This manipulates commit dates. Only run this in a new repository. Do not
use on repositories with important commit history.

## Quick start

1. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

2. Convert a GIF into frames (52x7 arrays):

```bash
python bad_apple/convert_gif.py --input my_bad_apple.gif --output frames.json --threshold 128
```

Or convert from video (MP4) using ffmpeg backend via imageio:

```bash
python bad_apple/convert_video.py --input vidio/badapple.mp4 --output frames.json --fps 1 --max-frames 300

If your video file is in a different folder (e.g., `source/vidio/badapple.mp4`), pass the full relative path:

```bash
python bad_apple/convert_video.py --input source/vidio/badapple.mp4 --output frames.json --fps 1
```
```

3. Dry-run generation to see what commits would be made:

```bash
python bad_apple/generate.py --data frames.json --start-date 2023-12-31 --intensity 5 --dry-run
```

4. Generate commits and push to GitHub (again, only in a dedicated empty repo):

```bash
python bad_apple/generate.py --data frames.json --start-date 2023-12-31 --intensity 5
git remote add origin <url>
git push -u origin main --force
```

## Notes & design choices

- `convert_gif.py` resizes frames to 52x7 and thresholds them into 0/1 pixels. The output
	format is a JSON containing `frames: [frame0, frame1, ...]` where each frame is 52 lists of 7 numbers.
- `generate.py` creates one empty commit per pixel intensity specified for each pixel that is `1` in the JSON.
- `convert_video.py` extracts frames from a video using `imageio` and converts them to 52x7 arrays.
- You can generate many frames, but note that spacing multiple frames across time will cause the timeline to
	cover a very large span of dates. See `--frame-spacing-weeks` for control.

## Visualize frames (quick preview)

You can preview the generated JSON with a small ASCII preview:

```bash
python bad_apple/visualize.py --data frames.json --frame 0
```

This prints `#` for darker pixels and spaces for blank pixels. Useful to check before generating commits.

## Choosing a start date

Pick a Sunday as the start of the 52 x 7 canvas. You can get the nearest past Sunday in Python:

```bash
python - <<'PY'
from datetime import datetime, timedelta
today = datetime.now()
last_sunday = today - timedelta(days=(today.weekday() + 1) % 7)
print(last_sunday.strftime('%Y-%m-%d'))
PY
```


## Safety

This repo is an educational toy. Manipulating commit timestamps can be surprising to collaborators
and may be confusing in real projects. Use responsibly.

# played-on-GitHub-
# badApple
