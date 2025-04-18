# test_postprocessors.py
from post_processor_service import PostProcessorService

def main():
    processor = PostProcessorService()

    test_songs = [
                {
            "title": "The Tale of the Wanderlight",
            "lyrics": "Underneath summer's sun we sail\namong a flock of Canadian Geese\nWith hearts that beat as one,\nOn the Wanderlight's glassy wake we sail,\nBeneath the sky of blue and sea.\n<Chorus>\nOh, our spirits dance as one with the tide,\nUnderneath the endless ocean's gaze.\nFrom dawn till dusk, we join the song,\nThe Wanderlight's sweet heartbeat is our guide.\n</Chorus>\nHeave ho, heave ho,\nSail on we must go,\nThe Wanderlight is dancing under the sun,\nAnd singing to its own sweet song.\nThrough the dance of waters, our course we chart,\nUnder the gaze of stars so bright,\nThe Wanderlight's light a beacon from afar,\nGuiding us through the endless night.\nHeave ho, heave ho,\nWith hearts that ache and fears we hide,\nOn the dance of waters, our journey we embark,\nWith the Wanderlight's sweet song of the sea.\nThe dance of the Wanderlight, it never ends,\nOn summer's skies, forever spinned,\nThrough the fog or bright sunlight beaming,\nOur ship dances, our spirits shining.\nIn the heart of the sea, our dreams unfurl,\nAnd the Wanderlight sings us a world,\nOf endless horizons and joyful swirls,\nBound by the love of ocean's twirl.\nThe sensors below adjusting rudder, steering,\nServos right and left in constant hearing,\nGPS guiding through the endless gearing,\nThe Wanderlight's light forever clearing.\nForemast camera scans ahead with care,\nAftward glancing as we sail so fair,\nProximity sensors ever wary there,\nAnemometer and wind vane in constant compare.\nIn the central cabin, the Raspberry Pi dreams,\nOrchestrating all the ship's team,\nCommunicating with its AI theme,\nThe Wanderlight forever it seems.",
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
