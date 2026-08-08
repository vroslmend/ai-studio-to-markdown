import json
import argparse
import os
import base64
from datetime import datetime

# MIME types AI Studio exports use, mapped onto sensible file extensions
IMAGE_EXTENSIONS = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
    "image/heic": "heic",
    "image/heif": "heif",
}

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

def get_extension(mime_type):
    """Picks a file extension for an image MIME type."""
    if mime_type in IMAGE_EXTENSIONS:
        return IMAGE_EXTENSIONS[mime_type]
    # Fall back to whatever follows the slash (e.g. 'image/bmp' -> 'bmp')
    if "/" in mime_type:
        return mime_type.split("/")[-1]
    return "bin"

def collect_images(chunk):
    """
    Pulls attached image payloads out of a chunk, covering both export schemas.

    Google Drive Auto-Save files store them on the chunk itself as 'inlineImage',
    while API payload exports nest them inside 'parts' as 'inlineData'.
    """
    images = []

    inline = chunk.get("inlineImage")
    if isinstance(inline, dict) and inline.get("data"):
        images.append(inline)

    for part in chunk.get("parts", []):
        data = part.get("inlineData") or part.get("inline_data")
        if isinstance(data, dict) and data.get("data"):
            images.append(data)

    return images

def save_image(image, assets_dir, counter):
    """Decodes a Base64 image payload and writes it into the assets folder."""
    mime_type = image.get("mimeType") or image.get("mime_type") or "image/jpeg"
    filename = f"image_{counter:03d}.{get_extension(mime_type)}"

    try:
        raw_bytes = base64.b64decode(image["data"])
    except Exception as e:
        print(f"Warning: Could not decode image {counter}. Detail: {e}")
        return None

    try:
        os.makedirs(assets_dir, exist_ok=True)
        with open(os.path.join(assets_dir, filename), "wb") as f:
            f.write(raw_bytes)
    except Exception as e:
        print(f"Warning: Could not save image {counter}. Detail: {e}")
        return None

    return filename

def clean_chat(input_file, output_file, keep_thoughts, extract_images=True):
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

    # Attached images are written to a folder sitting beside the markdown file
    base_name = os.path.splitext(os.path.basename(output_file))[0]
    assets_folder = f"{base_name}_images"
    assets_dir = os.path.join(os.path.dirname(os.path.abspath(output_file)), assets_folder)
    image_count = 0

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

        # Handle Attached Images
        image_refs = []
        if extract_images:
            for image in collect_images(chunk):
                filename = save_image(image, assets_dir, image_count + 1)
                if filename:
                    image_count += 1
                    # Forward slashes keep the link working on every platform
                    image_refs.append(f"![Attached image {image_count}]({assets_folder}/{filename})")

        # Handle Standard Text Blocks
        text = chunk.get("text", "")
        if not text and "parts" in chunk:
            text = "".join([p.get("text", "") for p in chunk.get("parts", []) if "text" in p])

        # Images and text from the same chunk share one heading
        body = []
        if image_refs:
            body.append("\n\n".join(image_refs))
        if text.strip():
            body.append(text.strip())

        if body:
            markdown_output.append(f"### {role}{time_display}\n\n" + "\n\n".join(body) + "\n\n---\n")

    # Write Output
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("".join(markdown_output))
        print(f"Success! Extracted chat saved to: {output_file}")
        if image_count:
            print(f"Saved {image_count} image(s) to: {assets_dir}")
    except Exception as e:
        print(f"Error saving output file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Extract and format clean Markdown from Google AI Studio JSON exports.")
    parser.add_argument("input", help="Path to the downloaded AI Studio JSON file")
    parser.add_argument("-o", "--output", default="clean_chat.md", help="Output markdown file name (default: clean_chat.md)")
    parser.add_argument("-t", "--thoughts", action="store_true", help="Include model thoughts inside collapsible HTML tags")
    parser.add_argument("--no-images", action="store_true", help="Skip extracting attached images into a sibling folder")

    args = parser.parse_args()
    clean_chat(args.input, args.output, args.thoughts, not args.no_images)

if __name__ == "__main__":
    main()
