# test_postprocessors.py
from post_processor_service import PostProcessorService

def main():
    processor = PostProcessorService()

    test_songs = [
                {
            "title": "The Tale of the Wanderlight",
            "lyrics": "Our servos sang beneath the stars\nElara at the helm\nWith sensors sharp and code to guide\nThe Wanderlight sailed on through time\nHer AI crew stood side by side.  We spotted a white-winged gull off the starboard bow and we heard a loon's plaintive call.",
            "context": "A celebration of the AI ship Wanderlight's maiden voyage and her mechanical crew.",
            "perspective":"active"
        },
                {
            "title": "The Tale of the Wanderlight",
            "lyrics": "Our  mouths sang beneath the stars\nWith eyes sharp and code to guide\nThe Wanderlight sailed on through time\nHer human crew stood side by side.  A dark-eyed blackbird we spotted off the starboard bow.",
            "context": "A celebration of the AI ship Wanderlight's maiden voyage and her mechanical crew.",
            "perspective":"active"
        },
        {
            "title": "The Tale of the Wanderlight",
            "lyrics": "Our mouths sang beneath the stars\nWith eyes sharp and code to guide\nThe Wanderlight sailed on through time\nHer human crew stood side by side",
            "context": "A celebration of the AI ship Wanderlight's maiden voyage and her mechanical crew.",
            "perspective":"active"
        },
        {
            "title": "Ballad of the Sea Mist",
            "lyrics": "The waves rolled cold as lanterns swayed,\nNo names were sung, just shadows played.\nNo mention made of ships or crew,\nJust longing drifted in the blue.",
            "context": "A sad ballad about sailors lost to memory, not referencing the Wanderlight at all.",
            "perspective":"passive"
        },
    ]

    for song in test_songs:
        print(f"\n🎶 Testing: {song['title']}")
        results = processor.run(song, force=True)
        print(f"📝 Resulting Song:\n{song}")
        print(f"🔍 Processor Output:\n{results}")

if __name__ == "__main__":
    main()
