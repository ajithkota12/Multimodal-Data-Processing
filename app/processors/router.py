from dataclasses import dataclass
from typing import List, Dict
from pathlib import Path

from .text_processors import extract_text_from_path
from .vision_ocr import extract_text_from_image
from .speech_to_text import transcribe_audio_or_video, transcribe_youtube


@dataclass
class Document:
    id: str
    source: str
    content: str
    metadata: Dict[str, str]


def _process_single(item: str) -> List[Document]:
    p = Path(item)
    # URL handling (YouTube)
    if item.startswith("http") and "youtube" in item.lower():
        text = transcribe_youtube(item)
        return [Document(id=item, source=item, content=text, metadata={"type": "youtube"})]

    suffix = p.suffix.lower()
    if suffix in {".png", ".jpg", ".jpeg"}:
        text = extract_text_from_image(str(p))
        return [Document(id=str(p), source=str(p), content=text, metadata={"type": "image"})]
    if suffix in {".mp3", ".mp4", ".wav", ".m4a"}:
        text = transcribe_audio_or_video(str(p))
        return [Document(id=str(p), source=str(p), content=text, metadata={"type": "audio_video"})]

    # Default to text-like
    text = extract_text_from_path(str(p))
    return [Document(id=str(p), source=str(p), content=text, metadata={"type": "text"})]


def process_inputs(items: List[str]) -> List[Document]:
    docs: List[Document] = []
    for item in items:
        try:
            docs.extend(_process_single(item))
        except Exception as exc:  # only log; keep going
            docs.append(Document(id=item, source=item, content=f"[INGEST ERROR] {exc}", metadata={"type": "error"}))
    return docs


