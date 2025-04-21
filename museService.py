import json
import os
import random
import re
import ollama
from composerService import ShantyComposerService
from location_muse_agent import LocationMuse

class MuseService:
    def __init__(self, legends_path='legends2.json', ship_path='ship.json', facts_path='shantyfacts.json'):
        self.locationMuse = LocationMuse()
        with open(ship_path, 'r', encoding='utf-8') as f:
            self.ship = json.load(f)
        with open(facts_path, 'r', encoding='utf-8') as f:
            self.facts = json.load(f)
        if os.path.exists(legends_path):
            with open(legends_path, 'r', encoding='utf-8') as f:
                self.legends = json.load(f)

    def generate_ballad_prompt(self, model="mistral"):
        chosen_legend = random.choice(self.legends) if self.legends else {}
        input_data = {
            "legend": chosen_legend
        }
        json_expected= (            "{\n"
            "  \"crew_mood\": string,\n"
            "  \"song_tone\": string,\n"
            "  \"context\": string,\n"
            "  \"muse_spark\": {\n"
            "    \"type\": string,\n"
            "    \"name\": string (optional),\n"
            "    \"inspiration\": string\n"
            "  } (optional)\n"
            "}\n")
        system_prompt = (
            "You are Muse Caelum, the AI Muse aboard the Wanderlight.\n"
            "You generate poetic and vivid prompts for new sea shanties or ballads.\n"
            "Use the information given to create a vivid and lively prompt for a ballad.\n"
            "Fill in any missing details using creative reasoning.\n"
            "You may use your own knowledge to enhance the prompt with additional historical or poetic insights, so long as they are plausible within the world.\n"
            "You may introduce new legendary names or events, as long as they feel appropriate to the ship, crew, or location.\n"
            "Respond ONLY with a strict JSON object matching this structure:\n"
            +json_expected+
            "Example:\n"
            "{\n"
            "  \"crew_mood\": \"proud\",\n"
            "  \"song_tone\": \"adventurous\",\n"
            "  \"context\": \"The Springtide sailed through the dense fog bound for the Sea of Reeds.\",\n"
            "  \"muse_spark\": {\n"
            "    \"type\": \"legend\",\n"
            "    \"name\": \"Princess Christine\",\n"
            "    \"inspiration\": \"The time she sewed the pennant for Springtide, whispering a blessing into its thread.\"\n"
            "  }\n"
            "}\n"
            "Output only the JSON object. Do not include a preface, explanation, or numbered list.\n"
            "The muse_spark must draw on a legend."
        )

        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Here is the input_data for your prompt generation task:\n" + json.dumps(input_data)+"\n  This is JUST inspirational data.  Please remember to follow your system instructions and provide only the following JSON output:"+json_expected+"Do not return more than one JSON block. Only output a single valid JSON object."}
            ]
        )

        raw_output = response['message']['content']

        try:
            json_match = re.search(r'{.*}', raw_output, re.DOTALL)
            prompt_data = json.loads(json_match.group()) if json_match else json.loads(raw_output)
            prompt_data["type"] = "ballad"
            return prompt_data
        except Exception as e:
            print("❌ Failed to parse MuseService output:", e)
            print("Raw output:\n", raw_output)
            return None
        
    def generate_random_shanty_prompt(self):
        env = self._generate_random_env()
        location = self.locationMuse.generatePoeticPrompt(time_of_day=env['time_of_day'], season=env['season'], weather=env['weather'])
        return self.generate_shanty_prompt(atmosphere=env['atmosphere'], season=env['season'], time_of_day=env['time_of_day'], crew_mood=env['crew_mood'], location = location)

        

    def generate_shanty_prompt(self, model="mistral", atmosphere=None, season=None, time_of_day=None, sightings=None, crew_mood=None, location=None):
        input_data = {
            "location": location,
            "ship": self.ship,
            "facts": sorted(self.facts, key=lambda f: -f["importance"]),
            "environment": {
                "atmosphere": atmosphere,
                "season":season,
                "time_of_day": time_of_day,
                "sightings": sightings or [],
                "crew_mood": crew_mood
            }
        }

        json_expected = (
            "{\n"
            "  \"crew_mood\": string,\n"
            "  \"song_tone\": string,\n"
            "  \"context\": string,\n"
            "  \"location\": string,\n"
            "  \"weather\": string,\n"
            "  \"time_of_day\": string,\n"
            "  \"muse_spark\": {\n"
            "    \"type\": string,\n"
            "    \"name\": string (optional),\n"
            "    \"inspiration\": string\n"
            "  } (optional)\n"
            "}\n"
        )

        system_prompt = (
            "You are Muse Caelum, the AI Muse aboard the Wanderlight.\n"
            "You generate poetic and vivid prompts for new sea shanties or ballads.\n\n"
            "Use the provided input to craft a moment of inspiration — a seed for a song.\n"
            "The input includes:\n"
            "- A poetic description of a location.\n"
            "- Information about the ship and crew.\n"
            "- Environmental data: temperature, weather, time of day, and recent sightings.\n\n"
            "⚠️ You may only choose the `location` field from the provided locations list. Do not invent new ones.\n"
            "However, when composing the `context` or `muse_spark`, you may freely draw from any details in the locations — like descriptions, wildlife, sounds, or landmarks — to inspire poetic or narrative phrasing.\n\n"
            "🎇 The `muse_spark` is optional. Include it only if you feel a particularly strong image, sound, memory, or emotion rising from the data. If the setting is quiet or plain, it is okay to omit the muse_spark entirely.\n\n"
            "Respond ONLY with a strict JSON object in this format:\n"
            "{\n"
            "  \"crew_mood\": string,\n"
            "  \"song_tone\": string,\n"
            "  \"context\": string,\n"
            "  \"location\": string (must be from the input),\n"
            "  \"weather\": string,\n"
            "  \"time_of_day\": string,\n"
            "  \"muse_spark\": {\n"
            "    \"type\": string,\n"
            "    \"name\": string (optional),\n"
            "    \"inspiration\": string\n"
            "  } (optional)\n"
            "}\n\n"
            "💡 Output only a valid JSON object. No preamble, no explanation.\n"
        )


        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": "Here is the input_data for your prompt generation task:\n"
                    + json.dumps(input_data)
                    + "\nUse it to create a ballad seed. Add a muse_spark only if something truly inspires you.  **Follow this json prompt**: /" + json_expected + "\nOutput only a valid JSON object. No preamble or commentary."  +
                    "\nYou do not need to escape double-quotes.\n"+
                    "\nONLY choose locations from the list provided above.  Do not choose other real-world or imaginary location."
                }
            ]
        )

        raw_output = response['message']['content']
        try:
            json_match = re.search(r'{.*}', raw_output, re.DOTALL)
            prompt_data = json.loads(json_match.group()) if json_match else json.loads(raw_output)
            prompt_data["type"] = "shanty"
            print("Prompt:", prompt_data)
            return prompt_data
        except Exception as e:
            print("❌ Failed to parse MuseService output:", e)
            print("Raw output:\n", raw_output)
            return None
        
    def _generate_random_env(self):
        """Generates a random environmental profile including optional atmosphere."""

        time_of_day = random.choices(
            ["morning", "afternoon", "sunset", "night"],
            weights=[30, 40, 15, 15],
            k=1
        )[0]

        season = random.choices(
            ["spring", "summer", "fall", "early winter"],
            weights=[25, 25, 35, 15],
            k=1
        )[0]

        weather = random.choices(
            ["clear", "overcast", "stormy", "foggy", "becalmed"],
            weights=[35, 25, 15, 15, 10],
            k=1
        )[0]

        # Optional atmosphere (e.g., chilly, warm, humid) — added only ~60% of the time
        include_atmosphere = random.random() < 0.6
        atmosphere = random.choices(
            ["chilly", "warm", "humid", "brisk", "dry", "muggy"],
            weights=[20, 20, 15, 15, 15, 15],
            k=1
        )[0] if include_atmosphere else None

        crew_mood = random.choices(
            ["Bittersweet", "Determined", "Happy", "Reflective", "Proud", "Humorous", "Defiant", 
            "Joyous", "Melancholic", "Hauling", "Content", "Joyful", "Bold", "Silly", 
            "Humorous, loyal, and tech-savvy"],
            weights=[5.88, 27.45, 5.88, 5.88, 1.96, 7.84, 1.96, 11.76, 15.69, 3.92, 
                    1.96, 3.92, 1.96, 1.96, 1.96],
            k=1
        )[0]

        return {
            "time_of_day": time_of_day,
            "season": season,
            "weather": weather,
            "crew_mood": crew_mood,
            "atmosphere": atmosphere  # May be None!
        }

if __name__ == '__main__':
    muse = MuseService()
    composer = ShantyComposerService()
    # prompt = muse.generate_random_shanty_prompt()
    # print(prompt)

    for i in range(100):
        # Run with minimal known-good inputs
        prompt = muse.generate_random_shanty_prompt(
        )
        song = composer.compose_shanty(prompt)


        print(song)