import os
import time
from pathlib import Path
from typing import Iterator

from elevenlabs import Voice, VoiceSettings, save
from elevenlabs.client import ElevenLabs
from openai import OpenAI
from pydub import AudioSegment

from neuralnoise.types import Speaker


def generate_audio_segment_elevenlabs(
    content: str,
    speaker: Speaker,
) -> bytes | Iterator[bytes]:
    client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

    voice_id = speaker.settings.voice_id
    voice_settings = (
        speaker.settings.voice_settings.model_dump()
        if speaker.settings.voice_settings is not None
        else {}
    )

    audio = client.generate(
        text=content,
        model=speaker.settings.voice_model,
        voice=Voice(
            voice_id=voice_id,
            settings=VoiceSettings(
                **voice_settings,
            ),
        ),
    )

    return audio


def generate_audio_segment_openai(
    content: str,
    speaker: Speaker,
) -> bytes | Iterator[bytes]:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    audio = client.audio.speech.create(
        model=speaker.settings.voice_model,
        voice=speaker.settings.voice_id,  # type: ignore
        input=content,
    )

    time.sleep(1)

    return audio.content


TTS_PROVIDERS = {
    "elevenlabs": generate_audio_segment_elevenlabs,
    "openai": generate_audio_segment_openai,
}


def generate_audio_segment(
    content: str,
    speaker: Speaker,
    output_path: Path,
    overwrite: bool = False,
) -> AudioSegment:
    if not output_path.exists() or overwrite:
        print(f"Generating {output_path} with content: {content[:80]}...")
        tts_function = TTS_PROVIDERS[speaker.settings.provider]
        audio = tts_function(content, speaker)

        save(audio, str(output_path))

    audio_segment = AudioSegment.from_mp3(str(output_path))
    return audio_segment
