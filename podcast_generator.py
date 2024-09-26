import io
import os
import random
from openai import OpenAI
from pydub import AudioSegment

# Initialize the OpenAI client using the API key from environment variable
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_conversation(topic, resources):
    prompt = f"""Generate a conversation between two people discussing {topic}. Use these resources for information: {resources}
Use the following format, no markdown:

Speaker 1: ________
Speaker 2: ________
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are generating a podcast script for two speakers."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def text_to_speech(text, voice, speed=0.95, model="tts-1-hd"):
    response = client.audio.speech.create(
        input=text,
        voice=voice,
        speed=speed,
        model=model,
        response_format="wav"
    )
    return response.content

def create_podcast(conversation):
    combined_audio = AudioSegment.empty()
    lines = conversation.split('\n')

    for line in lines:
        if line.startswith("Speaker 1:"):
            voice = "shimmer"
            text = line.replace("Speaker 1:", "").strip()
        elif line.startswith("Speaker 2:"):
            voice = "onyx"
            text = line.replace("Speaker 2:", "").strip()
        else:
            continue

        audio_content = text_to_speech(text, voice, speed=random.uniform(0.95, 1.05))
        audio_segment = AudioSegment.from_wav(io.BytesIO(audio_content))

        # Normalize audio to a consistent volume
        normalized_audio = audio_segment.normalize(target_level=-5)

        # Add a slight fade in and out
        faded_audio = normalized_audio.fade_in(50).fade_out(50)

        # Add a random pause between 0.5s and 1s
        combined_audio += faded_audio + AudioSegment.silent(duration=int(500 + 500 * random.random()))

    # Export as WAV for highest quality
    combined_audio.export("podcast.wav", format="wav", parameters=["-ar", "44100", "-ac", "2"])

    # Convert WAV to MP3 with high bitrate for browser compatibility
    AudioSegment.from_wav("podcast.wav").export("podcast.mp3", format="mp3", bitrate="192k")

    os.remove("podcast.wav")

# Example usage
topic = "The future of AI"
resources = "https://example.com/ai-article, https://example.com/future-tech"

conversation = generate_conversation(topic, resources)

print(conversation)

create_podcast(conversation)

print("Podcast generated and saved as 'podcast.mp3'")
