import os
import tempfile
from typing import Optional, List
from urllib.parse import urlparse, parse_qs

from faster_whisper import WhisperModel
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from pytube import YouTube


_model_cache: Optional[WhisperModel] = None


def _get_model() -> WhisperModel:
    global _model_cache
    if _model_cache is None:
        _model_cache = WhisperModel("base", device="cpu")
    return _model_cache


def transcribe_audio_or_video(path: str) -> str:
    model = _get_model()
    segments, _ = model.transcribe(path)
    return " ".join(seg.text.strip() for seg in segments)


def _clean_youtube_url(url: str) -> str:
    """Return a canonical watch URL with only the v parameter."""
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    vid = None
    if "v" in qs and qs["v"]:
        vid = qs["v"][0]
    # support youtu.be short links
    if not vid and parsed.netloc in {"youtu.be"}:
        vid = parsed.path.strip("/")
    if not vid:
        # best-effort: last path segment
        vid = parsed.path.strip("/").split("/")[-1]
    return f"https://www.youtube.com/watch?v={vid}"


def _download_youtube_audio(url: str) -> str:
    yt = YouTube(_clean_youtube_url(url))
    stream = yt.streams.filter(only_audio=True).first()
    tmpdir = tempfile.mkdtemp()
    out_path = stream.download(output_path=tmpdir)
    return out_path


def transcribe_youtube(url: str) -> str:
    # Try official transcript first with robust parsing and fallbacks
    def _get_video_id(u: str) -> str:
        parsed = urlparse(u)
        qs = parse_qs(parsed.query)
        if "v" in qs and qs["v"]:
            return qs["v"][0]
        if parsed.netloc in {"youtu.be"}:
            return parsed.path.strip("/")
        return parsed.path.strip("/").split("/")[-1]

    vid = _get_video_id(url)
    try:
        # Prefer manually created 'en' if available, else any transcript, else auto-translated to 'en'
        transcripts = YouTubeTranscriptApi.list_transcripts(vid)
        try:
            t = transcripts.find_manually_created_transcript(["en"])  # type: ignore[attr-defined]
            fetched = t.fetch()
        except Exception:
            try:
                t = transcripts.find_transcript(["en"])  # type: ignore[attr-defined]
                fetched = t.fetch()
            except Exception:
                # try translation to English
                t = transcripts.find_transcript(transcripts._generated_transcripts.keys())  # type: ignore[attr-defined]
                fetched = t.translate("en").fetch()  # type: ignore[attr-defined]
        return " ".join(item.get("text", "") for item in fetched)
    except (TranscriptsDisabled, NoTranscriptFound, Exception):
        # Fallback: download audio and run STT
        path = _download_youtube_audio(url)
        return transcribe_audio_or_video(path)


