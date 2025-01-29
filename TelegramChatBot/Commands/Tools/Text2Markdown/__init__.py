"""
This function is according to the following docs:
https://core.telegram.org/bots/api#formatting-options
"""

import re

def text2markdown(text: str) -> str:
    """
    Escapes special characters in a given markdown text according to the provided rules.
    This function avoids escaping characters used for Markdown formatting (like * for bold or italic).

    Args:
        text (str): The input string that needs to be escaped.

    Returns:
        str: The escaped string where markdown special characters are properly escaped.
    """
    # Define the characters that need to be escaped in general
    special_chars = r"_\*\[\]\(\)~>#\+\-=|{}.!"
    
    # Escape backslashes first to avoid double escaping
    text = text.replace("\\", "\\\\")
    
    # Escape general special characters except those used for markdown formatting
    # Avoid escaping * and _ inside bold and italic text, and similar
    def escape_special(match):
        if match.group(0) in ["*", "_"]:
            return match.group(0)  # Don't escape * and _
        return "\\" + match.group(0)  # Escape all other special characters

    # Use a regular expression to find and escape special characters
    text = re.sub(f"([{special_chars}])", escape_special, text)
    
    return text