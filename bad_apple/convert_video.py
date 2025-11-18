#!/usr/bin/env python3
"""
Extract frames from a video, downsample to 52x7 and save as pixel JSON for use with
`bad_apple/generate.py`.

This script uses imageio (ffmpeg backend) for reading video frames. Recommended to
install with `pip install imageio imageio-ffmpeg Pillow`.

Usage:
  python bad_apple/convert_video.py --input vidio/badapple.mp4 --output frames.json --fps 1 --max-frames 50
"""
import argparse
import json
import math
from PIL import Image
import imageio
import os
import glob


def pixel_from_frame(frame, threshold=128):
    im = Image.fromarray(frame)
    im_gray = im.convert("L")
    im_small = im_gray.resize((52, 7), Image.BICUBIC)
    # Build weeks (52) x days (7) structure
    weeks = []
    for col in range(52):
        week = []
        for row in range(7):
            # Value: 0 white, 255 black; thresholded into 0/1 where 1 is dark pixel
            val = im_small.getpixel((col, row))
            week.append(1 if val < threshold else 0)
        weeks.append(week)
    return weeks


def extract_frames(video_path, fps=1, max_frames=None):
    reader = imageio.get_reader(video_path)
    meta = reader.get_meta_data()
    video_fps = meta.get('fps', 30)
    step = max(1, int(round(video_fps / fps)))

    frames = []
    for i, frame in enumerate(reader):
        # sample frames according to step
        if (i % step) != 0:
            continue
        frames.append(frame)
        if max_frames and len(frames) >= max_frames:
            break

    reader.close()
    return frames


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', default='frames.json')
    parser.add_argument('--fps', type=float, default=1.0, help='Target frames per second to sample')
    parser.add_argument('--max-frames', type=int, default=600, help='Maximum number of frames to extract')
    parser.add_argument('--threshold', type=int, default=128, help='Threshold for black/white')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        base_name = os.path.basename(args.input)
        print(f"ERROR: Input file not found: {args.input}")
        # try to suggest similar files
        matches = glob.glob(f"**/{base_name}", recursive=True)
        if matches:
            print("Found these matching files in the repo:")
            for m in matches:
                print("  ", m)
        else:
            print("No matching files were found in the workspace. Check the path or move the file into the repository.")
        return

    print(f"Reading video {args.input} at target {args.fps} fps (max frames={args.max_frames})")
    raw_frames = extract_frames(args.input, fps=args.fps, max_frames=args.max_frames)
    print(f"Extracted {len(raw_frames)} frames")

    frames_pixels = []
    for i, f in enumerate(raw_frames):
        p = pixel_from_frame(f, threshold=args.threshold)
        frames_pixels.append(p)

    with open(args.output, 'w') as fh:
        json.dump({"frames": frames_pixels}, fh)

    print(f"Saved {len(frames_pixels)} frames to {args.output}")


if __name__ == '__main__':
    main()
