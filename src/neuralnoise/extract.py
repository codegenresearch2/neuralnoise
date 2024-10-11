import os
from asyncio import run
from pathlib import Path


async def crawl_web(url: str) -> str:
    from crawl4ai import AsyncWebCrawler

    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(
            url,
            css_selector="article",
        )

    if result.markdown is None:
        raise ValueError(f"No valid content found at {url}")

    return result.markdown


def extract_content(extract_from: str | Path) -> str:
    # TODO: allow more types if content extraction
    if os.path.isfile(extract_from):
        with open(extract_from, "r") as file:
            content = file.read()
    elif isinstance(extract_from, str) and extract_from.startswith("http"):
        content = run(crawl_web(extract_from))
    else:
        raise ValueError("Invalid input")

    return content
