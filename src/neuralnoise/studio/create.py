import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from pydub import AudioSegment
from pydub.effects import normalize
from rich.progress import Progress

from neuralnoise.studio import PodcastStudio
from neuralnoise.tts import generate_audio_segment
from neuralnoise.types import StudioConfig

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_podcast_episode_from_script(
    script: dict[str, Any], config: StudioConfig, output_dir: Path
) -> AudioSegment:
    script_segments = []

    temp_dir = output_dir / "segments"
    temp_dir.mkdir(exist_ok=True)

    sections_ids = list(sorted(script["sections"].keys()))
    script_segments = [
        (section_id, segment)
        for section_id in sections_ids
        for segment in script["sections"][section_id]["segments"]
    ]

    with Progress() as progress:
        task = progress.add_task(
            "[cyan]Generating audio segments...", total=len(script_segments)
        )
        audio_segments = []

        for section_id, segment in script_segments:
            speaker = config.speakers[segment["speaker"]]
            content = segment["content"]

            content = content.replace("¡", "").replace("¿", "")

            content_hash = hashlib.md5(content.encode("utf-8")).hexdigest()
            segment_path = temp_dir / f"{section_id}_{segment['id']}_{content_hash}.mp3"

            audio_segment = generate_audio_segment(
                content, speaker, output_path=segment_path
            )

            audio_segments.append(audio_segment)

            if blank_duration := segment.get("blank_duration"):
                silence = AudioSegment.silent(duration=blank_duration * 1000)
                audio_segments.append(silence)

            progress.update(task, advance=1)

    podcast = AudioSegment.empty()

    for chunk in audio_segments:
        podcast += chunk

    podcast = normalize(podcast)

    return podcast


def create_podcast_episode(
    name: str,
    content: str,
    config_file: str | Path,
    only_script: bool = False,
):
    # Create output directory
    output_dir = Path("output") / name
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load configuration
    logger.info("🔧  Loading configuration from %s", config_file)
    with open(config_file, "r") as f:
        config = StudioConfig.model_validate_json(f.read())

    # Generate the script
    script_cache_filepath = output_dir / f"{name}_script.json"
    if script_cache_filepath.exists():
        logger.info("💬  Loading cached script")
        with open(script_cache_filepath, "r", encoding="utf-8") as f:
            script = json.load(f)
    else:
        logger.info("💬  Generating podcast script")
        studio = PodcastStudio(name, config=config)
        script = studio.generate_script(content)
        with open(script_cache_filepath, "w", encoding="utf-8") as f:
            json.dump(script, f, ensure_ascii=False, indent=2)

    if only_script:
        return

    # Generate audio segments and create the podcast
    logger.info("🎙️  Recording podcast episode")
    podcast = create_podcast_episode_from_script(script, config, output_dir=output_dir)

    # Export podcast
    podcast_filepath = output_dir / f"{name}.wav"
    logger.info("️💾  Exporting podcast to %s", podcast_filepath)
    podcast.export(podcast_filepath, format="wav")

    logger.info("✅  Podcast generation complete")
