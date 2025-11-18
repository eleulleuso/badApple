#!/usr/bin/env python3
"""
Convert a GIF (or other multi-frame image) into frames resized to 52x7 and
save as JSON. Each frame is a 52x7 (weeks x days) array of 0/1.

Usage:
  python bad_apple/convert_gif.py --input badapple.gif --output frames.json --threshold 128
"""
import argparse
import json
from PIL import Image, ImageSequence


def frame_to_52x7(im, threshold=128):
    # normalize to 52 x 7
    im_gray = im.convert("L")
    im_small = im_gray.resize((52, 7), Image.NEAREST)
    pixels = list(im_small.getdata())
    # produce rows 7 and columns 52
    data = []
    for col in range(52):
        week = []
        for row in range(7):
            # note Image.getdata returns row-major; but we want (week,day)
            # so pick pixel at (col,row)
            val = im_small.getpixel((col, row))
            week.append(1 if val < threshold else 0)
        data.append(week)
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to GIF or multi-frame image")
    parser.add_argument("--output", default="frames.json", help="Output JSON filename")
    parser.add_argument("--threshold", type=int, default=128, help="Threshold for black/white")

    args = parser.parse_args()

    im = Image.open(args.input)
    frames = []
    for i, frame in enumerate(ImageSequence.Iterator(im)):
        data = frame_to_52x7(frame, threshold=args.threshold)
        frames.append(data)

    with open(args.output, "w") as f:
        json.dump({"frames": frames}, f)

    print(f"Saved {len(frames)} frames to {args.output}")


if __name__ == "__main__":
    main()
