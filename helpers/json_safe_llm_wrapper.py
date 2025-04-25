import json
import re
import datetime


class JsonSafeLLMWrapper:
    def __init__(self, fields_to_escape=None, log_failures_to="./log/json_parse_failures.log"):
        self.fields_to_escape = fields_to_escape if fields_to_escape else []
        self.log_path = log_failures_to

    def _strip_preamble(self, text):
        if text.lower().startswith("here's") or "===" in text:
            return text.split("===")[-1]
        return text

    def _fix_trailing_commas(self, text):
        text = re.sub(r',\s*}', '}', text)
        text = re.sub(r',\s*]', ']', text)
        return text

    def _quote_unquoted_keys(self, text):
        return re.sub(r'(?<=\{|\n)\s*([a-zA-Z0-9_]+)\s*:', r'"\1":', text)

    def _escape_field(self, text, field_name):
        # Escape newlines and quotes in specified fields
        return re.sub(
            rf'"{field_name}"\s*:\s*"([\s\S]*?)"',
            lambda m: f'"{field_name}": "' + m.group(1).replace('"', '\\"').replace('\n', '\\n').replace('\r', '').replace('\t', '    ').replace('\u2028', ' ') + '"',
            text,
            flags=re.DOTALL
        )

    def _extract_json_block(self, text):
        match = re.search(r'{[\s\S]*}', text)
        return match.group(0) if match else text

    def _log_failure(self, original_text, error):
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n--- JSON Parse Failure [{datetime.datetime.now()}] ---\n")
            f.write(f"Error: {error}\n")
            f.write(f"Output:\n{original_text}\n")

    def try_parse(self, raw_output):
        original = raw_output
        try:
            text = self._strip_preamble(raw_output)
            text = self._extract_json_block(text)
            text = self._fix_trailing_commas(text)
            text = self._quote_unquoted_keys(text)
            for field in self.fields_to_escape:
                text = self._escape_field(text, field)

            return json.loads(text)

        except Exception as e:
            self._log_failure(original, e)
            raise ValueError("Failed to safely parse JSON. Logged to file.")