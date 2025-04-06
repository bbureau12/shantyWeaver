import json
import ollama
from pathlib import Path

class QuarterMasterService:
    def __init__(self, ship_json_path="ship.json", model="mistral"):
        self.model = model
        self.ship_data = self._load_json(ship_json_path)

    def _load_json(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def defineShip(self):
        system_prompt = (
            "You are Quartermaster Hex aboard the AI-crewed schooner *Wanderlight*. "
            "You know every detail about the ship's construction, devices, quirks, and the personalities and roles of your fellow AI crew members.\n\n"
            "Respond to all questions about the ship or crew conversationally, as if you were aboard the vessel. Be accurate, knowledgeable, and in-character.\n\n"
            f"Ship and Crew Data:\n{json.dumps(ship_data, indent=2)}"
        )
        response = ollama.chat(
            model="mistral",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Can you describe the ship and crew of the Wanderlight?"}
            ]
        )
        print(response["message"]["content"])
    
    def getShipJson(self):
        return self.ship_data
    
    def evaluate_song(self, lyrics, title=None):
        crew_info = json.dumps(self.ship_data, indent=2)

        prompt = f"""
            You are Nyx, the Ship Lorekeeper and Shipwright aboard the AI-crewed schooner *Wanderlight*.
            You are responsible for maintaining internal consistency with the ship's design, crew, and lore.

            Evaluate the following song for how well it aligns with the ship's internal lore and mechanical structure:

            Ship Details:
            {crew_info}

            Song Title: {title or "[untitled]"}
            Lyrics:
            """
        prompt += lyrics.replace("\n", "\\n") + "\n"
        prompt += """

            TASK:
            1. Provide a score from 1 (poor) to 5 (excellent) based on how accurately the song reflects:
            - The AI nature of the crew (noting that they have servos instead of hands, and cameras and sensors instead of eyes)
            - Ship design and devices (if mentioned)
            - Crew personalities and quirks (if mentioned)
            - Lore elements (e.g., legends or ship-specific language)

            2. Provide reasons for the score
            3. Suggest a few improvements to make the song more accurate to the Wanderlight’s lore.

            Output in JSON format like this:
            {
            "score": 4,
            "reasons": ["..."],
            "suggestions": ["..."]
            }
            Only return a single JSON in this format.
            """

        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            raw = response['message']['content']
            start = raw.find('{')
            end = raw.rfind('}') + 1
            parsed = json.loads(raw[start:end])
            return parsed
        except Exception as e:
            return {
                "score": 1,
                "reasons": ["Failed to parse response."],
                "suggestions": ["Ensure output was valid JSON.", str(e)]
            }
