import argparse
import io
import os
import random
import requests
import numpy as np
import soundfile as sf
from dotenv import load_dotenv
from openai import OpenAI
from crawler import Crawler
load_dotenv()

# Initialize the OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")
openai_client = OpenAI(api_key=openai_api_key)

# Initialize the Cartesia client
cartesia_api_key = os.getenv("CARTESIA_API_KEY")
if not cartesia_api_key:
    raise ValueError("CARTESIA_API_KEY environment variable is not set")

def generate_conversation(podcast_name, topic, resources, character1, character2):
    # Fetch content from the resources
    resource_list = resources.split(',')
    crawler = Crawler(resource_list)
    fetched_content = crawler.fetch_content()
    resources_text = " ".join(fetched_content)

    prompt = f"""Generate an engaging and dynamic conversation between two people discussing {topic}. Use these resources for information: {resources_text}
Make the conversation lively and natural, including emotions, emphasis, and varied speech patterns. Use the following format, no markdown:

```
Speaker 1 (positivity): Hey, this is {character1}! Welcome to the {podcast_name} podcast! Today we're going to talk about {topic}.
Speaker 2 (curiosity): Hello {character1}! This is {character2}! ...
Speaker 1 (neutrality): ...
Speaker 1 (positivity): ...
Speaker 2 (surprise): ...
...
...
Speaker ??? (positivity): And that wraps up our podcast for today.
```

- You can alternate between the two speakers, but don't make it too obvious. During an explanation, the speaker should probably be the same.
- Supported emotions (within the parentheses): neutrality, curiosity, positivity, and surprise.
- Vary emotions and speech patterns naturally.
- If the resources provide author names, you may cite them as a reference.

Word limit: 300 words.
"""
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are generating a lively podcast script for two speakers with varied emotions and speech patterns."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def text_to_speech(text, voice_id, speed="normal", emotion=None):
    output_format = {
        "container": "wav",
        "encoding": "pcm_f32le",
        "sample_rate": 44100
    }

    experimental_controls = {}
    if speed != "normal":
        experimental_controls = {"speed": speed}
    if emotion and emotion != "neutrality":
        experimental_controls["emotion"] = [get_supported_emotion_for_emotion(emotion)]

    try:
        response = requests.post(
            "https://api.cartesia.ai/tts/bytes",
        headers={
            "X-API-Key": cartesia_api_key,
            "Cartesia-Version": "2024-06-10",
            "Content-Type": "application/json"
        },
        json={
            "model_id": "sonic-english",
            "transcript": text,
            "voice": {
                "mode": "id",
                "id": voice_id,
                "__experimental_controls": experimental_controls
            },
            "output_format": output_format,
            }
        )

        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None

def create_podcast(conversation, character1, character2):
    lines = conversation.split('\n')

    voices = {
        "jerry": "ee7ea9f8-c0c1-498c-9279-764d6b56d189", # generic man
        "lisa": "156fb8d2-335b-4950-9cb3-a2d33befec77", # generic woman
        "dua": "a3e63c00-e221-48a6-97cc-e2f48135611a",
        "gandalf": "c863b314-26b2-4855-b4fa-e38dc797385a",
        "post": "0c9d1cae-538e-49c3-9d41-e63a3cf6d5f9",
        "luis": "d95fed12-a136-4438-9be1-1aafa6c21b9b"
    }

    voice_ids = [voices.get(character1.lower(), voices["jerry"]), voices.get(character2.lower(), voices["lisa"])]

    audio_segments = []
    samplerate = None

    for line in lines:
        if line.startswith("Speaker 1"):
            voice_id = voice_ids[0]
            text = line.split(":", 1)[1].strip()
            emotion = line.split("(")[1].split(")")[0]
        elif line.startswith("Speaker 2"):
            voice_id = voice_ids[1]
            text = line.split(":", 1)[1].strip()
            emotion = line.split("(")[1].split(")")[0]
        else:
            continue

        speed = get_speed_for_emotion(emotion)
        audio_content = text_to_speech(text, voice_id, speed=speed, emotion=emotion)

        # Read audio data from bytes
        data, sr = sf.read(io.BytesIO(audio_content))
        if samplerate is None:
            samplerate = sr

        audio_segments.append(data)

    # Create silence between segments with random duration
    silence_durations = np.random.uniform(0.4, 0.7, len(audio_segments) - 1)
    silences = [np.zeros(int(duration * samplerate), dtype=audio_segments[0].dtype) for duration in silence_durations]

    # Combine all audio segments with varying silence in between
    combined_audio = np.concatenate([segment for pair in zip(audio_segments, silences + [np.array([])])
                                     for segment in pair if len(segment) > 0])

    # Write the combined audio to a file
    sf.write("podcast.wav", combined_audio, samplerate)

    print("High-quality podcast generated and saved as 'podcast.wav'")

def get_speed_for_emotion(emotion):
    emotion_speeds = {
        "curious": "normal",
        "explaining": "slow",
        "surprised": "fast",
        "excited": "fast",
        "thoughtful": "slow",
        "enthusiastic": "fast",
        "reassuring": "normal",
    }
    return emotion_speeds.get(emotion, "normal")

def get_supported_emotion_for_emotion(emotion):
    supported_emotions = ["neutrality", "curiosity", "positivity", "surprise"]

    if emotion in supported_emotions:
        return emotion
    if emotion == "curious" or emotion == "thoughtful":
        return "curiosity"
    if emotion == "excited" or emotion == "enthusiastic":
        return "positivity"
    if emotion == "surprised" or emotion == "reassuring":
        return "surprise"

    return "neutrality"

def main():
    parser = argparse.ArgumentParser(description="Generate a podcast based on a given topic and resources.")
    parser.add_argument("--podcast_name", type=str, required=True, help="The name of the podcast")
    parser.add_argument("--topic", type=str, required=True, help="The topic of the podcast")
    parser.add_argument("--resources", type=str, required=True, help="Comma-separated list of resources for the podcast")
    parser.add_argument("--character1", type=str, default="Jerry", help="Name of the first character")
    parser.add_argument("--character2", type=str, default="Lisa", help="Name of the second character")

    args = parser.parse_args()

    conversation = generate_conversation(args.podcast_name, args.topic, args.resources, args.character1, args.character2)

    print(conversation)

    create_podcast(conversation, args.character1, args.character2)

if __name__ == "__main__":
    main()
