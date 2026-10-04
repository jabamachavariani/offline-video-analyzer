from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional

import cv2
import numpy as np
from PIL import Image


@dataclass
class VideoAnalysisResult:
    file: str
    duration_seconds: float
    fps: float
    width: int
    height: int
    frame_count: int
    average_brightness: float
    motion_score: float
    scene_change_count: int
    scene_changes: List[Dict[str, float]]
    keyframes: List[str]
    summary: str


class VideoAnalyzer:
    def __init__(self, video_path: str | Path, sample_every: int = 30, max_frames: int = 12):
        self.video_path = Path(video_path)
        self.sample_every = max(1, sample_every)
        self.max_frames = max(1, max_frames)

    def _to_rgb(self, bgr_frame: np.ndarray) -> np.ndarray:
        return cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)

    def _brightness(self, frame: np.ndarray) -> float:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return float(gray.mean())

    def _average_color(self, frame: np.ndarray) -> tuple[int, int, int]:
        rgb = self._to_rgb(frame)
        return tuple(int(value) for value in rgb.mean(axis=(0, 1)))

    def _motion_delta(self, prev_frame: np.ndarray, curr_frame: np.ndarray) -> float:
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(prev_gray, curr_gray)
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        return float(np.mean(thresh))

    def analyze(self, output_dir: Optional[str | Path] = None) -> VideoAnalysisResult:
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video not found: {self.video_path}")

        cap = cv2.VideoCapture(str(self.video_path))
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {self.video_path}")

        fps = float(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = 0.0 if total_frames == 0 or fps == 0 else total_frames / fps

        brightness_values: List[float] = []
        motion_values: List[float] = []
        scene_changes: List[Dict[str, float]] = []
        sample_frames: List[np.ndarray] = []
        avg_color_samples: List[tuple[int, int, int]] = []

        previous_frame: Optional[np.ndarray] = None
        frame_index = 0

        while True:
            ok, frame = cap.read()
            if not ok:
                break

            if frame_index % self.sample_every == 0:
                brightness_values.append(self._brightness(frame))
                avg_color_samples.append(self._average_color(frame))
                if len(sample_frames) < self.max_frames:
                    sample_frames.append(frame.copy())

            if previous_frame is not None:
                delta = self._motion_delta(previous_frame, frame)
                motion_values.append(delta)
                if delta > 30:
                    scene_changes.append({"frame": float(frame_index), "delta": float(delta)})

            previous_frame = frame
            frame_index += 1

        cap.release()

        average_brightness = float(np.mean(brightness_values)) if brightness_values else 0.0
        motion_score = float(np.mean(motion_values)) if motion_values else 0.0
        scene_change_count = len(scene_changes)

        output_path = Path(output_dir) if output_dir else self.video_path.parent / "analysis_output"
        output_path.mkdir(parents=True, exist_ok=True)

        keyframe_paths: List[str] = []
        for idx, frame in enumerate(sample_frames, start=1):
            keyframe_name = f"frame_{idx:04d}.jpg"
            keyframe_path = output_path / keyframe_name
            cv2.imwrite(str(keyframe_path), frame)
            keyframe_paths.append(str(keyframe_path))

        dominant_colors = []
        if avg_color_samples:
            for color in avg_color_samples[:5]:
                dominant_colors.append({"r": color[0], "g": color[1], "b": color[2]})

        summary = (
            f"Video contains {frame_index} frames at {fps:.2f} FPS. "
            f"Average brightness is {average_brightness:.2f}, motion score is {motion_score:.2f}, "
            f"and {scene_change_count} scene changes were detected."
        )

        result = VideoAnalysisResult(
            file=str(self.video_path),
            duration_seconds=float(duration),
            fps=float(fps),
            width=int(width),
            height=int(height),
            frame_count=int(frame_index),
            average_brightness=average_brightness,
            motion_score=motion_score,
            scene_change_count=scene_change_count,
            scene_changes=scene_changes[:25],
            keyframes=keyframe_paths,
            summary=summary,
        )

        return result

    def save_report(self, result: VideoAnalysisResult, output_path: str | Path) -> Path:
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8") as fh:
            json.dump(asdict(result), fh, indent=2)
        return target


def analyze_video(video_path: str | Path, output_dir: Optional[str | Path] = None, json_path: Optional[str | Path] = None) -> VideoAnalysisResult:
    analyzer = VideoAnalyzer(video_path)
    result = analyzer.analyze(output_dir=output_dir)
    if json_path:
        analyzer.save_report(result, json_path)
    return result
