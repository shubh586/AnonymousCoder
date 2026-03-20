from pathlib import Path

from langchain_core.tools import tool


@tool
def edit_file(path: str, old_content: str, new_content: str) -> str:
    """
    Edit a file by replacing a specific block of text with new content.
    This performs a targeted find-and-replace within the file.
    
    Args:
        path: The file path to edit
        old_content: The exact text block to find and replace (must match exactly)
        new_content: The replacement text
    
    Returns:
        A success message with line information, or an error message
    """
    try:
        file_path = Path(path)
        
        if not file_path.exists():
            return f"File '{path}' does not exist."
        
        if not file_path.is_file():
            return f"'{path}' is not a file."
        
        # Read the current content
        current_content = file_path.read_text(encoding='utf-8')
        
        # Check if old_content exists in the file
        if old_content not in current_content:
            return (
                f"Could not find the specified text block in '{path}'. "
                f"Make sure the text matches exactly (including whitespace and indentation)."
            )
        
        # Count occurrences
        count = current_content.count(old_content)
        if count > 1:
            return (
                f"Found {count} occurrences of the specified text in '{path}'. "
                f"Please provide a more specific text block that matches only once."
            )
        
        # Perform the replacement
        new_file_content = current_content.replace(old_content, new_content, 1)
        
        # Write back
        file_path.write_text(new_file_content, encoding='utf-8')
        
        # Find the line number where the edit was made
        lines_before = current_content[:current_content.index(old_content)].count('\n') + 1
        old_line_count = old_content.count('\n') + 1
        new_line_count = new_content.count('\n') + 1
        
        return (
            f"Successfully edited '{path}' at line {lines_before}. "
            f"Replaced {old_line_count} line(s) with {new_line_count} line(s)."
        )
        
    except PermissionError as e:
        return f"Permission denied editing '{path}': {e}"
    except OSError as e:
        return f"Error editing '{path}': {e}"
    except Exception as e:
        return f"Unexpected error editing '{path}': {e}"