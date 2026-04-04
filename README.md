# video-qa

Analyze screen recordings to auto-detect key moments, generate timeline comparisons, and create test reports — **no test code required**.

## What it does

1. Extracts frames from a screen recording at configurable FPS
2. Computes RMSE between adjacent frames to detect visual changes
3. Clusters nearby changes into "regions" (Before / Peak / After)
4. Generates timeline comparison images and a Markdown test report

## Prerequisites

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/) (includes ffprobe)
- [ImageMagick](https://imagemagick.org/) v6 or v7

```bash
# macOS
brew install ffmpeg imagemagick

# Ubuntu/Debian
apt install ffmpeg imagemagick

# Windows
choco install ffmpeg imagemagick
```

## Install

```bash
pip install video-qa
```

## Usage

```bash
# Basic analysis (5 fps, default threshold)
video-qa recording.mp4

# Higher frame rate for fast UI transitions
video-qa recording.mp4 --fps 30

# Custom threshold and output directory
video-qa recording.mp4 --threshold 0.1 --output-dir ./results

# All options
video-qa recording.mp4 \
  --fps 10 \
  --threshold 0.05 \
  --cluster-window 2.0 \
  --analyzer none \
  --output-dir ./output \
  --output-format markdown
```

## Output

```
output/
  report.md              # Markdown test report
  images/
    region_01.png         # Timeline comparison (Before/Peak/After)
    region_02.png
    ...
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--fps` | 5 | Frames per second for extraction (1-60) |
| `--threshold` | 0.05 | RMSE threshold for change detection (0.0-1.0) |
| `--cluster-window` | 2.0 | Time window (seconds) to group nearby changes |
| `--analyzer` | none | AI backend: `none`, `claude`, `gemini` |
| `--output-dir` | ./output | Output directory |
| `--output-format` | markdown | Report format: `markdown` |

## How it works

```
[Input] Screen recording (.mp4)
    |
    v
 ffprobe -> video metadata (resolution, fps, duration)
    |
    v
 ffmpeg -> frame extraction at configured FPS
    |
    v
 ImageMagick compare -> RMSE between adjacent frames
    |
    v
 Clustering -> group changes within time window
    |
    v
 Pillow -> timeline comparison images (Before/Peak/After)
    |
    v
[Output] Markdown report + images
```

## License

MIT
