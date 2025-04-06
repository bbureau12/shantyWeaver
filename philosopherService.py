import os
import json
import re
from jinja2 import Template
from shipsCarpenterService import QuarterMasterService
import ollama

class EvaluationAgentService:
    def __init__(self, evaluator_path="evaluators", model="mistral"):
        self.quarterMasterService = QuarterMasterService()
        self.evaluator_path = evaluator_path
        self.model = model
        self.evaluators = self._load_evaluators()

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

    def evaluate(self, song):
        results = []

        for evaluator in self.evaluators:
            # Inject context based on dependencies
            evaluator["context"] = []
            for dep in evaluator.get("dependencies", []):
                evaluator["context"].append(self.resolve_dependency(dep))

            template = Template(evaluator["template"])
            prompt = template.render(
                agent=evaluator.get("agent", "Evaluator"),
                song_title=song.get("title", "Untitled"),
                lyrics=song.get("lines", "")
            )

            system_prompt = self.build_system_prompt(evaluator)

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

            results.append({
                "evaluator": evaluator.get("name"),
                "description": evaluator.get("description"),
                "score": result
            })

        return results

    def build_system_prompt(self, evaluator) -> str:
        name = evaluator.get("name", "Evaluator")
        desc = evaluator.get("description", "You evaluate songs.")
        intro = f"You are {name}. {desc}\n\n"

        context_sections = ""
        for c in evaluator.get("context", []):
            label = c.get("title", "Context")
            content = c.get("content", "")
            body = json.dumps(content, indent=2) if isinstance(content, (dict, list)) else str(content)
            context_sections += f"{label}:\n{body}\n\n"

        return intro + context_sections + "Only respond with a JSON object."
