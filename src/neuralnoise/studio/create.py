import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Literal, Optional

from pydub import AudioSegment
from pydub.effects import normalize
from tqdm import tqdm

from neuralnoise.studio import PodcastStudio
from neuralnoise.tts import generate_audio_segment
from neuralnoise.types import StudioConfig


logger = logging.getLogger(__name__)


def create_podcast_episode_from_script(
    script: dict[str, Any], config: StudioConfig, output_dir: Path
) -> AudioSegment:
    # Create a temporary directory to store audio segments
    temp_dir = output_dir / "segments"
    temp_dir.mkdir(exist_ok=True)

    # Initialize the list of script segments
    script_segments = [
        (section_id, segment)
        for section_id in sorted(script["sections"].keys())
        for segment in script["sections"][section_id]["segments"]
    ]

    audio_segments = []

    # Generate audio segments using tqdm for progress tracking
    for section_id, segment in tqdm(script_segments, desc="Generating audio segments"):
        speaker = config.speakers[segment["speaker"]]
        content = segment["content"].replace("¡", "").replace("¿", "")

        # Generate a unique filename for each segment
        content_hash = hashlib.md5(content.encode("utf-8")).hexdigest()
        segment_path = temp_dir / f"{section_id}_{segment['id']}_{content_hash}.mp3"

        # Generate the audio segment
        audio_segment = generate_audio_segment(content, speaker, output_path=segment_path)
        audio_segments.append(audio_segment)

        # Add silence if there is a blank duration
        if blank_duration := segment.get("blank_duration"):
            silence = AudioSegment.silent(duration=blank_duration * 1000)
            audio_segments.append(silence)

    # Combine all audio segments into a single podcast
    podcast = AudioSegment.empty()
    for chunk in audio_segments:
        podcast += chunk

    # Normalize the podcast audio
    podcast = normalize(podcast)
    return podcast


def create_podcast_episode(
    name: str,
    content: str,
    config: StudioConfig | None = None,
    config_path: str | Path | None = None,
    format: Literal["wav", "mp3", "ogg"] = "wav",
    only_script: bool = False,
) -> Optional[AudioSegment]:
    # Create the output directory for the podcast
    output_dir = Path("output") / name
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load the studio configuration
    if config_path:
        logger.info("🔧  Loading configuration from %s", config_path)
        with open(config_path, "r") as f:
            config = StudioConfig.model_validate_json(f.read())

    if not config:
        raise ValueError("No studio configuration provided")

    # Generate the podcast script if it doesn't exist
    script_path = output_dir / "script.json"
    if script_path.exists():
        logger.info("💬  Loading cached script")
        script = json.loads(script_path.read_text())
    else:
        logger.info("💬  Generating podcast script")
        studio = PodcastStudio(work_dir=output_dir, config=config)
        script = studio.generate_script(content)
        script_path.write_text(json.dumps(script, ensure_ascii=False))

    if only_script:
        return None

    # Generate the podcast audio
    logger.info("🎙️  Recording podcast episode")
    try:
        podcast = create_podcast_episode_from_script(script, config, output_dir=output_dir)
    except Exception as e:
        logger.error(f"Error creating podcast episode: {e}")
        return None

    # Export the podcast audio
    podcast_filepath = output_dir / f"output.{format}"
    logger.info("️💾  Exporting podcast to %s", podcast_filepath)
    podcast.export(podcast_filepath, format=format)

    logger.info("✅  Podcast generation complete")

    return podcast