from pydub import AudioSegment

def merge_audios(speaker1_file, speaker2_file, output_file):
    speaker1 = AudioSegment.from_mp3(f'../output/{speaker1_file}')
    speaker2 = AudioSegment.from_mp3(f'../output/{speaker2_file}')

    # Simple merge: overlay or alternate as needed
    final = speaker1.overlay(speaker2)
    final.export(f'../output/{output_file}', format='mp3')
    print(f"Final podcast saved to ../output/{output_file}")

if __name__ == "__main__":
    merge_audios('speaker1.mp3', 'speaker2.mp3', 'final_podcast.mp3')
