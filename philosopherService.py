import os
import json
import re
from jinja2 import Template
from shipsCarpenterService import QuarterMasterService
import ollama
from evaluation_logger_service import EvaluationLogger

class EvaluationAgentService:
    def __init__(self, evaluator_path="evaluators", model="mistral"):
        self.quarterMasterService = QuarterMasterService()
        self.evaluator_path = evaluator_path
        self.model = model
        self.evaluators = self._load_evaluators()
        self.logger = EvaluationLogger()


    def _load_evaluators(self):
        evaluators = []
        for fname in os.listdir(self.evaluator_path):
            if fname.endswith(".json"):
                with open(os.path.join(self.evaluator_path, fname), 'r', encoding='utf-8') as f:
                    evaluators.append(json.load(f))
        return evaluators

    def resolve_dependency(self, key):
        if key == "ship_data":
            return {
                "title": "Ship Data",
                "content": self.quarterMasterService.getShipJson()
            }
        elif key == "nautical_terminology":
            with open("data/nautical_terms.json", "r", encoding="utf-8") as f:
                return {
                    "title": "Nautical Terminology",
                    "content": json.load(f)
                }
        else:
            return {
                "title": key,
                "content": f"[Missing data for dependency: {key}]"
            }

    def evaluate(self, song, force=False):
        results = []
        existing_metrics = {grade["metric"] for grade in song.get("grades", [])}

        for evaluator in self.evaluators:
            metric = evaluator.get("metric", evaluator.get("name", "unknown_metric"))

            # 🚫 Skip if already graded and force is False
            if not force and metric in existing_metrics:
                print(f"🔁 Skipping evaluator '{evaluator['name']}' — metric '{metric}' already exists.")
                continue

            # Inject song context and dependencies
            evaluator["song"] = {
                "title": song.get("title", ""),
                "lyrics": song.get("lyrics", ""),
                "context": song.get("context", ""),
                "perspective": song.get("perspective", "")
            }
            evaluator["data"] = [self.resolve_dependency(dep) for dep in evaluator.get("dependencies", [])]

            # Render prompt
            template = Template("\n".join(evaluator["template"]))
            prompt = template.render(
                agent=evaluator.get("agent", "Evaluator"),
                song_title=song.get("title", "Untitled"),
                lyrics=song.get("lyrics", ""),
                context=song.get("context", "")
            )

            # Build system + user messages
            system_prompt = self.build_system_prompt(evaluator)
            print("=== SYSTEM PROMPT ===")
            print(system_prompt)
            print("=== USER PROMPT ===")
            print(prompt)

            # Call model
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )

            raw_output = response['message']['content']

            try:
                json_match = re.search(r'{.*}', raw_output, re.DOTALL)
                result = json.loads(json_match.group()) if json_match else {"error": "No JSON found"}
            except Exception as e:
                result = {"error": f"Failed to parse: {e}", "raw": raw_output}

            # Add to song's grades if it's valid
            self._apply_grade_to_song(song, evaluator, result)

            # Log the evaluation
            self.logger.log(
                song_title=song.get("title", "Untitled"),
                evaluator_name=evaluator.get("name", "Unknown Evaluator"),
                result=result,
                lyrics=song.get("lyrics", "")
            )

            results.append({
                "evaluator": evaluator.get("name"),
                "description": evaluator.get("description"),
                "score": result
            })

        return results

    def save_songbook(self, songs, path="shanty_songbook.json"):
        """Writes the updated list of songs back to the songbook file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(songs, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {len(songs)} songs to {path}")

    def _apply_grade_to_song(self, song, evaluator, result):
        """Adds a grade entry to the song based on evaluator output."""
        metric = evaluator.get("metric", evaluator.get("name", "unknown_metric"))
        if "score" not in result:
            return

        grade_entry = {
            "metric": metric,
            "weight": evaluator.get("weight", 1.0),
            "score": result.get("score"),
            "notes": result.get("notes", []),
            "evaluator": evaluator.get("name", "unknown")
        }
        song.setdefault("grades", []).append(grade_entry)


    def build_system_prompt(self, evaluator) -> str:
        name = evaluator.get("name", "Evaluator")
        desc = evaluator.get("description", "You evaluate songs.")
        intro = f"You are {name}. {desc}\n\n"

        # Get SONG first if it's been added
        song_data = evaluator.get("song", {})
        song_block = ""
        if song_data:
            song_block = "SONG:\n" + json.dumps(song_data, indent=2) + "\n\n"

        # Then append context blocks (like ship_data)
        context_sections = ""
        for c in evaluator.get("data", []):
            label = c.get("title", "Context")
            content = c.get("content", "")
            body = json.dumps(content, indent=2) if isinstance(content, (dict, list)) else str(content)
            context_sections += f"{label}:\n{body}\n\n"

        return intro + song_block + context_sections + "Only respond with a JSON object."