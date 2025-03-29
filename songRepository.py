import json
import faiss
import random
from sentence_transformers import SentenceTransformer

class ShantyRepository:
    def __init__(self, json_path="shanties.json"):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.songs = self._load_json(json_path)
        self.documents = [s["title"] + ": " + s["lines"] for s in self.songs]
        self.embeddings = self.model.encode(self.documents)
        self.index = faiss.IndexFlatL2(self.embeddings[0].shape[0])
        self.index.add(self.embeddings)

    def search_by_prompt(
        self,
        text: str,
        k: int = 3,
        tone: str = None,
        theme: str = None,
        structure: str = None,
        add_random: bool = False
    ):
        # Filter songs based on optional metadata
        filtered_songs = self.songs
        if tone:
            filtered_songs = [s for s in filtered_songs if s.get("tone", "").lower() == tone.lower()]
        if theme:
            filtered_songs = [s for s in filtered_songs if s.get("theme", "").lower() == theme.lower()]
        if structure:
            filtered_songs = [s for s in filtered_songs if s.get("structure", "").lower() == structure.lower()]

        if not filtered_songs:
            filtered_songs =  random.choices(self.songs, k)

        # Prepare documents to embed from filtered list
        docs = [s["title"] + ": " + s["lines"] for s in filtered_songs]
        embeddings = self.model.encode(docs)
        
        # Build temporary FAISS index for filtered data
        dim = embeddings[0].shape[0]
        temp_index = faiss.IndexFlatL2(dim)
        temp_index.add(embeddings)

        query_vec = self.model.encode([text])
        _, idxs = temp_index.search(query_vec, min(k, len(filtered_songs)))

        # Gather top results
        top_results = [filtered_songs[i] for i in idxs[0]]

# Determine how many random songs to add
        random_count = k - len(top_results) if len(top_results) < k else 1

        # Add random non-duplicate(s) from filtered set, fallback to full set if needed
        if add_random:
            candidates = [s for s in filtered_songs if s not in top_results]
            if len(candidates) < random_count:
                # Fallback to all songs
                candidates = [s for s in self.songs if s not in top_results]

            if candidates:
                extras = random.sample(candidates, k=min(random_count, len(candidates)))
                top_results.extend(extras)

        return top_results

    def get_random_songs(self, times: int = 1):
        return random.choices(self.songs, k=times)
    
    def _load_json(self, path):
        with open(path, 'r') as f:
            return json.load(f)["songs"]