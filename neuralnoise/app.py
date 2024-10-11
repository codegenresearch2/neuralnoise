import json
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from neuralnoise.generate import generate_podcast
from neuralnoise.types import AppConfig, Speaker, VoiceSettings

load_dotenv()

# Load app configuration
with open("config/app_config.json", "r") as config_file:
    app_config = AppConfig.parse_obj(json.load(config_file))

st.set_page_config(page_title="AI Podcast Generator", layout="wide")

st.title("AI Podcast Generator")

# Content input
st.header("Content Input")
content = st.text_area("Enter your content here:", height=300)

# Configuration
st.header("Configuration")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Speaker 1")
    speaker1_voice_id = st.text_input(
        "Voice ID for Speaker 1:", value=app_config.speakers["speaker1"].voice_id
    )
    speaker1_stability = st.slider(
        "Stability for Speaker 1:",
        0.0,
        1.0,
        app_config.speakers["speaker1"].voice_settings.stability,
        0.01,
    )
    speaker1_similarity = st.slider(
        "Similarity Boost for Speaker 1:",
        0.0,
        1.0,
        app_config.speakers["speaker1"].voice_settings.similarity_boost,
        0.01,
    )

with col2:
    st.subheader("Speaker 2")
    speaker2_voice_id = st.text_input(
        "Voice ID for Speaker 2:", value=app_config.speakers["speaker2"].voice_id
    )
    speaker2_stability = st.slider(
        "Stability for Speaker 2:",
        0.0,
        1.0,
        app_config.speakers["speaker2"].voice_settings.stability,
        0.01,
    )
    speaker2_similarity = st.slider(
        "Similarity Boost for Speaker 2:",
        0.0,
        1.0,
        app_config.speakers["speaker2"].voice_settings.similarity_boost,
        0.01,
    )

if st.button("Generate Podcast"):
    if not content:
        st.error("Please provide content for the podcast.")
    else:
        # Save content to a temporary file
        content_file = Path("temp_content.txt")
        content_file.write_text(content)

        # Create configuration
        config = AppConfig(
            speakers={
                "speaker1": Speaker(
                    name="Carlos",
                    aliases=["Charly", "Calini"],
                    voice_id=speaker1_voice_id,
                    voice_settings=VoiceSettings(
                        stability=speaker1_stability,
                        similarity_boost=speaker1_similarity,
                    ),
                ),
                "speaker2": Speaker(
                    name="Nacho",
                    aliases=["Nachito"],
                    voice_id=speaker2_voice_id,
                    voice_settings=VoiceSettings(
                        stability=speaker2_stability,
                        similarity_boost=speaker2_similarity,
                    ),
                ),
            },
            music=app_config.music,
        )

        # Save configuration to a temporary JSON file
        config_file = Path("temp_config.json")
        config_file.write_text(config.json())

        # Generate podcast
        output_file = "generated_podcast.mp3"
        with st.spinner("Generating podcast..."):
            generate_podcast(str(content_file), str(config_file), output_file)

        # Provide download link
        st.success("Podcast generated successfully!")
        with open(output_file, "rb") as f:
            st.download_button("Download Podcast", f, file_name="generated_podcast.mp3")

        # Clean up temporary files
        content_file.unlink()
        config_file.unlink()

st.markdown("---")
st.markdown("Created by Your Name")
