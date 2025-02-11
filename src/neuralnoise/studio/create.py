import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Literal, Optional, Union

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
    script_segments = []
    temp_dir = output_dir / "segments"
    temp_dir.mkdir(exist_ok=True)

    sections_ids = sorted(script["sections"].keys())
    for section_id in sections_ids:
        for segment in script["sections"][section_id]["segments"]:
            script_segments.append((section_id, segment))

    audio_segments = []

    for section_id, segment in tqdm(script_segments, desc="Generating audio segments"):
        speaker = config.speakers[segment["speaker"]]
        content = segment["content"].replace("¡", "").replace("¿", "")
        content_hash = hashlib.md5(content.encode("utf-8")).hexdigest()
        segment_path = temp_dir / f"{section_id}_{segment['id']}_{content_hash}.mp3"
        audio_segment = generate_audio_segment(content, speaker, output_path=segment_path)
        audio_segments.append(audio_segment)
        if blank_duration := segment.get("blank_duration"):
            silence = AudioSegment.silent(duration=blank_duration * 1000)
            audio_segments.append(silence)

    podcast = AudioSegment.empty()
    for chunk in audio_segments:
        podcast += chunk

    podcast = normalize(podcast)
    return podcast

def create_podcast_episode(
    name: str,
    content: str,
    config: Optional[StudioConfig] = None,
    config_path: Optional[Union[str, Path]] = None,
    format: Literal["wav", "mp3", "ogg"] = "wav",
    only_script: bool = False,
) -> Optional[AudioSegment]:
    output_dir = Path("output") / name
    output_dir.mkdir(parents=True, exist_ok=True)

    if config is None:
        raise ValueError("No studio configuration provided")

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

    logger.info("🎙️  Recording podcast episode")
    podcast = create_podcast_episode_from_script(script, config, output_dir=output_dir)

    if podcast is None:
        return None

    podcast_filepath = output_dir / f"output.{format}"
    logger.info("️💾  Exporting podcast to %s", podcast_filepath)
    podcast.export(podcast_filepath, format=format)

    logger.info("✅  Podcast generation complete")
    return podcast