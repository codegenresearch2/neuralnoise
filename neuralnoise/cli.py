from pathlib import Path

import typer
from dotenv import load_dotenv

from neuralnoise.generate import generate_podcast

app = typer.Typer()

load_dotenv()


@app.command()
def generate_script(
    content_file: Path = typer.Argument(..., help="Path to the input text file"),
    config_file: Path = typer.Option(..., help="Path to the configuration file"),
    output_dir: Path = typer.Option(
        Path("output"), help="Directory to save the generated script"
    ),
    only_script: bool = typer.Option(False, help="Only generate the script and exit"),
):
    """
    Generate a script from an input text file using the specified configuration.
    """
    typer.echo(f"Generating script from {content_file}")

    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"{content_file.stem}_podcast.mp3"

    generate_podcast(
        content_file=str(content_file),
        config_file=str(config_file),
        output_file=str(output_file),
        only_script=only_script,
    )

    typer.echo(f"Podcast generation complete. Output saved to {output_dir}")


if __name__ == "__main__":
    app()
