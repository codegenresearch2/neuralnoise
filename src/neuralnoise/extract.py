import os
from pathlib import Path
from tempfile import NamedTemporaryFile

import requests
from langchain_community.document_loaders import (
    BSHTMLLoader,
    PyMuPDFLoader,
    TextLoader,
    YoutubeLoader,
)
from langchain_community.document_loaders.base import BaseLoader


def get_best_loader(extract_from: str | Path) -> BaseLoader:
    match extract_from:
        case str() | Path() if os.path.isfile(extract_from):
            if os.path.splitext(extract_from)[1] == ".pdf":
                return PyMuPDFLoader(file_path=str(extract_from))
            else:
                return TextLoader(file_path=extract_from)
        case str() if extract_from.startswith("http"):
            if "youtube" in extract_from:
                video_id = YoutubeLoader.extract_video_id(extract_from)
                return YoutubeLoader(video_id=video_id)
            else:
                html_content = requests.get(extract_from).text

                with NamedTemporaryFile(delete=False, mode="w", suffix=".html") as f:
                    f.write(html_content)

                loader = BSHTMLLoader(file_path=f.name)
                f.close()

                return loader
        case _:
            raise ValueError("Invalid input")


def extract_content(extract_from: str | Path) -> str:
    loader = get_best_loader(extract_from)

    docs = loader.load()

    content = ""

    for doc in docs:
        if doc.metadata.get("title"):
            content += f"\n\n# {doc.metadata['title']}\n\n"

        content += doc.page_content.strip()

    return content
