#!/usr/bin/env python3
"""Semantic search for Obsidian vaults using sentence-transformers and FAISS."""

import os
import sys
import yaml
import json
import pathlib
import re
import argparse
import hashlib
from datetime import datetime

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


class SemanticSearch:
    def __init__(self, vault_path, model_name="paraphrase-multilingual-MiniLM-L12-v2"):
        self.vault_path = pathlib.Path(vault_path).resolve()
        self.index_dir = self.vault_path / ".obsidian" / "ai_index"
        self.index_path = self.index_dir / "index.faiss"
        self.mapping_path = self.index_dir / "mapping.yaml"
        self.hashes_path = self.index_dir / "hashes.yaml"
        self.model = None
        self.model_name = model_name

    def _load_model(self):
        if self.model is None:
            self.model = SentenceTransformer(self.model_name)

    def _parse_frontmatter(self, content):
        """Extract frontmatter and body from markdown content."""
        if content.startswith("---"):
            end = content.find("---", 3)
            if end != -1:
                try:
                    fm = yaml.safe_load(content[3:end])
                    body = content[end + 3:].strip()
                    return fm or {}, body
                except yaml.YAMLError:
                    pass
        return {}, content

    def _get_notes(self):
        """Get all markdown files in the vault, excluding .obsidian."""
        notes = []
        for p in self.vault_path.rglob("*.md"):
            rel = p.relative_to(self.vault_path)
            if str(rel).startswith(".obsidian"):
                continue
            notes.append(p)
        return sorted(notes)

    def _file_hash(self, path):
        """Fast hash of file modification time + size."""
        stat = path.stat()
        return hashlib.md5(f"{stat.st_mtime}:{stat.st_size}".encode()).hexdigest()

    def build(self):
        """Build full search index."""
        self._load_model()
        self.index_dir.mkdir(parents=True, exist_ok=True)

        notes = self._get_notes()
        if not notes:
            print("No markdown files found in vault.")
            return

        texts, mapping, hashes = [], [], {}
        for note in tqdm(notes, desc="Indexing notes"):
            content = note.read_text(encoding="utf-8", errors="ignore")
            fm, body = self._parse_frontmatter(content)

            title = fm.get("title", note.stem)
            tags = fm.get("tags", [])
            aliases = fm.get("aliases", [])
            tag_str = " ".join(f"#{t}" for t in tags) if isinstance(tags, list) else ""
            alias_str = " ".join(aliases) if isinstance(aliases, list) else ""

            # Build searchable text: title + aliases + tags + body (truncated)
            text = f"Title: {title}\n{alias_str}\n{tag_str}\n{body[:2000]}"
            texts.append(text)

            rel_path = str(note.relative_to(self.vault_path))
            mapping.append(rel_path)
            hashes[rel_path] = self._file_hash(note)

        embeddings = self.model.encode(texts, show_progress_bar=True, batch_size=32)
        embeddings = np.array(embeddings).astype("float32")

        index = faiss.IndexFlatIP(embeddings.shape[1])  # Inner product (cosine after normalize)
        faiss.normalize_L2(embeddings)
        index.add(embeddings)

        faiss.write_index(index, str(self.index_path))
        with open(self.mapping_path, "w", encoding="utf-8") as f:
            yaml.dump(mapping, f, allow_unicode=True)
        with open(self.hashes_path, "w", encoding="utf-8") as f:
            yaml.dump(hashes, f, allow_unicode=True)

        print(f"Indexed {len(notes)} notes.")

    def update(self):
        """Incremental update: only re-index new or modified files."""
        if not self.index_path.exists():
            print("No existing index found. Running full build.")
            return self.build()

        self._load_model()

        # Load existing data
        index = faiss.read_index(str(self.index_path))
        with open(self.mapping_path, "r", encoding="utf-8") as f:
            mapping = yaml.safe_load(f) or []
        with open(self.hashes_path, "r", encoding="utf-8") as f:
            old_hashes = yaml.safe_load(f) or {}

        notes = self._get_notes()
        current_paths = set()
        new_notes = []

        for note in notes:
            rel = str(note.relative_to(self.vault_path))
            current_paths.add(rel)
            current_hash = self._file_hash(note)
            if rel not in old_hashes or old_hashes[rel] != current_hash:
                new_notes.append(note)

        if not new_notes:
            removed = set(mapping) - current_paths
            if not removed:
                print("Index is up to date.")
                return
            # If only removals, rebuild
            print(f"{len(removed)} notes removed. Rebuilding index.")
            return self.build()

        print(f"{len(new_notes)} notes to update. Rebuilding index.")
        return self.build()

    def ask(self, query, top_k=5, format_output="text"):
        """Query the semantic index."""
        if not self.index_path.exists():
            print("No index found. Run with --action build first.")
            sys.exit(1)

        self._load_model()
        index = faiss.read_index(str(self.index_path))
        with open(self.mapping_path, "r", encoding="utf-8") as f:
            mapping = yaml.safe_load(f)

        q_vec = self.model.encode([query])
        q_vec = np.array(q_vec).astype("float32")
        faiss.normalize_L2(q_vec)

        D, I = index.search(q_vec, min(top_k, len(mapping)))

        results = []
        for score, idx in zip(D[0], I[0]):
            if idx == -1:
                continue
            results.append({"path": mapping[idx], "score": float(score)})

        if format_output == "json":
            print(json.dumps(results, indent=2))
        else:
            print(f"Top {len(results)} results for: \"{query}\"\n")
            for i, r in enumerate(results, 1):
                print(f"  {i}. [[{pathlib.Path(r['path']).stem}]] ({r['path']}) — score: {r['score']:.3f}")

        return results


def main():
    parser = argparse.ArgumentParser(description="Semantic search for Obsidian vaults")
    parser.add_argument("--vault", required=True, help="Path to Obsidian vault")
    parser.add_argument("--action", required=True, choices=["build", "update", "ask"],
                        help="Action: build index, update index, or ask query")
    parser.add_argument("--query", help="Search query (for ask action)")
    parser.add_argument("--top", type=int, default=5, help="Number of results (default: 5)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--model", default="paraphrase-multilingual-MiniLM-L12-v2",
                        help="Sentence transformer model name")
    args = parser.parse_args()

    engine = SemanticSearch(args.vault, model_name=args.model)

    if args.action == "build":
        engine.build()
    elif args.action == "update":
        engine.update()
    elif args.action == "ask":
        if not args.query:
            parser.error("--query is required for ask action")
        engine.ask(args.query, top_k=args.top, format_output=args.format)


if __name__ == "__main__":
    main()
