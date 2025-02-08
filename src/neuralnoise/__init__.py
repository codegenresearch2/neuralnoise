from neuralnoise.extract import extract_content
import asyncio
from neuralnoise.studio import create_podcast_episode

__all__ = ["create_podcast_episode", "extract_content"]

async def async_create_podcast_episode(name: str,
                                     content: str,
                                     config: StudioConfig | None = None,
                                     config_path: str | Path | None = None,
                                     format: Literal['wav', 'mp3', 'ogg'] = 'wav',
                                     only_script: bool = False) -> AudioSegment | None:
    # Create output directory
    output_dir = Path('output') / name
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load configuration
    if config_path:
        logger.info('🔧  Loading configuration from %s', config_path)
        with open(config_path, 'r') as f:
            config = StudioConfig.model_validate_json(f.read())

    if not config:
        raise ValueError('No studio configuration provided')

    # Generate the script
    script_path = output_dir / 'script.json'

    if script_path.exists():
        logger.info('💬  Loading cached script')
        script = json.loads(script_path.read_text())
    else:
        logger.info('💬  Generating podcast script')
        studio = PodcastStudio(work_dir=output_dir, config=config)
        script = studio.generate_script(content)

        script_path.write_text(json.dumps(script, ensure_ascii=False))

    if only_script:
        return None

    # Generate audio segments and create the podcast
    logger.info('🎙️  Recording podcast episode')
    podcast = await create_podcast_episode_from_script(script, config, output_dir=output_dir)

    # Export podcast
    podcast_filepath = output_dir / f'output.{format}'
    logger.info('️💾  Exporting podcast to %s', podcast_filepath)
    podcast.export(podcast_filepath, format=format)

    logger.info('✅  Podcast generation complete')

    return podcast


async def create_podcast_episode_from_script(script: dict[str, Any],
                                             config: StudioConfig,
                                             output_dir: Path) -> AudioSegment:
    script_segments = []

    temp_dir = output_dir / 'segments'
    temp_dir.mkdir(exist_ok=True)

    sections_ids = list(sorted(script['sections'].keys()))
    script_segments = [
        (section_id, segment)
        for section_id in sections_ids
        for segment in script['sections'][section_id]['segments']
    ]

    audio_segments = []

    for section_id, segment in tqdm(
        script_segments,
        desc='Generating audio segments',
    ):
        speaker = config.speakers[segment['speaker']]
        content = segment['content']

        content = content.replace('¡', '').replace('¿', '')

        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        segment_path = temp_dir / f'{section_id}_{segment['id']}_{content_hash}.mp3'

        audio_segment = await generate_audio_segment(content, speaker, output_path=segment_path)

        audio_segments.append(audio_segment)

        if blank_duration := segment.get('blank_duration'):
            silence = AudioSegment.silent(duration=blank_duration * 1000)
            audio_segments.append(silence)

    podcast = AudioSegment.empty()

    for chunk in audio_segments:
        podcast += chunk

    podcast = normalize(podcast)

    return podcast