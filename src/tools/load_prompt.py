def load_prompt(path: str) -> str:
    """
    Load prompt from specific text file.
    
    Args:
        path (str): File path
    
    Returns:
        str: Return prompt
    """
    with open(path, "r") as f:
        return"".join(f.readlines())