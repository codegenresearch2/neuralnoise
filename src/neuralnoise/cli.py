from pathlib import Path

import typer
from dotenv import load_dotenv
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
from tabulate import tabulate

from neuralnoise.extract import extract_content
from neuralnoise.studio import create_podcast_episode

app = typer.Typer()

load_dotenv()


@app.command()
def new(
    input: str = typer.Argument(..., help="Path to the input file or URL"),
    name: str = typer.Option(..., help="Name of the podcast episode"),
    config: Path = typer.Option(..., help="Path to the podcast configuration file"),
    only_script: bool = typer.Option(False, help="Only generate the script and exit"),
):
    """
    Generate a script from an input text file using the specified configuration.

    For example:

    nn new <url|file> --name <name> --config config/config_openai.json
    """
    typer.echo(f"Generating script from {input}")

    output_dir = Path("output") / name
    output_dir.mkdir(parents=True, exist_ok=True)

    typer.echo(f"Extracting content from {input}")
    content = extract_content(input)

    with open(output_dir / "content.txt", "w") as f:
        f.write(content)

    typer.echo(f"Generating podcast episode {name}")
    create_podcast_episode(
        name,
        content,
        config_path=config,
        only_script=only_script,
    )

    typer.echo(f"Podcast generation complete. Output saved to {output_dir}")


def get_audio_length(file_path: Path) -> float:
    """Get the length of an audio file in seconds."""
    try:
        audio = AudioSegment.from_file(file_path)
        return len(audio) / 1000  # Convert milliseconds to seconds
    except CouldntDecodeError:
        typer.echo(f"Error: Couldn't decode audio file {file_path}")
        return -1.0


@app.command("list")
def list_episodes():
    """
    List all generated podcast episodes stored in the 'output' folder,
    including their audio file length in minutes. Episodes with invalid audio files are filtered out.
    """
    output_dir = Path("output")
    if not output_dir.exists():
        typer.echo("No episodes found. The 'output' folder does not exist.")
        return

    episodes = [d for d in output_dir.iterdir() if d.is_dir()]

    if not episodes:
        typer.echo("No episodes found in the 'output' folder.")
        return

    episode_data = []
    for episode in sorted(episodes):
        audio_files = list(episode.glob("*.wav")) + list(episode.glob("*.mp3"))
        if audio_files:
            audio_file = audio_files[0]  # Take the first audio file found
            length_seconds = get_audio_length(audio_file)
            if length_seconds != -1:  # Filter out invalid audio files
                length_minutes = length_seconds / 60  # Convert seconds to minutes
                episode_data.append(
                    [episode.name, audio_file.name, f"{length_minutes:.2f}"]
                )
        else:
            episode_data.append([episode.name, "No audio file", "N/A"])

    if not episode_data:
        typer.echo("No valid episodes found.")
        return

    headers = ["Episode", "Audio File", "Length (minutes)"]
    table = tabulate(episode_data, headers=headers, tablefmt="grid")
    typer.echo("Generated podcast episodes:")
    typer.echo(table)


if __name__ == "__main__":
    app()
