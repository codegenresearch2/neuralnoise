from pathlib import Path
from string import Template


def load_prompt(prompt_name: str, **kwargs: str) -> str:
    prompt_path = Path("prompts") / f"{prompt_name}.xml"

    with open(prompt_path, "r") as f:
        content = f.read()

    if kwargs:
        template = Template(content)
        content = template.safe_substitute(kwargs)

    return content
