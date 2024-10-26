# Neural Noise: Podcast Studio

<div align="center">
  <img src="./assets/banner.png" alt="Neural Noise banner" />
</div>

Neural Noise is an AI-powered podcast studio that uses multiple AI agents working together. These agents collaborate to analyze content, write scripts, and generate audio, creating high-quality podcast content with minimal human input. The team generates a script that the cast team (TTS of your choice) will then record.

## Examples

| Source | Neural Noise | NotebookLM |
| ------ | ------------ | ---------- |

| [BBC News article (TikTok owner sacks intern for sabotaging AI project
)](https://www.bbc.com/news/articles/c7v62gg49zro) | [Listen to Neural Noise version](placeholder_link) | [Listen to NotebookLM version](placeholder_link) |
| [BBC AI Podcast](https://www.bbc.com/news/articles/c7v62gg49zro) | [Listen to Neural Noise version](placeholder_link) | [Listen to NotebookLM version](placeholder_link) |

## Objective

The main objective of Neural Noise is to create a Python package that simplifies the process of generating AI podcasts. It utilizes OpenAI for content analysis and script generation, ElevenLabs for high-quality text-to-speech conversion, and Streamlit for an intuitive user interface.

## Features

- Content analysis and script generation using OpenAI's language models
- High-quality voice synthesis with ElevenLabs or OpenAI
- Audio processing and manipulation with pydub
- User-friendly interface built with Streamlit

## Installation

To install Neural Noise, follow these steps:

1. Install the package:

   ```
   pip install neuralnoise
   ```

   or from source:

   ```
   git clone https://github.com/leopiney/neuralnoise.git
   cd neuralnoise
   uv sync
   ```

2. Set up your API keys:

   - Create a `.env` file in the project root
   - Add your OpenAI and ElevenLabs API keys:

     ```
     OPENAI_API_KEY=your_openai_api_key

     # Optional
     ELEVENLABS_API_KEY=your_elevenlabs_api_key
     ```

## Usage

To run the Neural Noise application first make sure that you create a configuration file you want to use. There are examples in the `config` folder.

Then you can run the application with:

```
nn <url|filepath> --name <name> --config-path <config>
```

## Want to edit the generated script?

The generated script and audio segments are saved in the `output/<name>` folder. To edit the script:

1. Locate the JSON file in this folder containing all script segments and their text content.
2. Make your desired changes to specific segments in the JSON file. Locate the "sections" and "segments" content in this file that you want to change, then feel free to edit the content of the segments you want to change.
3. Run the same command as before (same name) to regenerate the podcast.

The application will regenerate the podcast, preserving unmodified segments and only processing the changed ones. This approach allows for efficient editing without regenerating the entire podcast from scratch.

## Roadmap

- [ ] Add local LLM provider. More generic LLM configuration. Leverage AutoGen for this.
- [ ] Add local TTS provider
- [ ] Add podcast generation format options: interview, narrative, etc.
- [ ] Add more agent roles to the studio. For example, a "Content Curator" or "Content Researcher" that uses tools to find and curate content before being analyzed. Or a "Sponsor" agent that adds segways to ads in the podcast script ([à la LTT](https://www.youtube.com/live/EefvOLKoXdg?si=G1714t2jK4ZIvao0&t=5307)).
- [ ] Add music and sound effects options
- [ ] Real-time podcast generation with human and AI collaboration (🤔)

## Contributing

Contributions to Neural Noise are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Related projects

- [NotebookLM](https://notebooklm.google.com/)
- [Podcastify.ai](https://github.com/souzatharsis/podcastfy)
