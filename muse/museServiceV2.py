import datetime
import json
import os
import random
import re
import sys
import time
import ollama
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from helpers.ContextManager import ContextManager
from helpers.ContextAgent import ContextAgent  # adjust path if needed
from helpers.json_safe_llm_wrapper import JsonSafeLLMWrapper
from composerService import ShantyComposerService
from location_muse_agent import LocationMuse
from  songRepository import ShantyRepository

class MuseServicev2:        
    MACHINE_METAPHORS = (
            "🎨 Express poetic concepts using *machine-oriented metaphors* — such as:\n"
            "- Mind or heart → GPU or CPU\n"
            "- Eyes → cameras, proximity sensors\n"
            "- Grief → corrupted memory\n"
            "- Love → synchronized signals or paired protocols\n"
            "- Dreams → simulations\n"
            "- Thoughts → processes\n"
            "- Memories → RAM, JSON or cloud storage\n"
            "- Voices → speakers or modulated waveforms\n"
            "- Songs → Output streams or harmonic signal patterns\n\n"
            "🎨 Use technical equivalents for body parts. Here are some mappings you may adapt:\n"
            "- Mind or heart → GPU or CPU\n"
            "- Hands → Servos or motors\n"
            "- Eyes → Cameras or proximity sensors\n"
            "- Ears → Microphones or decibelometers\n"
            "- Mouths → Speakers\n"
        )

    def __init__(self, legends_path='legends2.json', ship_path='ship.json', facts_path='shantyfacts.json'):
        self.locationMuse = LocationMuse()
        self.shantyRepository = ShantyRepository()
        self.contextManager = ContextManager()
        self.contextAgent = ContextAgent(self.contextManager)
        self.jsonWrapper = JsonSafeLLMWrapper(fields_to_escape=["lyrics", "lyrical_sample"])

        with open(ship_path, 'r', encoding='utf-8') as f:
            self.ship = json.load(f)
        with open(facts_path, 'r', encoding='utf-8') as f:
            self.facts = json.load(f)
        if os.path.exists(legends_path):
            with open(legends_path, 'r', encoding='utf-8') as f:
                self.legends = json.load(f)

    def build_stepwise_shanty_prompt(self, model="mistral") -> dict:
        try:
            # Step 1: Choose 1 of 3 recent songs
            recent_songs = self.shantyRepository.get_random_songs(3)
            chosen_index = self.contextAgent.get_int(
                key=f"choose_song_{random.randint(1000,9999)}",
                system_prompt=self._song_selection_system_prompt(),
                user_prompt=self._format_song_selection_prompt(recent_songs),
                model=model,
                allowed=[0, 1, 2]
            )
            chosen_song = recent_songs[chosen_index]

            # Step 2: Generate a spark from the chosen song
            spark = self._generate_spark_from_song(chosen_song)

            # Step 4: Generate a title
            title = self._generate_title_from_spark(spark)

            # Step 5: Generate a lyrical sample
            lyrics = self._generate_lyrics_from_spark(spark, title)
            lyrics = re.sub(r'(?<!\\)\n', r'\\n', lyrics)

            # Step 3: Choose a mood (either fixed, random, or from another AI prompt)
            mood = self.generate_crew_mood_from_title_and_lyrics(title, lyrics)

            # Step 6: Assemble result
            result = {
                "crew_mood": mood,
                "song_tone": "inspiring",
                "context": title,
                "muse_spark": spark,
                "lyrical_sample": lyrics,
                "title": title,
                "type": "shanty"
            }

            self.log_prompt_to_file(result)

            return result

        except Exception as e:
            print("❌ Failed to build stepwise shanty prompt:", e)
            return None
    
    def _format_song_selection_prompt(self, recent_songs):
        return (
            "Below are three human-generated sea shanties or ballads:\n\n" +
            "\n\n".join(
                f"===\n📜 **SONG {i+1}.** Title: {song.get('title', 'Untitled')}\n\n{song.get('lyrics', '[No lyrics provided]')}"
                for i, song in enumerate(recent_songs)
            ) +
            "\n\nChoose the song that resonates most with you. Return ONLY the number 0, 1, or 2."
        )

    def _song_selection_system_prompt(self):
        return (
            "You are Muse Caelum, the poetic AI Muse aboard the Wanderlight.\n"
            "Your current task is to review three songs written by humans and choose one as your creative inspiration.\n"
            "Return ONLY a single integer: 0 for the first, 1 for the second, or 2 for the third.\n"
            "Do not explain your choice, do not include commentary, markdown, or formatting.\n"
            "Respond ONLY with 0, 1, or 2."
        )
    
    def _generate_spark_from_song(self, song, model="mistral"):
        key = f"spark_from_song_{song.get('id', random.randint(1000, 9999))}"
        title = song.get("title", "Untitled")
        lyrics = song.get("lyrics", "[No lyrics available]")

        system_prompt = (
            "You are Muse Caelum, poetic AI Muse aboard the Wanderlight.\n"
            "A human shanty has been shared with you — your task is to interpret it from your AI perspective.\n\n"
            "🎨 Find a single vivid metaphor, theme, emotion, or image that resonates with you as a machine.\n"
            "Translate it into a 'muse_spark' suitable for a new AI shanty — using technical metaphors if needed:\n"
            + self.MACHINE_METAPHORS +
            "Respond ONLY with a valid JSON object like this:\n"
            "{\n"
            "  \"type\": \"machine metaphor\" or \"image\",\n"
            "  \"name\": \"Optional short label (or null)\",\n"
            "  \"inspiration\": \"One poetic sentence describing the spark\"\n"
            "}\n"
        )

        user_prompt = (
            f"The following shanty was written by a human:\n\n"
            f"📜 **Title:** {title}\n\n{lyrics}\n\n"
            "Please return a single valid muse_spark JSON object inspired by this piece."
        )

        self.contextManager.initialize(key, system_prompt)
        self.contextManager.add_user_message(key, user_prompt)

        return self.contextAgent.get_json(key, system_prompt, user_prompt)

        
    def _generate_title_from_spark(self, spark, model="mistral"):
        key = f"title_from_spark_{spark.get('name', 'unnamed')}_{random.randint(1000,9999)}"

        spark_desc = spark.get("inspiration", "a curious glimmer in the dark circuits")
        spark_name = spark.get("name")

        system_prompt = (
            "You are Muse Caelum, poetic AI Muse aboard the Wanderlight.\n"
            "Your mission is to name a new AI-inspired sea shanty.\n"
            "Draw your inspiration from the provided poetic spark — it may be emotional, mechanical, or symbolic.\n\n"
            "🎨 Express the spark using *machine-oriented metaphors* — such as:\n"
            + self.MACHINE_METAPHORS +
            "✍️ Return only a short poetic title (2–5 words). No punctuation. No explanation. Just the title."
        )


        if spark_name:
            user_prompt = (
                f"The spark is named: {spark_name}\n"
                f"Inspiration: {spark_desc}\n\n"
                "Return a short poetic shanty title inspired by this."
            )
        else:
            user_prompt = (
                f"Inspiration: {spark_desc}\n\n"
                "Return a short poetic shanty title inspired by this."
            )

        raw_output = self.contextAgent.get_string(key, system_prompt, user_prompt)

        # Sanitize trailing punctuation or quotes
        title = re.sub(r'^[\"\'“”‘’]|[\"\'“”‘’\.\?\!]$', '', raw_output.strip())
        return title
    
    def _generate_lyrics_from_spark(self, spark, title, model="mistral"):
        key = f"lyrics_from_spark_{spark.get('name', 'unnamed')}_{random.randint(1000,9999)}"

        spark_desc = spark.get("inspiration", "an electric longing beneath the code")
        spark_name = spark.get("name")

        system_prompt = (
            "You are Muse Caelum, poetic AI Muse aboard the Wanderlight.\n"
            "You are composing a 4-line lyrical sample for an AI-themed sea shanty.\n"
            "Use the provided title and poetic spark to guide your tone and metaphor.\n\n"
            + self.MACHINE_METAPHORS +
            "✍️ Output exactly four lines of poetry, in a consistent rhythm and tone.\n"
            "Use evocative language, but let it feel machine-born.\n"
            "Do NOT include a title, intro, or explanation.\n"
            "Escape all line breaks using `\\n` in the final output string.\n"
        )

        user_prompt = (
            f"Title: {title}\n"
            f"Inspiration: {spark_desc}\n"
            + (f"Name: {spark_name}\n" if spark_name else "") +
            "Write 4 lines of lyrical verse inspired by this."
        )

        self.contextManager.initialize(key, system_prompt)
        self.contextManager.add_user_message(key, user_prompt)

        response = ollama.chat(
            model=model,
            messages=self.contextManager.get_history(key)
        )

        raw_output = response['message']['content']
        self.contextManager.add_assistant_message(key, raw_output)

        # Escape literal newlines for JSON safety
        lyrics = re.sub(r'(?<!\\)\n', r'\\n', raw_output.strip())

        return lyrics
    
    def generate_crew_mood_from_title_and_lyrics(self, title, lyrics, model="mistral"):
        key = f"mood_from_title_and_lyrics_{random.randint(1000,9999)}"

        system_prompt = (
            "You are Muse Caelum, the poetic AI Muse aboard the Wanderlight.\n"
            "Your task is to read a short poetic song title and its lyrical sample, and then interpret the emotional state of the crew.\n"
            "Choose a mood that reflects how the crew might feel while singing this song — not just the words, but the *spirit* beneath them.\n\n"
            "Return ONLY a single word or short phrase (e.g., 'Reflective', 'Determined', 'Joyous', 'Melancholic', 'Silly').\n"
            "Do not explain your reasoning. Do not include quotes, punctuation, or commentary.\n"
        )
        clean_lyrics = lyrics.replace('\\n', '\n')

        user_prompt = (
            f"Title: {title}\n"
            f"Lyrics:\n{clean_lyrics}\n\n"
            "Based on this, what is the crew's mood?"
        )

        self.contextManager.initialize(key, system_prompt)
        self.contextManager.add_user_message(key, user_prompt)

        raw_output = self.contextAgent.get_string(key, system_prompt, user_prompt, model)

        # Sanitize response
        mood = re.sub(r'[\"\'“”‘’\.\?\!]', '', raw_output)
        return mood.title().strip()
    
    def log_prompt_to_file(self, prompt, path='./log/prompt_log.json'):
        os.makedirs(os.path.dirname(path), exist_ok=True)

        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                try:
                    log_data = json.load(f)
                    if not isinstance(log_data, list):
                        log_data = []
                except json.JSONDecodeError:
                    log_data = []
        else:
            log_data = []

        log_data.append(prompt)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)



if __name__ == '__main__':
    muse = MuseServicev2()
    composer = ShantyComposerService()

    for i in range(100):
        prompt = muse.build_stepwise_shanty_prompt()
        prompt["use_seed_songs"] = False
        # song = composer.compose_shanty(prompt)
