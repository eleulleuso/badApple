#!/usr/bin/env python3
"""Analyze frames JSON to produce helpful statistics for commit generation."""
import json
import argparse


def analyze(data):
    frames = data.get("frames") or [data.get("weeks")]
    totals = []
    for i, frame in enumerate(frames):
        count = sum(sum(week) for week in frame)
        totals.append(count)

    all_counts = totals
    n_frames = len(frames)
    avg = sum(all_counts) / n_frames if n_frames else 0
    return {
        "n_frames": n_frames,
        "min": min(all_counts) if all_counts else 0,
        "max": max(all_counts) if all_counts else 0,
        "avg": avg,
        "total_pixels": sum(all_counts)
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', required=True)
    args = parser.parse_args()
    with open(args.data) as fh:
        data = json.load(fh)
    stats = analyze(data)
    print("Frames:", stats["n_frames"]) 
    print("Pixels per frame - min:", stats["min"], "avg:", stats["avg"], "max:", stats["max"]) 
    print("Total colored pixels:", stats["total_pixels"]) 
    # If every frame is full 52*7 = 364
    print("Max per frame (full):", 52 * 7)


if __name__ == '__main__':
    main()
