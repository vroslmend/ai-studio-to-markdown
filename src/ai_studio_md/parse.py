"""Turn AI Studio export JSON into plain objects the renderer can consume.

Kept deliberately free of any Markdown concerns: everything here describes what
was *in* the export, not how it should look.
"""

from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import parse_qs, urlparse

DRIVE_URL = "https://drive.google.com/file/d/{}/view"

ATTACHMENT_KEYS = {"driveImage": "image", "driveDocument": "document"}


@dataclass
class Attachment:
    kind: str
    drive_id: str

    @property
    def url(self):
        return DRIVE_URL.format(self.drive_id)


@dataclass
class Source:
    uri: str
    footnote: int = None


@dataclass
class Turn:
    role: str
    text: str = ""
    timestamp: datetime = None
    is_thought: bool = False
    token_count: int = 0
    attachments: list = field(default_factory=list)
    sources: list = field(default_factory=list)


@dataclass
class Conversation:
    turns: list = field(default_factory=list)
    model: str = ""
    temperature: object = None
    top_p: object = None
    top_k: object = None
    thinking_level: str = ""
    system_instruction: str = ""

    @property
    def total_tokens(self):
        return sum(t.token_count for t in self.turns)


def _parse_time(raw):
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def _text_of(chunk):
    if chunk.get("text"):
        return chunk["text"]
    return "".join(p.get("text", "") for p in chunk.get("parts", []))


def _attachments_of(chunk):
    return [
        Attachment(kind=kind, drive_id=chunk[key].get("id", ""))
        for key, kind in ATTACHMENT_KEYS.items()
        if isinstance(chunk.get(key), dict)
    ]


def _unwrap_redirect(uri):
    """Grounding URIs arrive wrapped in a google.com/url?q= redirect."""
    if not uri.startswith("https://www.google.com/url?"):
        return uri
    inner = parse_qs(urlparse(uri).query).get("q", [""])[0]
    return inner or uri


def _sources_of(chunk):
    sources = [
        Source(uri=c["uri"])
        for c in chunk.get("citations", [])
        if isinstance(c, dict) and c.get("uri")
    ]

    # The same footnote repeats once per character offset it supports.
    seen = set()
    for segment in chunk.get("grounding", {}).get("corroborationSegments", []):
        uri = _unwrap_redirect(segment.get("uri", ""))
        note = segment.get("footnoteNumber")
        if not uri or (note, uri) in seen:
            continue
        seen.add((note, uri))
        sources.append(Source(uri=uri, footnote=note))

    return sources


def _system_instruction(data):
    raw = data.get("systemInstruction")
    if isinstance(raw, str):
        return raw
    if isinstance(raw, dict):
        return "".join(p.get("text", "") for p in raw.get("parts", []))
    return ""


def parse_conversation(data):
    settings = data.get("runSettings", {})

    # Drive auto-save uses chunkedPrompt.chunks; API payloads use contents.
    chunks = data.get("chunkedPrompt", {}).get("chunks") or data.get("contents", [])

    turns = [
        Turn(
            role=chunk.get("role", ""),
            text=_text_of(chunk),
            timestamp=_parse_time(chunk.get("createTime")),
            is_thought=bool(chunk.get("isThought", False)),
            token_count=chunk.get("tokenCount", 0) or 0,
            attachments=_attachments_of(chunk),
            sources=_sources_of(chunk),
        )
        for chunk in chunks
    ]

    return Conversation(
        turns=turns,
        model=settings.get("model", ""),
        temperature=settings.get("temperature"),
        top_p=settings.get("topP"),
        top_k=settings.get("topK"),
        thinking_level=settings.get("thinkingLevel", ""),
        system_instruction=_system_instruction(data),
    )
