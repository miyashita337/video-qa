"""CLI entry point for video-qa."""

import tempfile
from pathlib import Path
from typing import Annotated

import typer

from video_qa._subprocess import check_dependencies
from video_qa.config import AnalysisConfig
from video_qa.core.clusterer import cluster_key_moments
from video_qa.core.comparator import compare_frames
from video_qa.core.extractor import extract_frames, get_video_metadata
from video_qa.core.renderer import render_timeline
from video_qa.exceptions import VideoQAError
from video_qa.reporters.markdown import generate_report

app = typer.Typer(
    name="video-qa",
    help="Auto-detect key moments in screen recordings.",
)


@app.command()
def analyze(
    video: Annotated[
        Path,
        typer.Argument(help="Path to the screen recording (.mp4)"),
    ],
    fps: Annotated[
        int,
        typer.Option(help="Frames per second for extraction (1-60)"),
    ] = 5,
    threshold: Annotated[
        float,
        typer.Option(help="RMSE threshold for change detection (0.0-1.0)"),
    ] = 0.05,
    cluster_window: Annotated[
        float,
        typer.Option(help="Time window in seconds to group nearby changes"),
    ] = 2.0,
    analyzer: Annotated[
        str,
        typer.Option(help="AI backend (none/claude/gemini)"),
    ] = "none",
    output_dir: Annotated[
        Path,
        typer.Option(help="Output directory for results"),
    ] = Path("./output"),
    output_format: Annotated[
        str,
        typer.Option(help="Report format (markdown/json)"),
    ] = "markdown",
) -> None:
    """Analyze a screen recording to detect key moments."""
    try:
        _run_pipeline(
            video,
            fps,
            threshold,
            cluster_window,
            analyzer,
            output_dir,
            output_format,
        )
    except VideoQAError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1) from e


def _run_pipeline(
    video: Path,
    fps: int,
    threshold: float,
    cluster_window: float,
    analyzer: str,
    output_dir: Path,
    output_format: str,
) -> None:
    """Run the full analysis pipeline."""
    # 1. Check dependencies
    typer.echo("Checking dependencies...")
    tools = check_dependencies()
    for name, info in tools.items():
        typer.echo(f"  {name}: {info}")

    # 2. Validate config
    config = AnalysisConfig(
        fps=fps,
        threshold=threshold,
        cluster_window=cluster_window,
        analyzer=analyzer,
        output_dir=output_dir,
        output_format=output_format,
    )

    # 3. Get video metadata
    typer.echo(f"\nAnalyzing: {video}")
    metadata = get_video_metadata(video)
    typer.echo(
        f"  {metadata.width}x{metadata.height}, "
        f"{metadata.duration:.1f}s, {metadata.fps:.1f}fps"
    )

    # 4. Extract frames
    with tempfile.TemporaryDirectory(prefix="video-qa-") as tmp:
        frames_dir = Path(tmp) / "frames"
        typer.echo(f"\nExtracting frames at {fps}fps...")
        frames = extract_frames(video, frames_dir, fps)
        typer.echo(f"  {len(frames)} frames extracted")

        # 5. Compare frames
        typer.echo("Comparing frames (RMSE)...")
        diffs = compare_frames(frames)
        above = sum(1 for d in diffs if d.rmse >= threshold)
        typer.echo(f"  {above}/{len(diffs)} frames above " f"threshold ({threshold})")

        # 6. Cluster key moments
        typer.echo("Clustering key moments...")
        regions = cluster_key_moments(
            diffs,
            threshold,
            cluster_window,
            fps,
            frames,
        )
        typer.echo(f"  {len(regions)} regions detected")

        # 7. Generate output
        output_dir.mkdir(parents=True, exist_ok=True)
        image_dir = output_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)

        # Render timeline images
        for i, region in enumerate(regions, 1):
            img_path = image_dir / f"region_{i:02d}.png"
            render_timeline(region, img_path, fps)
            typer.echo(f"  Timeline: {img_path}")

        # 8. Generate report
        if output_format == "markdown":
            report = generate_report(
                metadata,
                regions,
                config,
                image_dir,
            )
            report_path = output_dir / "report.md"
            report_path.write_text(report)
            typer.echo(f"\nReport: {report_path}")
        else:
            typer.echo("JSON format not yet supported.")

    # Summary
    typer.echo(f"\nDone! {len(regions)} regions detected.")


if __name__ == "__main__":
    app()
