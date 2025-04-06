import json
import os
from preprocessorService import SemanticPreprocessorService

# Load one song from shanty_songbook.json
def load_first_song(songbook_path="shanty_songbook.json"):
    with open(songbook_path, "r", encoding="utf-8") as f:
        songs = json.load(f)
    return songs[0]  # Get the first song

def run_test():
    # Initialize the evaluation service
    service = SemanticPreprocessorService()

    # Load the song
    song = load_first_song()

    # Evaluate it
    service.preprocess_song(song)

if __name__ == "__main__":
    run_test()
