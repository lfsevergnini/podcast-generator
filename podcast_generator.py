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

def generate_conversation(podcast_name, topic, resources):
    # Fetch content from the resources
    resource_list = resources.split(',')
    crawler = Crawler(resource_list)
    fetched_content = crawler.fetch_content()
    resources_text = " ".join(fetched_content)

    prompt = f"""Generate an engaging and dynamic conversation between two people discussing {topic}. Use these resources for information: {resources_text}
Make the conversation lively and natural, including emotions, emphasis, and varied speech patterns. Use the following format, no markdown:

```
Speaker 1 (excited): <emphasis>Welcome to the {podcast_name} podcast!</emphasis> Today we're going to talk about {topic}.
Speaker 2 (curious): ...
Speaker 1 (explaining): ...
...
...
Speaker ??? (reassuring): And that wraps up our podcast for today.
```

- You can alternate between the two speakers, but don't repeat the same speaker twice in a row very often.
- Supported emotions (within the parentheses): neutrality, curiosity, positivity, and surprise.
- Create a whole new conversation, do NOT repeat the example conversation.
- Vary emotions and speech patterns naturally.
- If the resources provide author names, you may cite them as a reference.

Word limit: 300 words.
"""
    response = openai_client.chat.completions.create(
        model="gpt-4o",
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
        experimental_controls["emotion"] = [emotion]

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

    return response.content

def create_podcast(conversation):
    lines = conversation.split('\n')

    # Selected voices
    woman_voice_id = "156fb8d2-335b-4950-9cb3-a2d33befec77"
    man_voice_id = "ee7ea9f8-c0c1-498c-9279-764d6b56d189"

    voice_ids = [woman_voice_id, man_voice_id]
    random.shuffle(voice_ids)

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

    # Create silence between segments
    silence_duration = 0.5  # 0.5 seconds of silence
    silence = np.zeros(int(silence_duration * samplerate), dtype=audio_segments[0].dtype)

    # Combine all audio segments with silence in between
    combined_audio = np.concatenate([segment for pair in zip(audio_segments, [silence] * len(audio_segments)) for segment in pair][:-1])

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

def main():
    parser = argparse.ArgumentParser(description="Generate a podcast based on a given topic and resources.")
    parser.add_argument("--podcast_name", type=str, required=True, help="The name of the podcast")
    parser.add_argument("--topic", type=str, required=True, help="The topic of the podcast")
    parser.add_argument("--resources", type=str, required=True, help="Comma-separated list of resources for the podcast")

    args = parser.parse_args()

    # conversation = generate_conversation(args.podcast_name, args.topic, args.resources)
    conversation = """Speaker 1 (neutrality): Hello Luis!
Speaker 2 (curiosity): How is it going?
Speaker 1 (positivity): Not much, just working on this podcast. You?
Speaker 2 (surprise): Podcast?
Speaker 1 (positivity): Yeah, I'm trying to get better at this whole podcast thing.
Speaker 2 (curiosity): How's it going?
Speaker 1 (positivity): Not bad, I think. I'm getting the hang of it.
Speaker 2 (curiosity): What's the topic?
Speaker 1 (positivity): I'm not sure yet, but I'm sure we'll figure it out.
"""

    # print(conversation)

    create_podcast(conversation)

if __name__ == "__main__":
    main()
