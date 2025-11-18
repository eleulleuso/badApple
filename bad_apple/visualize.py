#!/usr/bin/env python3
"""Simple text visualization for frames JSON."""
import json
import argparse


def render_frame(frame):
    # frame: 52 weeks of 7 days each
    # print 7 rows (days) and 52 columns (weeks)
    rows = ["" for _ in range(7)]
    for week in frame:
        for d, v in enumerate(week):
            rows[d] += "#" if v else " "
    return "\n".join(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--frame", type=int, default=0)
    args = parser.parse_args()

    import os, glob

    if not os.path.exists(args.data):
        base_name = os.path.basename(args.data)
        print(f"ERROR: File not found: {args.data}")
        matches = glob.glob(f"**/{base_name}", recursive=True)
        if matches:
            print("Found these matching files in your workspace:")
            for m in matches:
                print("  ", m)
        else:
            print("No matching files were found.")
        return

    with open(args.data) as f:
        data = json.load(f)

    frames = data.get("frames") or [data.get("weeks")]
    frame = frames[args.frame]
    print(render_frame(frame))


if __name__ == "__main__":
    main()
