import datetime

class ContextManager:
    def __init__(self, max_history=10):
        self.histories = {}  # Maps a key like 'shanty_34' to a list of messages
        self.max_history = max_history

    def initialize(self, key, system_prompt):
        """Start a new history session if it doesn't exist."""
        if key not in self.histories:
            self.histories[key] = [{"role": "system", "content": system_prompt}]

    def add_user_message(self, key, content):
        self.histories[key].append({"role": "user", "content": content})
        self.trim_history(key)

    def add_assistant_message(self, key, content):
        self.histories[key].append({"role": "assistant", "content": content})
        self.trim_history(key)

    def get_history(self, key):
        return self.histories.get(key, [])

    def trim_history(self, key):
        if len(self.histories[key]) > self.max_history:
            # Keep system prompt and last (max_history - 1) messages
            system = self.histories[key][0:1]
            recent = self.histories[key][-self.max_history + 1:]
            self.histories[key] = system + recent
