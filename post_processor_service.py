import os
import json
import re
import time
import random
from jinja2 import Template
from requirementsService import DependencyService
import ollama

class PostProcessorService:
    def __init__(self, processor_path="post-processors", model="llama3"):
        self.processor_path = processor_path
        self.model = model
        self.processors = self._load_processors()
        self.dependencyService = DependencyService()

    def _load_processors(self):
        processors = []
        for fname in os.listdir(self.processor_path):
            if fname.endswith(".json"):
                with open(os.path.join(self.processor_path, fname), 'r', encoding='utf-8') as f:
                    processor = json.load(f)
                    processor.setdefault("dependencies", [])
                    processors.append(processor)
        return sorted(processors, key=lambda x: x.get("priority", 100))

    def run(self, song, force=False):
        """Applies post-processors to the song and mutates it directly."""
        results = []

        for processor in self.processors:
            metric = processor.get("metric", processor.get("name", "unknown_metric"))
            if not force and metric in song:
                print(f"⏭️ Skipping post-processor '{processor['name']}' — already applied.")
                continue

            # Inject only the needed fields
            injected_song = {}
            injected_facts = {}
            for dep in processor.get("dependencies", []):
                if dep in song:
                    injected_song[dep] = song[dep]
                else:
                    fact = self.dependencyService.resolve(dep)
                    if fact:
                        injected_facts[dep.replace(':','_')] = fact

            template_context = {**injected_song, **injected_facts}

            template = Template("\n".join(processor["template"]))
            prompt = template.render(**template_context)

            system_prompt = f"You are {processor.get('name', 'PostProcessor')}\n{processor.get('description', '')}\nReturn a JSON object or plain string depending on type."

            result = self._try_run_processor(system_prompt, prompt, processor)
            result = self._apply_processor_result(song, processor, result)

            results.append({
                "processor": processor.get("name"),
                "result": result
            })

        return song

    def _try_run_processor(self, system_prompt, prompt, processor, retries=3):
        model = processor.get("model", self.model)
        for attempt in range(1, retries + 1):
            try:
                response = ollama.chat(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ]
                )
                return response['message']['content']
            except Exception as e:
                print(f"⚠️ Error on attempt {attempt}: {e}")
                if attempt < retries:
                    time.sleep(random.uniform(0.5, 1.5))
        return ""

    def _apply_processor_result(self, song, processor, raw_output):
        """Processes the raw output and applies it to the song based on processor type."""
        p_type = processor.get("type", "addendum")
        metric = processor.get("metric", processor.get("name", "unknown_metric"))

        try:
            if p_type == "addendum":
                json_match = re.search(r'{.*}', raw_output, re.DOTALL)
                result = json.loads(json_match.group()) if json_match else {}
                for key, value in result.items():
                    song[key] = value
                song.setdefault("metrics_applied", []).append(metric)
                return result


            elif p_type == "lyrics":
                result_text = raw_output.strip().strip('"')
                if len(result_text) >= len(song.get("lyrics", "")) // 2:
                    song["lyrics"] = result_text
                    song[metric] = True
                    return {"lyrics_updated": True, "new_lyrics": result_text}
                else:
                    print(f"⚠️ Skipping lyrics update — too short from '{processor['name']}'")
                    return {"lyrics_updated": False, "reason": "Lyrics too short or invalid", "raw": result_text}

            else:
                return {"error": f"Unknown processor type: {p_type}"}

        except Exception as e:
            return {"error": f"Failed to parse: {e}", "raw": raw_output}
