"""Command line entry point.

Path resolution follows a strict precedence: explicit arguments win outright
and never open a dialog; a bare run falls back to the picker.
"""

import argparse
import json
import sys
from pathlib import Path

from .config import config_path, load_config, save_config
from .parse import parse_conversation
from .picker import select_picker
from .render import render_markdown


def _default_output_for(input_path):
    return str(Path(input_path).with_suffix(".md"))


def resolve_io(input_arg, output_arg, picker, settings):
    """Return (input, output), asking the picker only for what is missing."""
    input_path = input_arg
    if not input_path:
        input_path = picker.choose_input(settings.get("input_dir", ""))
        if not input_path:
            return None

    output_path = output_arg
    if not output_path:
        default_name = Path(_default_output_for(input_path)).name
        if input_arg:
            # An explicit input implies its own destination; don't interrupt.
            output_path = _default_output_for(input_path)
        else:
            output_path = picker.choose_output(settings.get("output_dir", ""), default_name)
            if not output_path:
                return None

    return input_path, output_path


def _load_export(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _remember(input_path, output_path):
    settings = load_config(config_path())
    settings["input_dir"] = str(Path(input_path).resolve().parent)
    settings["output_dir"] = str(Path(output_path).resolve().parent)
    save_config(config_path(), settings)


def _summarise(conv):
    turns = sum(1 for t in conv.turns if not t.is_thought)
    attachments = sum(len(t.attachments) for t in conv.turns)
    sources = sum(len(t.sources) for t in conv.turns)
    parts = [f"{turns} turns"]
    if attachments:
        parts.append(f"{attachments} attachments")
    if sources:
        parts.append(f"{sources} sources")
    return ", ".join(parts)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="ai-studio-md",
        description="Convert a Google AI Studio export into clean Markdown. "
        "Run with no arguments to pick the files interactively.",
    )
    parser.add_argument("input", nargs="?", help="AI Studio export (extension optional)")
    parser.add_argument("-o", "--output", help="Markdown file to write")
    parser.add_argument(
        "-t", "--thoughts", action="store_true", help="include the model's reasoning, collapsed"
    )
    parser.add_argument(
        "--drive-links",
        action="store_true",
        help="link attachments to Google Drive (embeds private file ids in the output)",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    settings = load_config(config_path())
    chosen = resolve_io(args.input, args.output, select_picker(), settings)
    if chosen is None:
        print("Cancelled.", file=sys.stderr)
        return 1
    input_path, output_path = chosen

    try:
        data = _load_export(input_path)
    except OSError:
        print(f"Error: could not find or read '{input_path}'", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: that file is not valid JSON ({e})", file=sys.stderr)
        return 1

    conv = parse_conversation(data)
    markdown = render_markdown(conv, keep_thoughts=args.thoughts, drive_links=args.drive_links)

    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown)
    except OSError as e:
        print(f"Error: could not write '{output_path}' ({e})", file=sys.stderr)
        return 1

    _remember(input_path, output_path)
    print(f"Saved {output_path}  ({_summarise(conv)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
