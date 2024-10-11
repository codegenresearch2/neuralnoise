from typing import Literal

from pydantic import BaseModel, Field


class VoiceSettings(BaseModel):
    stability: float = Field(..., ge=0.0, le=1.0)
    similarity_boost: float = Field(..., ge=0.0, le=1.0)
    style: float = Field(default=0.0, ge=0.0, le=1.0)
    speaker_boost: bool = Field(default=False)


class SpeakerSettings(BaseModel):
    voice_id: str

    provider: Literal["elevenlabs", "openai"] = "elevenlabs"
    voice_model: Literal["eleven_multilingual_v2", "tts-1", "tts-1-hd"] = (
        "eleven_multilingual_v2"
    )
    voice_settings: VoiceSettings | None = None


class Speaker(BaseModel):
    name: str
    about: str

    settings: SpeakerSettings


class Show(BaseModel):
    name: str
    about: str
    language: str


class StudioConfig(BaseModel):
    show: Show
    speakers: dict[str, Speaker]

    def show_info(self) -> str:
        return (
            f"Show:\n\n\tName: {self.show.name}\n\tAbout: {self.show.about}"
            f"\n\tLanguage: {self.show.language}"
        )

    def speakers_info(self) -> str:
        return "\n".join(
            f"{speaker_id}:\n\n\tName: {self.speakers[speaker_id].name}"
            f"\n\tAbout: {self.speakers[speaker_id].about}"
            for speaker_id in self.speakers
        )
