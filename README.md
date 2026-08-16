# AI Studio JSON to Markdown Extractor

A lightweight, zero-dependency Python CLI utility to convert Google AI Studio export files into clean, readable Markdown documents.

Google AI Studio exports are packed with configuration metadata, Web Search citations, and massive Base64 cryptographic thought signatures. This tool extracts the core conversation, styles it clearly, and strips out the noise.

## Quick start

Run it with no arguments and pick your files:

```bash
ai-studio-clean
```

A file dialog opens so you can browse to the downloaded export, then a save dialog asks where the Markdown should go. Both reopen wherever you were last time, so after the first run you just double-click the file and hit Save.

Passing paths directly still works exactly as before:

```bash
ai-studio-clean your_chat_file.json -o conversation.md
ai-studio-clean your_chat_file.json -o conversation.md -t
```

## Features

- Zero Dependencies: Built entirely with standard Python libraries.
- Interactive File Picking: Running the command bare opens native Open/Save dialogs that remember your last folders, so you never type a path.
- Headless Fallback: If no graphical dialog is available, it falls back to terminal prompts and names the package you need. Explicit path arguments never touch the GUI, so scripted and CI runs work anywhere.
- Dual-Schema Parsing: Automatically works with both Google Drive Auto-Save files and API payload JSON exports.
- Attachment Preservation: Images and documents shared into the chat stay marked in place instead of disappearing, so replies that refer to them still make sense. No Drive file IDs are written unless you ask for them.
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

## Method 1: Direct usage (no installation)

You only need a clone of this repository:

```bash
python extract.py                                  # pick files interactively
python extract.py your_chat_file.json -o out.md    # or pass paths
```

## Method 2: Global installation (run from anywhere)

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
| `input` | Path to your AI Studio export. Optional; omit it to pick the file in a dialog. |
| `-o`, `--output` | Where to write the Markdown. Omit it and you'll be asked, or it defaults to the input filename with a `.md` extension. |
| `-t`, `--thoughts` | Include the model's reasoning in collapsible sections. Works with the picker too. |
| `--drive-links` | Turn attachment markers into clickable Google Drive links. Off by default, because the link embeds the private file ID of your Drive file into the output. |

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

- Windows: `%APPDATA%\ai-studio-clean\config.json`
- macOS/Linux: `~/.config/ai-studio-clean/config.json`

Delete that file to reset. Nothing else is stored, and it never contains chat content.

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT
