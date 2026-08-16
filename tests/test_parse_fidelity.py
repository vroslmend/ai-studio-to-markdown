"""Coverage for the export data the old extractor dropped on the floor.

Chunk shapes here mirror the ones observed in a real 352-chunk Drive export.
"""

from ai_studio_md.parse import parse_conversation


def _wrap(chunks):
    return {"runSettings": {}, "chunkedPrompt": {"chunks": chunks}}


def test_drive_image_chunk_becomes_a_turn_with_an_image_attachment():
    conv = parse_conversation(
        _wrap([{"driveImage": {"id": "1AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPp"}, "role": "user"}])
    )

    assert len(conv.turns) == 1
    attachment = conv.turns[0].attachments[0]
    assert attachment.kind == "image"
    assert attachment.drive_id == "1AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPp"


def test_drive_document_chunk_becomes_a_turn_with_a_document_attachment():
    conv = parse_conversation(
        _wrap([{"driveDocument": {"id": "1QqRrSsTtUuVvWwXxYyZz0011223344Aa"}, "role": "user"}])
    )

    assert conv.turns[0].attachments[0].kind == "document"


def test_attachment_exposes_a_drive_url():
    conv = parse_conversation(_wrap([{"driveImage": {"id": "abc123"}, "role": "user"}]))

    assert conv.turns[0].attachments[0].url == "https://drive.google.com/file/d/abc123/view"


def test_citations_become_sources_on_the_turn():
    conv = parse_conversation(
        _wrap(
            [
                {
                    "role": "model",
                    "text": "here you go",
                    "citations": [
                        {"uri": "https://example.com/first-source"},
                        {"uri": "https://example.org/second-source"},
                    ],
                }
            ]
        )
    )

    assert [s.uri for s in conv.turns[0].sources] == [
        "https://example.com/first-source",
        "https://example.org/second-source",
    ]


def test_grounding_segments_become_numbered_sources():
    conv = parse_conversation(
        _wrap(
            [
                {
                    "role": "model",
                    "text": "grounded answer",
                    "grounding": {
                        "corroborationSegments": [
                            {"index": 562, "uri": "https://example.com/a", "footnoteNumber": 1},
                            {"index": 683, "uri": "https://example.com/b", "footnoteNumber": 2},
                        ]
                    },
                }
            ]
        )
    )

    assert [(s.footnote, s.uri) for s in conv.turns[0].sources] == [
        (1, "https://example.com/a"),
        (2, "https://example.com/b"),
    ]


def test_grounding_segments_repeated_across_offsets_are_deduplicated():
    """The same footnote is re-emitted at every character offset it supports."""
    conv = parse_conversation(
        _wrap(
            [
                {
                    "role": "model",
                    "text": "grounded",
                    "grounding": {
                        "corroborationSegments": [
                            {"index": 562, "uri": "https://example.com/a", "footnoteNumber": 2},
                            {"index": 683, "uri": "https://example.com/a", "footnoteNumber": 2},
                            {"index": 900, "uri": "https://example.com/a", "footnoteNumber": 2},
                        ]
                    },
                }
            ]
        )
    )

    assert len(conv.turns[0].sources) == 1


def test_google_redirect_wrapper_is_unwrapped_to_the_inner_url():
    wrapped = (
        "https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com"
        "%2Fgrounding-api-redirect%2FAUZIYQE9W7jcPnZokzoU"
    )
    conv = parse_conversation(
        _wrap(
            [
                {
                    "role": "model",
                    "text": "x",
                    "grounding": {
                        "corroborationSegments": [
                            {"index": 1, "uri": wrapped, "footnoteNumber": 1}
                        ]
                    },
                }
            ]
        )
    )

    assert conv.turns[0].sources[0].uri == (
        "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE9W7jcPnZokzoU"
    )


def test_attachment_only_turns_survive_even_though_they_have_no_text():
    """The old extractor emitted nothing for these, so images vanished silently."""
    conv = parse_conversation(
        _wrap(
            [
                {"role": "user", "text": "look at this"},
                {"driveImage": {"id": "img1"}, "role": "user"},
                {"role": "model", "text": "I see it"},
            ]
        )
    )

    assert len(conv.turns) == 3
    assert conv.turns[1].attachments[0].drive_id == "img1"
