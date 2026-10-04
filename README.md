# Offline Video Analyzer

A lightweight Python project for analyzing local video files entirely offline. It extracts basic video metadata, measures scene motion, detects scene changes, and saves keyframes without relying on cloud APIs or internet access.

## Features

- Read local video files from disk
- Extract metadata: duration, FPS, resolution, frame count
- Measure brightness and motion intensity
- Detect scene-change candidates from frame-to-frame differences
- Save representative keyframes as JPEGs
- Export JSON analysis reports
- Works offline with local Python dependencies only

## Project layout

- `app.py` - easy entry point for running analysis from the command line
- `src/video_analyzer/analyzer.py` - core video analysis logic
- `src/video_analyzer/cli.py` - command-line wrapper

## Quick start

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # on macOS/Linux
   # or .venv\Scripts\activate  # on Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run analysis on a local video file:

   ```bash
   python app.py /path/to/video.mp4 --output ./analysis.json --keyframes ./keyframes
   ```

## Example output

```json
{
  "file": "/path/to/video.mp4",
  "duration_seconds": 120.4,
  "fps": 24.0,
  "width": 1920,
  "height": 1080,
  "frame_count": 2890,
  "average_brightness": 129.7,
  "motion_score": 38.2,
  "scene_change_count": 9,
  "scene_changes": [
    {"frame": 210, "delta": 36.5},
    {"frame": 874, "delta": 48.1}
  ],
  "keyframes": [
    "./keyframes/frame_0001.jpg",
    "./keyframes/frame_0020.jpg"
  ]
}
```

## Notes

This starter version is designed for offline analysis and local experimentation. It is intentionally dependency-light and uses OpenCV for frame processing, so it can run in a local environment without internet access.

## Next upgrades

- object detection with local models
- face detection and tracking
- subtitle extraction
- audio waveform and speech activity analysis
- GUI app for drag-and-drop video inspection
- export to CSV/HTML reports

