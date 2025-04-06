import json
import os
from philosopherService import EvaluationAgentService

# Load one song from shanty_songbook.json
def load_first_song(songbook_path="shanty_songbook.json"):
    with open(songbook_path, "r", encoding="utf-8") as f:
        songs = json.load(f)
    return songs[0]  # Get the first song

def run_test():
    # Initialize the evaluation service
    service = EvaluationAgentService(
        evaluator_path="evaluators",  # path to evaluator JSON files
        model="mistral"               # model name for ollama
    )

    # Load the song
    song = load_first_song()

    # Evaluate it
    results = service.evaluate(song)

    # Print results nicely
    print(f"\nEvaluating Song: {song['title']}")
    for result in results:
        print("\n=== Evaluation by:", result["evaluator"], "===")
        print("Description:", result["description"])
        print("Score:", result["score"])

if __name__ == "__main__":
    run_test()
