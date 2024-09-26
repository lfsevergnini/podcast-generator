import requests
import json

API_KEY = 'your_elevenlabs_api_key'
TTS_ENDPOINT = 'https://api.elevenlabs.io/v1/text-to-speech'

def synthesize_speech(text, voice_id, filename):
    headers = {
        'Accept': 'audio/mpeg',
        'Content-Type': 'application/json',
        'xi-api-key': API_KEY
    }
    data = {
        "text": text,
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.75
        }
    }
    response = requests.post(f"{TTS_ENDPOINT}/{voice_id}/stream", headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        with open(f'../output/{filename}', 'wb') as f:
            f.write(response.content)
        print(f"Saved audio to ../output/{filename}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    with open('../output/conversation.txt', 'r') as file:
        conversation = file.read()

    # Split conversation into lines
    lines = conversation.split('\n')
    speaker1_text = []
    speaker2_text = []

    for line in lines:
        if line.startswith("Alice:"):
            speaker1_text.append(line.replace("Alice:", "").strip())
        elif line.startswith("Bob:"):
            speaker2_text.append(line.replace("Bob:", "").strip())

    speaker1_combined = "\n".join(speaker1_text)
    speaker2_combined = "\n".join(speaker2_text)

    synthesize_speech(speaker1_combined, 'voice_id_alice', 'speaker1.mp3')
    synthesize_speech(speaker2_combined, 'voice_id_bob', 'speaker2.mp3')
