from pydantic import BaseModel, Field


class VoiceSettings(BaseModel):
    stability: float = Field(..., ge=0.0, le=1.0)
    similarity_boost: float = Field(..., ge=0.0, le=1.0)
    style: float = Field(default=0.0, ge=0.0, le=1.0)
    speaker_boost: bool = Field(default=False)


class Speaker(BaseModel):
    name: str
    aliases: list[str]
    voice_id: str
    voice_settings: VoiceSettings


class MusicSettings(BaseModel):
    file_path: str
    fade_in: float = Field(default=2.0, ge=0.0)
    fade_out: float = Field(default=2.0, ge=0.0)
    duration: float = Field(default=10.0, ge=0.0)
    volume: float = Field(default=1.0, ge=0.0, le=1.0)


class Music(BaseModel):
    intro: MusicSettings
    outro: MusicSettings
    background: MusicSettings


class AppConfig(BaseModel):
    music: Music
    speakers: dict[str, Speaker]
