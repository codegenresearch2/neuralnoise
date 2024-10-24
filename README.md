# Neural Noise: Podcast Studio

<div align="center">
  <img src="./assets/banner.png" alt="Neural Noise banner" />
</div>

Neural Noise is an AI-powered podcast studio that uses multiple AI agents working together. These agents collaborate to analyze content, write scripts, and generate audio, creating high-quality podcast content with minimal human input. The team generates a script that the cast team (TTS of your choice) will then record.

## Examples

### BBC AI Podcast

Episode generated from this BBC article: https://www.bbc.com/news/articles/c7v62gg49zro

<div align="center">
  <audio src="./assets/example_bbc_ai_podcast.mp4" controls></audio>
</div>

## Objective

The main objective of Neural Noise is to create a Python package that simplifies the process of generating AI podcasts. It utilizes OpenAI for content analysis and script generation, ElevenLabs for high-quality text-to-speech conversion, and Streamlit for an intuitive user interface.

## Features

- Content analysis and script generation using OpenAI's language models
- High-quality voice synthesis with ElevenLabs
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

4. Set up your API keys:
   - Create a `.env` file in the project root
   - Add your OpenAI and ElevenLabs API keys:
     ```
     OPENAI_API_KEY=your_openai_api_key
     ELEVENLABS_API_KEY=your_elevenlabs_api_key
     ```

## Usage

To run the Neural Noise application first make sure that you create a configuration file you want to use. There are examples in the `config` folder.

Then you can run the application with:

```
nn <url|filepath> --name <name> --config-path <config>
```

## Roadmap

- [ ] Add local LLM provider
- [ ] Add local TTS provider
- [ ] Add podcast format (interview, narrative, etc.)
- [ ] Add music and sound effects options
- [ ] Add additional agents to the studio

## Contributing

Contributions to Neural Noise are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This project is for educational and experimental purposes only. Ensure you comply with the terms of service of all third-party APIs used in this project.