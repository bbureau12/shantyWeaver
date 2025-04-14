import json
import faiss
import random
from functools import lru_cache
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class ShantyRepository:
    def __init__(self, json_path="shanties.json"):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.songs = self._load_json(json_path)
        self.documents = [s["title"] + ": " + s["lyrics"] for s in self.songs]
        self.embeddings = self.model.encode(self.documents, normalize_embeddings=True)
        self.index = faiss.IndexFlatL2(self.embeddings[0].shape[0])
        self.index.add(self.embeddings)

        # Build vocabulary from metadata
        self.vocab = self._build_vocab()
        self.vocab_embeddings = self.model.encode(self.vocab, normalize_embeddings=True)

    def search_by_prompt(self, text, k=3, tone=None, theme=None, structure=None, add_random=True, threshold=0.8):
        filtered_songs = self._search_by_any_match(self.songs, tone=tone, theme=theme, structure=structure)
        if not filtered_songs:
            filtered_songs = random.choices(self.songs, k=k)

        docs = [s["title"] + ": " + s["lyrics"] for s in filtered_songs]
        embeddings = self.model.encode(docs, normalize_embeddings=True)
        query_vec = self.model.encode([text], normalize_embeddings=True)

        similarities = cosine_similarity(query_vec, embeddings)[0]
        top_k_indices = similarities.argsort()[-k:][::-1]
        top_results = [filtered_songs[i] for i in top_k_indices]

        random_count = k - len(top_results) if len(top_results) < k else 1
        if add_random:
            candidates = [s for s in self.songs if s not in top_results]
            if candidates:
                extras = random.sample(candidates, k=min(random_count, len(candidates)))
                top_results.extend(extras)

        return top_results

    def _build_vocab(self):
        vocab = set()
        for song in self.songs:
            for key in ["tone", "tags", "theme", "structure"]:
                val = song.get(key)
                if isinstance(val, str):
                    vocab.add(val.lower())
                elif isinstance(val, list):
                    vocab.update(v.lower() for v in val if isinstance(v, str))
        return list(vocab)

    @lru_cache(maxsize=128)
    def _expand_semantically_cached(self, term):
        return tuple(self._expand_semantically(term))

    def _expand_semantically(self, term, top_k=5, threshold=0.5):
        query_embedding = self.model.encode([term], normalize_embeddings=True)
        similarities = cosine_similarity(query_embedding, self.vocab_embeddings)[0]
        results = [
            self.vocab[i]
            for i, score in enumerate(similarities)
            if score >= threshold and self.vocab[i] != term
        ]
        return results[:top_k]

    def _search_by_any_match(self, songs, tone=None, theme=None, structure=None):
        tone_matches = self._fuzzy_filter(songs, "tone", tone) if tone else []
        tag_matches = self._fuzzy_filter(songs, "tags", tone) if tone else []
        theme_matches = self._fuzzy_filter(songs, "theme", theme) if theme else []
        structure_matches = self._fuzzy_filter(songs, "structure", structure) if structure else []

        combined_results = tone_matches + tag_matches + theme_matches + structure_matches
        return self._dedupe(combined_results) if combined_results else songs

    def _fuzzy_filter(self, songs, key, values):
        if not values:
            return songs

        raw_terms = [v.strip().lower() for v in values.split(",") if v.strip()]
        terms = set()
        for term in raw_terms:
            terms.add(term)
            terms.update(self._expand_semantically_cached(term))

        filtered = []
        for song in songs:
            field = song.get(key, "")
            if isinstance(field, str):
                if any(term in field.lower() for term in terms):
                    filtered.append(song)
            elif isinstance(field, list):
                if any(term in str(item).lower() for term in terms for item in field):
                    filtered.append(song)
        return filtered

    def _dedupe(self, songs):
        seen = set()
        unique = []
        for song in songs:
            hashable_items = tuple(
                (k, tuple(v) if isinstance(v, list) else v)
                for k, v in sorted(song.items())
            )
            if hashable_items not in seen:
                seen.add(hashable_items)
                unique.append(song)
        return unique

    def get_random_songs(self, times=1):
        return random.choices(self.songs, k=times)

    def _load_json(self, path):
        with open(path, 'r', encoding="utf-8") as f:
            return json.load(f)["songs"]