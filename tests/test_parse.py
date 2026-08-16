from datetime import datetime, timezone

from ai_studio_md.parse import parse_conversation


def _wrap(chunks, settings=None, system=None):
    data = {"runSettings": settings or {}, "chunkedPrompt": {"chunks": chunks}}
    if system is not None:
        data["systemInstruction"] = system
    return data


def test_parses_a_plain_text_turn():
    conv = parse_conversation(
        _wrap([{"role": "user", "text": "Hello there", "createTime": "2026-05-22T12:17:00.000Z"}])
    )

    assert len(conv.turns) == 1
    assert conv.turns[0].role == "user"
    assert conv.turns[0].text == "Hello there"


def test_joins_parts_when_chunk_has_no_top_level_text():
    conv = parse_conversation(
        _wrap([{"role": "model", "parts": [{"text": "one "}, {"text": "two"}]}])
    )

    assert conv.turns[0].text == "one two"


def test_reads_the_contents_schema_used_by_api_exports():
    data = {"contents": [{"role": "user", "parts": [{"text": "from api"}]}]}

    conv = parse_conversation(data)

    assert conv.turns[0].text == "from api"


def test_marks_thought_chunks():
    conv = parse_conversation(
        _wrap(
            [
                {"role": "model", "isThought": True, "text": "reasoning"},
                {"role": "model", "text": "answer"},
            ]
        )
    )

    assert conv.turns[0].is_thought is True
    assert conv.turns[1].is_thought is False


def test_parses_create_time_into_an_aware_datetime():
    conv = parse_conversation(
        _wrap([{"role": "user", "text": "hi", "createTime": "2026-05-22T12:17:00.000Z"}])
    )

    assert conv.turns[0].timestamp == datetime(2026, 5, 22, 12, 17, tzinfo=timezone.utc)


def test_keeps_timestamp_none_when_absent_or_unparseable():
    conv = parse_conversation(
        _wrap([{"role": "user", "text": "a"}, {"role": "user", "text": "b", "createTime": "junk"}])
    )

    assert conv.turns[0].timestamp is None
    assert conv.turns[1].timestamp is None


def test_extracts_run_settings():
    conv = parse_conversation(
        _wrap(
            [],
            settings={
                "model": "models/gemini-3.1-pro-preview",
                "temperature": 1.0,
                "topP": 0.95,
                "topK": 64,
                "thinkingLevel": "THINKING_HIGH",
            },
        )
    )

    assert conv.model == "models/gemini-3.1-pro-preview"
    assert conv.temperature == 1.0
    assert conv.top_p == 0.95
    assert conv.top_k == 64
    assert conv.thinking_level == "THINKING_HIGH"


def test_sums_token_counts_across_chunks():
    conv = parse_conversation(
        _wrap([{"role": "user", "text": "a", "tokenCount": 10}, {"role": "model", "text": "b", "tokenCount": 32}])
    )

    assert conv.total_tokens == 42


def test_reads_system_instruction_from_parts():
    conv = parse_conversation(_wrap([], system={"parts": [{"text": "Be terse."}]}))

    assert conv.system_instruction == "Be terse."


def test_reads_system_instruction_given_as_a_bare_string():
    conv = parse_conversation(_wrap([], system="Be terse."))

    assert conv.system_instruction == "Be terse."


def test_empty_system_instruction_object_yields_no_instruction():
    conv = parse_conversation(_wrap([], system={}))

    assert conv.system_instruction == ""
