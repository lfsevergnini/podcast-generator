import os
from openai import OpenAI
from pydub import AudioSegment

# Initialize the OpenAI client using the API key from environment variable
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_conversation(topic, resources):
    prompt = f"Generate a conversation between two people discussing {topic}. Use these resources for information: {resources}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are generating a podcast script for two speakers."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def text_to_speech(text, voice):
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text
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

        audio_content = text_to_speech(text, voice)
        with open("temp.mp3", "wb") as f:
            f.write(audio_content)

        segment = AudioSegment.from_mp3("temp.mp3")

        # Add a random pause between 0.25s and 0.5s
        combined_audio += segment + AudioSegment.silent(duration=int(250 + 250 * random.random()))

    os.remove("temp.mp3")
    combined_audio.export("podcast.mp3", format="mp3")

# Example usage
topic = "The future of AI"
resources = "https://example.com/ai-article, https://example.com/future-tech"

conversation = generate_conversation(topic, resources)
create_podcast(conversation)

print("Podcast generated and saved as 'podcast.mp3'")
