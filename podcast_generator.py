import argparse
import io
import os
import random
from openai import OpenAI
from pydub import AudioSegment

# Initialize the OpenAI client using the API key from environment variable
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_conversation(topic, resources):
    prompt = f"""Generate an engaging and dynamic conversation between two people discussing {topic}. Use these resources for information: {resources}
Make the conversation lively and natural, including emotions, emphasis, and varied speech patterns. Use the following format, no markdown:

Speaker 1 (excited): <emphasis>Wow!</emphasis> Did you hear about the latest developments in {topic}?
Speaker 2 (curious): No, I haven't. <break time="0.5s"/> What's happening?
Speaker 1 (explaining): ...

You can alternate between the two speakers, but don't repeat the same speaker twice in a row very often.

Possible emotions (within the parentheses): excited, curious, explaining, surprised, thoughtful, enthusiastic, reassuring, thrilled

Create a whole new conversation, varying emotions and speech patterns naturally.

Word limit: 300 words.
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are generating a lively podcast script for two speakers with varied emotions and speech patterns."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def text_to_speech(text, voice, speed=1.0, model="tts-1-hd"):
    # Convert our custom tags to SSML
    ssml_text = f"<speak>{text}</speak>"

    response = client.audio.speech.create(
        input=ssml_text,
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
        if line.startswith("Speaker 1"):
            voice = "shimmer"
            text = line.split(":", 1)[1].strip()
            emotion = line.split("(")[1].split(")")[0]
        elif line.startswith("Speaker 2"):
            voice = "onyx"
            text = line.split(":", 1)[1].strip()
            emotion = line.split("(")[1].split(")")[0]
        else:
            continue

        # Adjust speed and pitch based on emotion
        speed = get_speed_for_emotion(emotion)
        
        audio_content = text_to_speech(text, voice, speed=speed)
        audio_segment = AudioSegment.from_wav(io.BytesIO(audio_content))

        # Normalize audio to a consistent volume
        normalized_audio = audio_segment.normalize()

        # Add a slight fade in and out
        faded_audio = normalized_audio.fade_in(50).fade_out(50)

        # Add a random pause for more natural timing
        combined_audio += faded_audio + AudioSegment.silent(duration=int(50 + 300 * random.random()))

    # Export as WAV for highest quality
    combined_audio.export("podcast.wav", format="wav", parameters=["-ar", "44100", "-ac", "2"])

    # Convert WAV to MP3 with high bitrate for browser compatibility
    AudioSegment.from_wav("podcast.wav").export("podcast.mp3", format="mp3", bitrate="192k")

    os.remove("podcast.wav")

def get_speed_for_emotion(emotion):
    emotion_speeds = {
        "excited": 1.15,
        "curious": 1.0,
        "explaining": 0.95,
        "surprised": 1.1,
        "thrilled": 1.25,
        "thoughtful": 0.9,
        "enthusiastic": 1.2,
        "reassuring": 1.05,
    }
    return emotion_speeds.get(emotion, 1.0)

def main():
    parser = argparse.ArgumentParser(description="Generate a podcast based on a given topic and resources.")
    parser.add_argument("--topic", type=str, required=True, help="The topic of the podcast")
    parser.add_argument("--resources", type=str, required=True, help="Comma-separated list of resources for the podcast")

    args = parser.parse_args()

    conversation = generate_conversation(args.topic, args.resources)

    print(conversation)

    create_podcast(conversation)

    print("Podcast generated and saved as 'podcast.mp3'")

if __name__ == "__main__":
    main()
