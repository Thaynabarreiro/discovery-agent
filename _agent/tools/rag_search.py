from __future__ import annotations

from pathlib import Path
from typing import Any

from rich.console import Console


class RagSearch:
    def __init__(self, knowledge_dir: str = "knowledge_base", persist_dir: str = ".chromadb") -> None:
        self.knowledge_dir = Path(knowledge_dir)
        self.persist_dir = persist_dir
        self.console = Console()
        self._collection: Any | None = None
        self._ready = False
        self._init_chroma()

    def _init_chroma(self) -> None:
        try:
            import chromadb
            from sentence_transformers import SentenceTransformer
        except Exception as exc:
            self.console.print(f"[yellow]RAG disabled: missing dependency ({exc}).[/yellow]")
            return

        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        client = chromadb.PersistentClient(path=self.persist_dir)
        self._collection = client.get_or_create_collection("case_knowledge")
        self._index_knowledge_base()
        self._ready = True

    def _index_knowledge_base(self) -> None:
        files = []
        if self.knowledge_dir.exists():
            files = sorted([*self.knowledge_dir.glob("*.txt"), *self.knowledge_dir.glob("*.pdf")])
        if not files:
            self.console.print("[yellow]knowledge_base/ is empty. Agents will continue without RAG cases.[/yellow]")
            return

        existing = set(self._collection.get(include=[])["ids"])
        for path in files:
            text = self._read_file(path)
            for idx, chunk in enumerate(self._chunk(text)):
                doc_id = f"{path.name}:{idx}"
                if doc_id in existing:
                    continue
                embedding = self.model.encode(chunk).tolist()
                self._collection.add(
                    ids=[doc_id],
                    documents=[chunk],
                    embeddings=[embedding],
                    metadatas=[{"source": str(path), "chunk": idx}],
                )

    def _read_file(self, path: Path) -> str:
        if path.suffix.lower() == ".pdf":
            try:
                from pypdf import PdfReader
            except Exception:
                return ""
            reader = PdfReader(str(path))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        return path.read_text(encoding="utf-8", errors="ignore")

    def _chunk(self, text: str, size: int = 1200, overlap: int = 150) -> list[str]:
        clean = " ".join(text.split())
        if not clean:
            return []
        chunks = []
        start = 0
        while start < len(clean):
            chunks.append(clean[start:start + size])
            start += size - overlap
        return chunks

    def search(self, query: str, n_results: int = 3) -> list[dict]:
        if not self._ready or not self._collection:
            return []
        embedding = self.model.encode(query).tolist()
        result = self._collection.query(query_embeddings=[embedding], n_results=n_results)
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0] if result.get("distances") else [None] * len(documents)
        return [
            {"text": doc, "metadata": meta, "distance": distance}
            for doc, meta, distance in zip(documents, metadatas, distances)
        ]


def search(query: str, n_results: int = 3) -> list[dict]:
    return RagSearch().search(query, n_results=n_results)
