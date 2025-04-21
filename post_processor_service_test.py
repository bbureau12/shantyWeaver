# test_postprocessors.py
from post_processor_service import PostProcessorService

def main():
    processor = PostProcessorService()

    test_songs = [
                {
            "title": "The Tale of the Wanderlight",
            "lyrics": "Beneath the azure sky we set our course,\nSailing towards the horizon far;\nWith compass wavering, yet we're bound by fate,\nCamarderie unbroken on this voyage of ours.\n\nAboard the Wavering Compass, our ship so grand,\nThe wind her song, the sea our dance;\nThrough storm and calm, we sail in union,\nOur bonds unbreakable, our spirits uncaught.\n\nEchoes of laughter on the salty breeze,\nFriends and foes become family at sea;\nFrom dawn to dusk, we share a story,\nA harmonious tale, as the compass wavers free.\n\nThe compass wavering, yet we sail ahead,\nOn a path unknown, to destiny unread;\nWith hearts resolute, and spirits unbound,\nWe'll ride these waves, on land or sea we roam.",
            "context": "A celebration of the AI ship Wanderlight's maiden voyage and her mechanical crew.",
            "tone":"sad",
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
