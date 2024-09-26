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
        model=model
    )
    return response.content

def create_podcast(conversation):
    combined_audio = AudioSegment.empty()
    lines = conversation.split('\n')
    
    for line in lines:
        if line.startswith("Speaker 1:"):
            voice = "alloy"
            text = line.replace("Speaker 1:", "").strip()
        elif line.startswith("Speaker 2:"):
            voice = "echo"
            text = line.replace("Speaker 2:", "").strip()
        else:
            continue

        audio_content = text_to_speech(text, voice, speed=random.uniform(0.85, 1.2))
        with open("temp.mp3", "wb") as f:
            f.write(audio_content)

        segment = AudioSegment.from_mp3("temp.mp3")

        # Add a random pause between 0.3s and 0.5s
        combined_audio += segment + AudioSegment.silent(duration=int(300 + 200 * random.random()))

    os.remove("temp.mp3")
    combined_audio.export("podcast.mp3", format="mp3")

# Example usage
topic = "The future of AI"
resources = "https://example.com/ai-article, https://example.com/future-tech"

conversation = generate_conversation(topic, resources)

print(conversation)

create_podcast(conversation)

print("Podcast generated and saved as 'podcast.mp3'")
