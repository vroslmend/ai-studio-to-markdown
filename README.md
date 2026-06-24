# AI Studio JSON to Markdown Extractor

A lightweight, zero-dependency Python CLI utility to convert Google AI Studio export files into clean, readable Markdown documents.

Google AI Studio exports are packed with configuration metadata, Web Search citations, and massive Base64 cryptographic thought signatures. This tool extracts the core conversation, styles it clearly, and strips out the noise.

## Features

- Zero Dependencies: Built entirely with standard Python libraries.
- Dual-Schema Parsing: Automatically works with both Google Drive Auto-Save files and API payload JSON exports.
- Metadata Extraction: Appends model settings (version, temperature) and system instructions to the top of the output.
- Collapsible Thought Logs: Optional -t flag preserves reasoning paths using collapsible HTML <details> tags for clean rendering on GitHub/VS Code.
- ISO Timestamp Formatting: Converts system dates into a human-friendly format.

## Prerequisites

- Python 3.7 or higher.

## Note on Google Drive Downloads

When you download your chat logs directly from the "Google AI Studio" folder in Google Drive, Google downloads them without any file extension (as an unknown file type).

You can handle this in two ways:

1. Rename the file: Append .json to the file you downloaded (e.g., rename MyChat to MyChat.json).
2. Run the script directly: The Python script does not require a specific extension to parse the data. You can pass the extensionless file straight to the script.

---

## Method 1: Direct Usage (No Installation Required)

This is the simplest way to run the script. You do not need to install anything; you only need the `extract.py` file in your working directory.

Run the script directly using Python:

```bash
# Basic extraction (strips model thoughts for maximum readability)
python extract.py your_chat_file.json -o conversation.md

# Keep the model's reasoning/thoughts inside dropdown menus
python extract.py your_chat_file.json -o conversation.md -t
```

---

## Method 2: Global Installation (Run from Anywhere)

If you use this tool frequently, you can install it globally on your system to run the `ai-studio-clean` command from any directory without typing out Python file paths.

### Option A: Standard Installation (Via Pip)

If you have cloned the repository, navigate to the folder and run:

```bash
pip install .
```

If you are a developer planning to modify the script, install it in editable mode so changes sync automatically:

```bash
pip install -e .
```

### Option B: For macOS and Modern Linux (Via Pipx)

Newer operating systems restrict global pip installations to protect system files. If you run into an `externally-managed-environment` error, use `pipx` instead:

```bash
pipx install .
```

### Option C: Direct Installation from GitHub

You can install the tool globally straight from GitHub without manually cloning the repository:

```bash
# Using pip
pip install git+https://github.com/yourusername/google-ai-studio-exporter.git

# Using pipx (macOS/Linux recommended)
pipx install git+https://github.com/yourusername/google-ai-studio-exporter.git
```

### Usage after Global Installation

Once installed, navigate to any folder (such as your Downloads folder) and run the command directly:

```bash
# Basic usage
ai-studio-clean MyDownloadedFile -o clean_chat.md

# Including thoughts
ai-studio-clean MyDownloadedFile -o clean_chat.md -t
```

---

## Options

- input: Path to your downloaded AI Studio file (required).
- -o, --output: Define a custom output filename (default: clean_chat.md).
- -t, --thoughts: Include the model's internal thinking process.

## License

MIT
