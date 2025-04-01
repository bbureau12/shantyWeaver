import json
import re
import ollama

class MuseService:
    def __init__(self, legends_path='legends.json', ship_path='ship.json', facts_path='shantyfacts.json', locations_path='locations.json'):
        with open(ship_path, 'r', encoding='utf-8') as f:
            self.ship = json.load(f)
        with open(facts_path, 'r', encoding='utf-8') as f:
            self.facts = json.load(f)
        with open(locations_path, 'r', encoding='utf-8') as f:
            self.locations = json.load(f)
        with open(legends_path,  'r', encoding='utf-8') as f:
            self.legends = json.load(f)

    def generate_ballad_prompt(self, model="mistral"):
        input_data = {
            "locations": self.locations,
            "ship": self.legends
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
            "Use the information given to create an idea for a ballad.\n"
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
                {"role": "user", "content": "Here is the input_data for your prompt generation task:\n" + json.dumps(input_data)+"\n  This is JUST inspirational data.  Please remember to follow your system instructions and provide only the following JSON output:"+json_expected}
            ]
        )

        raw_output = response['message']['content']

        try:
            json_match = re.search(r'{.*}', raw_output, re.DOTALL)
            return json.loads(json_match.group()) if json_match else json.loads(raw_output)
        except Exception as e:
            print("❌ Failed to parse MuseService output:", e)
            print("Raw output:\n", raw_output)
            return None
        


    def generate_shanty_prompt(self, model="mistral", temperature=None, wind_speed=None, time_of_day=None, sightings=None, crew_mood=None):
        input_data = {
            "locations": self.locations,
            "ship": self.ship,
            "facts": sorted(self.facts, key=lambda f: -f["importance"]),
            "environment": {
                "temperature": temperature,
                "wind_speed": wind_speed,
                "time_of_day": time_of_day,
                "sightings": sightings or [],
                "crew_mood": crew_mood
            }
        }
        json_expected= (            "{\n"
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
            "}\n")
        system_prompt = (
            "You are Muse Caelum, the AI Muse aboard the Wanderlight.\n"
            "You generate poetic and vivid prompts for new sea shanties or ballads.\n"
            "Use the information given to create an idea for a shanty.\n"
            "Fill in any missing details using creative reasoning.\n"
            "You may use your own knowledge to enhance the prompt with additional historical or poetic insights, so long as they are plausible within the world.\n"
            "You may introduce new legendary names or events, as long as they feel appropriate to the ship, crew, or location.\n"
            "Respond ONLY with a strict JSON object matching this structure:\n"
            +json_expected+
            "Example:\n"
            "{\n"
            "  \"crew_mood\": \"restless and excited\",\n"
            "  \"song_tone\": \"adventurous\",\n"
            "  \"context\": \"We set sail from Mahtoska Park, her pearly gazebo in sight.\",\n"
            "  \"location\": \"Mahtoska Park\",\n"
            "  \"weather\": \"A warm, rising wind with fog banks forming to the east.\",\n"
            "  \"time_of_day\": \"late afternoon\",\n"
            "  \"muse_spark\": {\n"
            "    \"type\": \"legend\",\n"
            "    \"name\": \"Princess Christine\",\n"
            "    \"inspiration\": \"The time she sewed the pennant for Springtide, whispering a blessing into its thread.\"\n"
            "  }\n"
            "}\n"
            "Output only the JSON object. Do not include a preface, explanation, or numbered list.\n"
            "The muse_spark may draw on a legend, a historical ship fact, or a cultural note about shanties."
        )

        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Here is the input_data for your prompt generation task:\n" + json.dumps(input_data)+"\n  This is JUST inspirational data.  Please remember to follow your system instructions and provide only the following JSON output:"+json_expected}
            ]
        )

        raw_output = response['message']['content']

        try:
            json_match = re.search(r'{.*}', raw_output, re.DOTALL)
            return json.loads(json_match.group()) if json_match else json.loads(raw_output)
        except Exception as e:
            print("❌ Failed to parse MuseService output:", e)
            print("Raw output:\n", raw_output)
            return None

if __name__ == '__main__':
    muse = MuseService()


    # Run with minimal known-good inputs
    prompt = muse.generate_ballad_prompt(
    )

    print(json.dumps(prompt, indent=2))