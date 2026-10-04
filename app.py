#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from video_analyzer.analyzer import analyze_video


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze local videos offline.")
    parser.add_argument("video_path", help="Path to the video file to analyze")
    parser.add_argument("--output", default="analysis_report.json", help="Path to save the JSON report")
    parser.add_argument("--keyframes", default="keyframes", help="Directory to save extracted keyframes")
    parser.add_argument("--sample-every", type=int, default=30, help="Sample every Nth frame for brightness analysis")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    video_path = Path(args.video_path)
    output_path = Path(args.output)
    keyframe_dir = Path(args.keyframes)

    result = analyze_video(video_path, output_dir=keyframe_dir, json_path=output_path)
    print(result.summary)
    print(f"JSON report saved to: {output_path}")
    print(f"Keyframes saved in: {keyframe_dir}")


if __name__ == "__main__":
    main()
