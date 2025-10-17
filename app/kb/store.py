import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List

from ..processors.router import Document


@dataclass
class KBEntry:
    id: str
    source: str
    content: str
    metadata: Dict[str, str]


class KnowledgeBase:
    def __init__(self, path: str):
        self.path = Path(path)
        self.documents: List[KBEntry] = []

    def add_documents(self, docs: List[Document]) -> None:
        for d in docs:
            self.documents.append(KBEntry(d.id, d.source, d.content, d.metadata))

    def persist(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as w:
            for d in self.documents:
                w.write(json.dumps(asdict(d), ensure_ascii=False) + "\n")

    def load(self) -> None:
        self.documents.clear()
        if not self.path.exists():
            return
        with self.path.open("r", encoding="utf-8", errors="ignore") as r:
            for line in r:
                obj = json.loads(line)
                self.documents.append(KBEntry(**obj))





