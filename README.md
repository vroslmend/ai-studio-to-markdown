# AI Studio JSON to Markdown Extractor

A lightweight, zero-dependency Python CLI utility to convert Google AI Studio export files into clean, readable Markdown documents.

Google AI Studio exports are packed with configuration metadata, Web Search citations, and massive Base64 cryptographic thought signatures. This tool extracts the core conversation, styles it clearly, and strips out the noise.

## Quick start

Download a chat from Google AI Studio, then get a copy of this repository. Either clone it, or use the green Code button above and choose Download ZIP if you do not have git. Open a terminal in that folder and run:

```bash
python extract.py
```

A file dialog opens so you can browse to the downloaded chat, then a second dialog asks where to save the Markdown. Both dialogs reopen at the folders you used last time, so from the second run onwards it is just double-click and Save.

If you would rather type the paths, pass them as arguments:

```bash
python extract.py your_chat_file.json -o conversation.md
python extract.py your_chat_file.json -o conversation.md -t
```

To run the tool from any folder on your computer as `ai-studio-md`, see [Installation](#installation) below.

## Features

- Zero Dependencies: Built entirely with standard Python libraries.
- Interactive File Picking: Running it with no arguments opens ordinary Open and Save dialogs that remember your last folders, so you never have to type a file path.
- Headless Fallback: On a machine with no graphical dialogs, it asks for the paths in the terminal instead and tells you which package to install. Passing paths as arguments never opens a dialog at all, so automated runs work anywhere.
- Dual-Schema Parsing: Automatically works with both Google Drive Auto-Save files and API payload JSON exports.
- Attachment Preservation: Images and documents you shared in the chat are marked in place, so replies that refer to them still make sense. No Google Drive file IDs are written into the output unless you ask for them.
- Source Retention: Web Search citations become a readable source list, and grounded answers keep their numbered footnotes.
- Metadata Extraction: Appends model settings (version, temperature, top-P, top-K, thinking level, token count) and system instructions to the top of the output.
- Collapsible Thought Logs: Optional -t flag preserves reasoning paths using collapsible HTML &lt;details&gt; tags for clean rendering on GitHub/VS Code.
- ISO Timestamp Formatting: Converts system dates into a human-friendly format.

## Prerequisites

- Python 3.8 or higher.

The file dialogs use `tkinter`, which ships with Python on Windows and with the python.org builds on macOS. On Linux it's usually a separate package (`python3-tk` on Debian/Ubuntu, `python3-tkinter` on Fedora). Without it the tool falls back to terminal prompts rather than failing.

## Note on Google Drive downloads

When you download chat logs from the "Google AI Studio" folder in Google Drive, they arrive without a file extension. You do not need to rename them. The tool parses by content, not by extension, and the Open dialog shows all files by default.

---

## Installation

You do not have to install anything. Running `python extract.py` from a clone of this repository works on its own, as shown in Quick start above.

Installing is only worth it if you use the tool often. It gives you an `ai-studio-md` command that works from any folder, so you never have to be inside the repository:

```bash
ai-studio-md                                     # pick files in a dialog
ai-studio-md your_chat_file.json -o out.md       # or pass paths
```

### Option A: via pip

```bash
pip install .
pip install -e .    # editable, if you plan to modify it
```

### Option B: macOS and modern Linux, via pipx

Newer operating systems restrict global pip installs. If you hit an `externally-managed-environment` error, use `pipx`:

```bash
pipx install .
```

### Option C: straight from GitHub

```bash
pip install git+https://github.com/vroslmend/ai-studio-to-markdown.git
pipx install git+https://github.com/vroslmend/ai-studio-to-markdown.git
```

---

## Options

| Argument | Description |
|---|---|
| `input` | The chat file you downloaded. Leave it out and a dialog opens so you can browse for it. |
| `-o`, `--output` | Where to save the Markdown. If you gave an input file, this defaults to the same name and folder ending in `.md`. If you did not, a save dialog asks you. |
| `-t`, `--thoughts` | Include the model's reasoning, hidden inside collapsible sections you can expand. Off by default, because it roughly doubles the file size. |
| `--drive-links` | Turn attachment markers into clickable Google Drive links. Off by default, because the link contains the private ID of your Drive file. |

## A note on attachments

Images and documents you paste into a chat are not stored in the export itself. The file only records a pointer to your Google Drive.

By default the tool writes a plain marker where the attachment sat:

```
### User _Jun 17, 2026 - 02:54 PM_

[Image attachment]
```

That keeps the conversation readable without putting anything private in the file, so the Markdown is safe to share. Pass `--drive-links` and the marker becomes a link to the file in your Drive instead. Useful for your own notes; worth thinking twice about before sending that file to anyone else.

## Where settings are stored

The last-used input and output folders are remembered in:

- Windows: `%APPDATA%\ai-studio-md\config.json`
- macOS/Linux: `~/.config/ai-studio-md/config.json`

Delete that file to reset. Nothing else is stored, and it never contains chat content.

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT
