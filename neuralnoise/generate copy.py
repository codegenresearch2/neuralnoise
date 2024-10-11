import json
import logging
import os
from pathlib import Path
from typing import Any

from elevenlabs import Voice, VoiceSettings, save
from elevenlabs.client import ElevenLabs
from openai import OpenAI
from pydub import AudioSegment
from pydub.silence import split_on_silence

from neuralnoise.types import AppConfig


def load_prompt(prompt_name: str) -> str:
    prompt_path = Path("prompts") / f"{prompt_name}.xml"
    with open(prompt_path, "r") as f:
        return f.read()


def analyze_content(content: str) -> dict[str, Any]:
    client = OpenAI()
    analysis_prompt_system = load_prompt("content_analysis.system")
    analysis_prompt_user = load_prompt("content_analysis.user")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": analysis_prompt_system},
            {
                "role": "user",
                "content": analysis_prompt_user.format(content=content),
            },
        ],
        temperature=0.7,
        max_tokens=1000,
        response_format={"type": "json_object"},
    )

    if response.choices[0].message.content is None:
        raise ValueError("No content returned from analysis prompt")

    return json.loads(response.choices[0].message.content)


def generate_script(
    analysis: dict[str, Any], speakers: dict[str, Any]
) -> dict[str, Any]:
    client = OpenAI()

    script_prompt_system = load_prompt("script_generation.system")
    script_prompt_user = load_prompt("script_generation.user")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": script_prompt_system},
            {
                "role": "user",
                "content": script_prompt_user.format(
                    analysis=json.dumps(analysis, indent=2),
                    speakers=json.dumps(speakers, indent=2),
                ),
            },
        ],
        temperature=0.7,
        response_format={"type": "json_object"},
    )

    if response.choices[0].message.content is None:
        raise ValueError("No content returned from script generation prompt")

    return json.loads(response.choices[0].message.content)


def generate_audio_segments(
    script: dict[str, Any], config: AppConfig
) -> list[AudioSegment]:
    segments = []
    client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

    for segment in script["segments"]:
        voice_id = config.speakers[segment["speaker"]].voice_id
        voice_settings = config.speakers[segment["speaker"]].voice_settings

        audio = client.generate(
            text=segment["content"],
            model="eleven_multilingual_v2",
            voice=Voice(
                voice_id=voice_id,
                settings=VoiceSettings(
                    **voice_settings.model_dump(),
                ),
            ),
        )
        save(audio, "temp_segment.mp3")

        # Convert bytes to AudioSegment
        audio_segment = AudioSegment.from_mp3("temp_segment.mp3")

        # Split audio_segment in blanks to remove unnecessary silence
        audio_segment_chunks = split_on_silence(
            audio_segment, min_silence_len=500, keep_silence=100
        )

        audio_segment_without_silence = AudioSegment.empty()
        for chunk in audio_segment_chunks:
            audio_segment_without_silence += chunk

        segments.append(audio_segment_without_silence)

        if segment.get("pause"):
            silence = AudioSegment.silent(duration=segment["pause"] * 1000)
            segments.append(silence)

        os.remove("temp_segment.mp3")

    return segments


def create_podcast(segments: list[AudioSegment]) -> AudioSegment:
    podcast = AudioSegment.empty()

    for chunk in segments:
        podcast += chunk

    return podcast


# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def generate_podcast(
    content_file: str, config_file: str, output_file: str, only_script: bool = False
):
    # Create output directory if it doesn't exist
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # Load content
    logger.info("Loading content from %s", content_file)
    with open(content_file, "r") as f:
        content = f.read()

    # Load configuration
    logger.info("Loading configuration from %s", config_file)
    with open(config_file, "r") as f:
        config = AppConfig.model_validate_json(f.read())

    # Analyze content (with caching)
    analysis_cache = output_dir / f"{Path(content_file).stem}_analysis.json"
    if analysis_cache.exists():
        logger.info("Loading cached content analysis")
        with open(analysis_cache, "r", encoding="utf-8") as f:
            analysis = json.load(f)
    else:
        logger.info("Analyzing content")
        analysis = analyze_content(content)
        with open(analysis_cache, "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)

    # Generate script (with caching)
    script_cache = output_dir / f"{Path(content_file).stem}_script.json"
    if script_cache.exists():
        logger.info("Loading cached script")
        with open(script_cache, "r", encoding="utf-8") as f:
            script = json.load(f)
    else:
        logger.info("Generating script")
        config_dump = config.model_dump()
        script = generate_script(analysis, config_dump["speakers"])
        with open(script_cache, "w", encoding="utf-8") as f:
            json.dump(script, f, ensure_ascii=False, indent=2)

    if only_script:
        return

    # Generate audio segments
    logger.info("Generating audio segments")
    audio_segments = generate_audio_segments(script, config)

    # Create podcast
    logger.info("Creating podcast")
    podcast = create_podcast(audio_segments)

    # Export podcast
    logger.info("Exporting podcast to %s", output_file)
    podcast.export(output_file, format="mp3")

    logger.info("Podcast generation complete")
