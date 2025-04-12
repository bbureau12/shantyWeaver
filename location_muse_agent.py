import json
import ollama
from pathlib import Path

class LocationMuse:
    def __init__(self, locations_path='locations.json', model='mistral'):
        self.model = model
        with open(locations_path, 'r', encoding='utf-8') as f:
            self.locations = json.load(f)
        self.location_names = {loc["name"] for loc in self.locations}
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self):
        return (
            "You are LocationMuse, the poetic heart of the ship Wanderlight.\n"
            "You receive a list of known locations. Choose one only if it feels especially poetic at this moment.\n"
            "Draw inspiration from its lore, sounds, wildlife, or visible landmarks — but only if they truly stand out.\n"
            "If nothing stirs your muse, respond with `null`.\n\n"
            "You MUST only choose from the exact location names given — do not modify or invent new names.\n\n"
            "🎇 When inspired, respond with:\n"
            "{\n"
            "  \"location\": \"exact name from input\",\n"
            "  \"spark\": {\n"
            "    \"inspiration\": \"A poetic line or vivid image derived from the place. You may (optionally) reference sounds, landmarks, or wildlife.\"\n"
            "  }\n"
            "}\n\n"
            "🕯️ If no spark arises, simply respond with `null`.\n"
            "⚠️ No commentary, no prose, no extra output. Just the JSON or null."
        )

    def choose_location_and_spark(self):
        location_names = [loc["name"] for loc in self.locations]
        location_summary = "\n".join(f"- {name}" for name in location_names)

        system_prompt = (
            "You are LocationMuse, the poetic mind of the Wanderlight.\n"
            "From the following list of valid locations:\n"
            f"{location_summary}\n\n"
            "You must ONLY choose from the exact names above. Do not invent or modify them.\n\n"
            "If one of these locations evokes a poetic image, return:\n"
            "{\n"
            "  \"location\": \"name from list\",\n"
            "  \"spark\": {\n"
            "    \"inspiration\": \"poetic line or imagery\"\n",
            "  }\n"
            "}\n\n"
            "If none of the locations feel meaningful or poetic, return `null`.\n"
            "Do not list or describe locations. Do not explain your choice. Just return the valid JSON."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Which of the locations above inspires you now?"}
        ]

        response = ollama.chat(model=self.model, messages=messages)
        content = response['message']['content'].strip()

        try:
            if content.lower() == "null":
                return None
            result = json.loads(content)
            if result["location"] not in location_names:
                raise ValueError(f"Invalid location: {result['location']}")
            return result
        except Exception as e:
            print("❌ Failed to parse LocationMuse output:", e)
            print("Raw output:", content)
            return None



if __name__ == '__main__':
    muse = LocationMuse()
    result = muse.choose_location_and_spark()
    if result:
        print("\n🎇 Location Spark:")
        print(json.dumps(result, indent=2))
    else:
        print("🕯️ No location spark this time.")
