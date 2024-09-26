import os
import openai
from pydub import AudioSegment

# Set your OpenAI API key
openai.api_key = "your-api-key-here"

def generate_conversation(topic, resources):
    prompt = f"Generate a conversation between two people discussing {topic}. Use these resources for information: {resources}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are generating a podcast script for two speakers."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def text_to_speech(text, voice):
    response = openai.audio.speech.create(
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
        combined_audio += segment + AudioSegment.silent(duration=500)  # Add a 0.5s pause
    
    os.remove("temp.mp3")
    combined_audio.export("podcast.mp3", format="mp3")

# Example usage
topic = "The future of AI"
resources = "https://example.com/ai-article, https://example.com/future-tech"

conversation = generate_conversation(topic, resources)
create_podcast(conversation)

print("Podcast generated and saved as 'podcast.mp3'")
