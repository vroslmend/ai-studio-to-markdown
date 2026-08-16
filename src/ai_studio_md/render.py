"""Reads only the dataclasses from `parse`, never the raw export, so output
formatting can change without touching schema handling.
"""

ROLE_LABELS = {"user": "User", "model": "AI"}
ATTACHMENT_LABELS = {"image": "Image attachment", "document": "Document attachment"}


def _blockquote(text):
    """Blank lines keep a bare '>' so the quote does not split into two blocks."""
    return "\n".join(f"> {line}" if line.strip() else ">" for line in text.splitlines())


def _format_time(timestamp):
    if timestamp is None:
        return ""
    return timestamp.strftime("%b %d, %Y - %I:%M %p")


def _header(conv):
    facts = []
    if conv.model:
        facts.append(f"**Model:** `{conv.model}`")
    if conv.temperature is not None:
        facts.append(f"**Temperature:** `{conv.temperature}`")
    if conv.top_p is not None:
        facts.append(f"**Top-P:** `{conv.top_p}`")
    if conv.top_k is not None:
        facts.append(f"**Top-K:** `{conv.top_k}`")
    if conv.thinking_level:
        facts.append(f"**Thinking:** `{conv.thinking_level}`")
    if conv.total_tokens:
        facts.append(f"**Tokens:** `{conv.total_tokens:,}`")

    lines = ["# Google AI Studio Export", ""]
    if facts:
        lines += [" | ".join(facts), ""]
    lines.append("---")
    lines.append("")
    return lines


def _attachment_lines(turn, drive_links):
    """Marks where an attachment sat, without leaking its Drive id by default."""
    lines = []
    for attachment in turn.attachments:
        label = ATTACHMENT_LABELS.get(attachment.kind, "Attachment")
        if drive_links:
            lines.append(f"[{label} - Google Drive]({attachment.url})")
        else:
            lines.append(f"[{label}]")
    return lines


def _source_lines(turn):
    if not turn.sources:
        return []
    lines = ["", "**Sources:**", ""]
    for index, source in enumerate(turn.sources, start=1):
        number = source.footnote if source.footnote is not None else index
        lines.append(f"{number}. <{source.uri}>")
    return lines


def _render_turn(turn, keep_thoughts, drive_links):
    time_display = _format_time(turn.timestamp)
    suffix = f" _{time_display}_" if time_display else ""

    if turn.is_thought:
        if not keep_thoughts:
            return []
        return [
            "<details>",
            f"<summary>Model Thought Process{suffix}</summary>",
            "",
            turn.text.strip(),
            "",
            "</details>",
            "",
        ]

    body = _attachment_lines(turn, drive_links)
    if turn.text.strip():
        body.append(turn.text.strip())
    if not body:
        return []

    label = ROLE_LABELS.get(turn.role, turn.role.capitalize() or "Unknown")
    return [f"### {label}{suffix}", "", "\n\n".join(body)] + _source_lines(turn) + ["", "---", ""]


def render_markdown(conv, keep_thoughts=False, drive_links=False):
    lines = _header(conv)

    if conv.system_instruction.strip():
        lines += [
            "### System Instructions",
            "",
            _blockquote(conv.system_instruction.strip()),
            "",
            "---",
            "",
        ]

    for turn in conv.turns:
        lines += _render_turn(turn, keep_thoughts, drive_links)

    return "\n".join(lines)
