import json
import argparse
import os
from datetime import datetime

def format_time(time_str):
    """Converts ISO timestamp into a clean, readable format."""
    if not time_str:
        return ""
    try:
        # Standardize 'Z' to UTC offset for compatibility across Python 3.7+
        clean_time = time_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_time)
        return dt.strftime("%b %d, %Y - %I:%M %p")
    except Exception:
        # Return raw string as fallback if parsing fails
        return time_str

def clean_chat(input_file, output_file, keep_thoughts):
    if not os.path.exists(input_file):
        print(f"Error: Could not find '{input_file}'")
        return

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON. Detail: {e}")
        return

    markdown_output = []

    # Extract Settings/Metadata
    settings = data.get("runSettings", {})
    model_name = settings.get("model", "Unknown Model")
    temp = settings.get("temperature", "N/A")
    
    markdown_output.append(f"# Google AI Studio Export\n")
    markdown_output.append(f"**Model:** `{model_name}` | **Temperature:** `{temp}`\n\n---\n")

    # Extract System Instructions
    sys_instruction = data.get("systemInstruction", {})
    sys_text = ""
    
    if isinstance(sys_instruction, dict):
        parts = sys_instruction.get("parts", [])
        sys_text = "".join([p.get("text", "") for p in parts if "text" in p])
    elif isinstance(sys_instruction, str):
        sys_text = sys_instruction

    if sys_text.strip():
        markdown_output.append(f"### System Instructions\n> {sys_text.strip()}\n\n---\n")

    # Process Conversation Chunks
    # Handles both Google Drive Sync and direct API exports
    chunks = data.get("chunkedPrompt", {}).get("chunks", [])
    if not chunks:
        chunks = data.get("contents", [])

    if not chunks:
        print("Warning: No chat history found in the typical schema keys ('chunks' or 'contents').")

    for chunk in chunks:
        role = chunk.get("role", "UNKNOWN").capitalize()
        if role == "Model":
            role = "AI"
            
        timestamp = format_time(chunk.get("createTime", ""))
        time_display = f" _{timestamp}_" if timestamp else ""
        
        # Handle Thinking Blocks
        is_thought = chunk.get("isThought", False)
        if is_thought:
            if not keep_thoughts:
                continue
            else:
                thought_text = "".join([p.get("text", "") for p in chunk.get("parts", []) if "text" in p])
                markdown_output.append(f"<details>\n<summary>Model Thought Process{time_display}</summary>\n\n{thought_text}\n\n</details>\n\n")
                continue

        # Handle Standard Text Blocks
        text = chunk.get("text", "")
        if not text and "parts" in chunk:
            text = "".join([p.get("text", "") for p in chunk.get("parts", []) if "text" in p])

        if text.strip():
            markdown_output.append(f"### {role}{time_display}\n\n{text.strip()}\n\n---\n")

    # Write Output
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("".join(markdown_output))
        print(f"Success! Extracted chat saved to: {output_file}")
    except Exception as e:
        print(f"Error saving output file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Extract and format clean Markdown from Google AI Studio JSON exports.")
    parser.add_argument("input", help="Path to the downloaded AI Studio JSON file")
    parser.add_argument("-o", "--output", default="clean_chat.md", help="Output markdown file name (default: clean_chat.md)")
    parser.add_argument("-t", "--thoughts", action="store_true", help="Include model thoughts inside collapsible HTML tags")
    
    args = parser.parse_args()
    clean_chat(args.input, args.output, args.thoughts)

if __name__ == "__main__":
    main()