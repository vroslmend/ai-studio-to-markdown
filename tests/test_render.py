from datetime import datetime, timezone

from ai_studio_md.parse import Attachment, Conversation, Source, Turn
from ai_studio_md.render import render_markdown


def test_header_carries_model_and_temperature():
    conv = Conversation(model="models/gemini-3.1-pro-preview", temperature=1.0)

    out = render_markdown(conv)

    assert "`models/gemini-3.1-pro-preview`" in out
    assert "`1.0`" in out


def test_header_carries_the_settings_the_old_extractor_discarded():
    conv = Conversation(
        model="m",
        top_p=0.95,
        top_k=64,
        thinking_level="THINKING_HIGH",
        turns=[Turn(role="user", text="hi", token_count=42)],
    )

    out = render_markdown(conv)

    assert "0.95" in out
    assert "64" in out
    assert "THINKING_HIGH" in out
    assert "42" in out


def test_every_line_of_a_multiline_system_instruction_is_quoted():
    """Regression: the old renderer quoted only the first line."""
    conv = Conversation(system_instruction="Line one\nLine two\nLine three")

    out = render_markdown(conv)

    assert "> Line one" in out
    assert "> Line two" in out
    assert "> Line three" in out


def test_blank_lines_inside_a_system_instruction_stay_inside_the_quote():
    conv = Conversation(system_instruction="Para one\n\nPara two")

    out = render_markdown(conv)

    assert "> Para one\n>\n> Para two" in out


def test_no_system_instruction_section_when_there_is_none():
    out = render_markdown(Conversation(system_instruction="   "))

    assert "System Instructions" not in out


def test_user_and_model_turns_get_readable_role_headings():
    conv = Conversation(turns=[Turn(role="user", text="q"), Turn(role="model", text="a")])

    out = render_markdown(conv)

    assert "### User" in out
    assert "### AI" in out


def test_thoughts_are_omitted_by_default():
    conv = Conversation(turns=[Turn(role="model", text="secret reasoning", is_thought=True)])

    out = render_markdown(conv)

    assert "secret reasoning" not in out


def test_thoughts_are_collapsed_into_details_when_requested():
    conv = Conversation(turns=[Turn(role="model", text="secret reasoning", is_thought=True)])

    out = render_markdown(conv, keep_thoughts=True)

    assert "<details>" in out
    assert "secret reasoning" in out
    assert "</details>" in out


def test_attachments_carry_no_drive_pointer_by_default():
    """Output is shareable without leaking private Drive file IDs."""
    conv = Conversation(
        turns=[Turn(role="user", attachments=[Attachment(kind="image", drive_id="img1")])]
    )

    out = render_markdown(conv)

    assert "[Image attachment]" in out
    assert "img1" not in out
    assert "drive.google.com" not in out


def test_drive_links_are_included_when_asked_for():
    conv = Conversation(
        turns=[Turn(role="user", attachments=[Attachment(kind="image", drive_id="img1")])]
    )

    out = render_markdown(conv, drive_links=True)

    assert "Image attachment" in out
    assert "https://drive.google.com/file/d/img1/view" in out


def test_a_turn_with_only_an_attachment_still_produces_output():
    """Regression: attachment-only turns used to vanish entirely."""
    conv = Conversation(
        turns=[
            Turn(role="user", text="look"),
            Turn(role="user", attachments=[Attachment(kind="document", drive_id="doc1")]),
            Turn(role="model", text="seen"),
        ]
    )

    out = render_markdown(conv)

    assert out.count("###") == 3
    assert "Document attachment" in out


def test_plain_citations_render_as_a_source_list():
    conv = Conversation(
        turns=[
            Turn(
                role="model",
                text="answer",
                sources=[Source(uri="https://example.com/cited-page")],
            )
        ]
    )

    out = render_markdown(conv)

    assert "Sources" in out
    assert "https://example.com/cited-page" in out


def test_grounded_sources_keep_their_footnote_numbers():
    conv = Conversation(
        turns=[
            Turn(
                role="model",
                text="answer",
                sources=[
                    Source(uri="https://example.com/a", footnote=1),
                    Source(uri="https://example.com/b", footnote=2),
                ],
            )
        ]
    )

    out = render_markdown(conv)

    assert "1." in out
    assert "2." in out


def test_timestamps_render_in_a_readable_form():
    conv = Conversation(
        turns=[
            Turn(role="user", text="hi", timestamp=datetime(2026, 5, 22, 17, 17, tzinfo=timezone.utc))
        ]
    )

    out = render_markdown(conv)

    assert "May 22, 2026" in out


def test_turns_with_nothing_in_them_are_skipped():
    conv = Conversation(turns=[Turn(role="user", text="   "), Turn(role="model", text="real")])

    out = render_markdown(conv)

    assert out.count("###") == 1
