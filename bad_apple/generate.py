#!/usr/bin/env python3
"""
Generate historical commits to draw a 52x7 pixel pattern on the GitHub Contribution graph.

Important notes:
- Run this in a NEW repository (do not run on a repo with important history).
- This script will create empty commits with manipulated `GIT_AUTHOR_DATE` and
  `GIT_COMMITTER_DATE` environment variables.

Modes:
- Single frame: supply a JSON with `weeks` (52 items each with 7 ints)
- Many frames: supply `frames` key. By default frames will be laid out sequentially
  in time by offsetting the date by `frame_spacing_weeks` weeks between frames.

Example usage:
  python bad_apple/generate.py --data frames/sample_frame.json --start-date 2023-12-31 --intensity 5 --dry-run

"""
import argparse
import json
import os
import subprocess
from datetime import datetime, timedelta


def load_data(path):
    with open(path, "r") as f:
        data = json.load(f)
    # support both single frame (weeks) and multiple frames
    if "frames" in data:
        return data["frames"]
    if "weeks" in data:
        return [data["weeks"]]
    raise ValueError("JSON must contain either 'frames' or 'weeks'")


def iso_date_str(dt):
    # use a standard time for the commit to avoid timezone issues
    return dt.strftime("%Y-%m-%d 12:00:00")


def create_commit_for_date(target_date, intensity, dry_run=False, message="BadApple Pixel"):
    commit_date = iso_date_str(target_date)
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = commit_date
    env["GIT_COMMITTER_DATE"] = commit_date

    for i in range(intensity):
        command = ["git", "commit", "--allow-empty", "-m", f"{message} {i+1}/{intensity}"]
        if dry_run:
            print(f"DRY-RUN: would run commit on {commit_date}: {command}")
        else:
            subprocess.run(command, check=True, env=env)


def generate_commits(frames, start_date, intensity, frame_spacing_weeks=1, dry_run=False, frame_spacing_days=None):
    # frames: list of 52x7 (weeks x days) arrays
    base = start_date
    for f_idx, weeks in enumerate(frames):
        if len(weeks) != 52:
            raise ValueError("Each frame must contain 52 weeks of 7-day arrays")
        print(f"Generating frame {f_idx + 1}/{len(frames)}")
        # compute offset for this frame (if multiple frames)
        if frame_spacing_days is not None:
            frame_offset = timedelta(days=f_idx * frame_spacing_days)
        else:
            frame_offset = timedelta(weeks=f_idx * frame_spacing_weeks)

        for week_index, week_data in enumerate(weeks):
            if len(week_data) != 7:
                raise ValueError("Week data must contain exactly 7 day values")

            for day_index, should_commit in enumerate(week_data):
                if should_commit:
                    # target date: base + (frame_offset * 7 weeks) + week_index weeks + day_index days
                    target_date = base + frame_offset + timedelta(weeks=week_index, days=day_index)
                    create_commit_for_date(target_date, intensity=intensity, dry_run=dry_run,
                                           message=f"BadApple F{f_idx+1} W{week_index+1} D{day_index+1}")


def compute_date_range(frames, base, frame_spacing_weeks=1, frame_spacing_days=None):
    # returns (min_date, max_date) across all '1' pixels in frames
    min_date = None
    max_date = None
    for f_idx, weeks in enumerate(frames):
        if frame_spacing_days is not None:
            frame_offset = timedelta(days=f_idx * frame_spacing_days)
        else:
            frame_offset = timedelta(weeks=f_idx * frame_spacing_weeks)

        for week_index, week_data in enumerate(weeks):
            for day_index, should_commit in enumerate(week_data):
                if should_commit:
                    target_date = base + frame_offset + timedelta(weeks=week_index, days=day_index)
                    if min_date is None or target_date < min_date:
                        min_date = target_date
                    if max_date is None or target_date > max_date:
                        max_date = target_date
    return (min_date, max_date)


def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="JSON file with 'frames' or 'weeks'")
    parser.add_argument("--start-date", default=None, help="Anchor start date (Sunday) - format YYYY-MM-DD")
    parser.add_argument("--intensity", type=int, default=10, help="Number of commits per pixel to affect color intensity")
    parser.add_argument("--frame-spacing-weeks", type=int, default=1, help="Spacing between frames (in weeks)")
    parser.add_argument("--frame-spacing-days", type=int, default=None, help="Spacing between frames in days (overrides weeks when set)")
    parser.add_argument("--start-frame", type=int, default=0, help="Index of first frame to generate (0-based)")
    parser.add_argument("--end-frame", type=int, default=None, help="Index of last frame to generate (exclusive)")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually run git, just print")
    parser.add_argument("--push", action="store_true", help="After generation, push to remote 'origin main' (use with care)")

    args = parser.parse_args()

    frames = load_data(args.data)

    if args.start_date:
        start_date = parse_date(args.start_date)
    else:
        # Use last Sunday as a default starting point
        today = datetime.now()
        start_date = today - timedelta(days=today.weekday() + 1)  # naive Sunday

    # Safety checks
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], check=True, stdout=subprocess.DEVNULL)
    except Exception:
        print("ERROR: Not inside a git repository. Please run `git init` first.")
        return

    # warn if repo already has commits
    try:
        proc = subprocess.run(["git", "rev-list", "--count", "HEAD"], check=True, capture_output=True, text=True)
        commits = int(proc.stdout.strip())
    except Exception:
        commits = 0

    if commits > 0:
        print(f"WARNING: repository already has {commits} commits. It's recommended to use a fresh repo.")

    # slice frames
    if args.end_frame is None:
        frames_to_use = frames[args.start_frame:]
    else:
        frames_to_use = frames[args.start_frame:args.end_frame]

    # Show date range for planned commits
    min_date, max_date = compute_date_range(frames_to_use, start_date, args.frame_spacing_weeks, args.frame_spacing_days)
    if min_date and max_date:
        print(f"Planned commit date range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
    else:
        print("Planned commit date range: (no commits, maybe empty frame data)")

    generate_commits(frames_to_use, start_date, args.intensity, args.frame_spacing_weeks, args.dry_run, frame_spacing_days=args.frame_spacing_days)

    if args.push and not args.dry_run:
        print("Pushing commits to origin main (please ensure your remote is set and you're OK with force push)")
        subprocess.run(["git", "push", "-u", "origin", "main", "--force"]) 


if __name__ == "__main__":
    main()
