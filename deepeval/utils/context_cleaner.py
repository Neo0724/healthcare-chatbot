import re


def clean_context_chunk(text):
    # Restore line breaks where pipe-delimited headers collapsed structure
    text = text.replace("|###", "\n###").replace("|", "\n")
    # Drop headers with no content before the next header
    text = re.sub(r"###\s*[A-Z\s]+\n(?=###)", "", text)
    return text.strip()