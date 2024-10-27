from pathlib import Path

import typer
from dotenv import load_dotenv

from neuralnoise.extract import extract_content
from neuralnoise.studio import create_podcast_episode

app = typer.Typer()

load_dotenv()


@app.command()
def new(
    input: str = typer.Argument(..., help="Path to the input file or URL"),
    name: str = typer.Option(..., help="Name of the podcast episode"),
    config_file: Path = typer.Option(
        ..., help="Path to the podcast configuration file"
    ),
    only_script: bool = typer.Option(False, help="Only generate the script and exit"),
):
    """
    Generate a script from an input text file using the specified configuration.

    For example:

    nn <url|file> --name <name> --config-file config/config_openai.json
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
        config_file=config_file,
        only_script=only_script,
    )

    typer.echo(f"Podcast generation complete. Output saved to {output_dir}")


if __name__ == "__main__":
    app()
