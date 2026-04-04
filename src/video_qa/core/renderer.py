"""Image rendering for annotated frames and timeline comparisons."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from video_qa.core.clusterer import Region


def _get_font(size: int = 20) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Get a font, falling back to default if system fonts unavailable."""
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        try:
            return ImageFont.truetype("Arial.ttf", size)
        except OSError:
            return ImageFont.load_default()


def render_annotated_frame(
    frame_path: Path,
    annotation: str,
    output_path: Path,
) -> Path:
    """Render a frame with annotation text overlay."""
    img = Image.open(frame_path)
    draw = ImageDraw.Draw(img)
    font = _get_font(24)

    # Draw text with background for readability
    bbox = draw.textbbox((0, 0), annotation, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    padding = 8
    x, y = 10, 10

    draw.rectangle(
        [x, y, x + text_w + padding * 2, y + text_h + padding * 2],
        fill=(0, 0, 0, 180),
    )
    draw.text(
        (x + padding, y + padding),
        annotation,
        fill=(255, 255, 255),
        font=font,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    return output_path


def render_timeline(
    region: Region,
    output_path: Path,
    fps: int,
) -> Path:
    """Render a Before/Peak/After timeline comparison image."""
    labels = [
        (region.before_frame, "Before"),
        (region.peak_frame, "Peak (Bug)"),
        (region.after_frame, "After"),
    ]

    images: list[Image.Image] = []
    for frame_path, _ in labels:
        images.append(Image.open(frame_path).convert("RGB"))

    # Normalize heights
    max_h = max(img.height for img in images)
    resized: list[Image.Image] = []
    for img in images:
        if img.height != max_h:
            ratio = max_h / img.height
            new_w = int(img.width * ratio)
            resized.append(img.resize((new_w, max_h), Image.Resampling.LANCZOS))
        else:
            resized.append(img)

    # Layout: images side by side with labels
    gap = 4
    label_height = 40
    total_w = sum(img.width for img in resized) + gap * (len(resized) - 1)
    total_h = max_h + label_height

    canvas = Image.new("RGB", (total_w, total_h), (30, 30, 30))
    draw = ImageDraw.Draw(canvas)
    font = _get_font(18)

    x_offset = 0
    for i, (_, label) in enumerate(labels):
        img = resized[i]
        canvas.paste(img, (x_offset, label_height))

        # Draw label centered above image
        bbox = draw.textbbox((0, 0), label, font=font)
        text_w = bbox[2] - bbox[0]
        label_x = x_offset + (img.width - text_w) // 2
        draw.text(
            (label_x, 10),
            label,
            fill=(255, 255, 255),
            font=font,
        )

        x_offset += img.width + gap

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path)
    return output_path
