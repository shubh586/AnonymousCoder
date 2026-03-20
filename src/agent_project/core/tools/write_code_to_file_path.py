from pathlib import Path

from langchain_core.tools import tool

from .diff_files import show_diff_function


@tool
def write_code_to_file(path: str, content: str) -> str:
    """
    Write content to a file at the specified path. If the file already exists,
    it will show a diff of the changes before writing.
    
    Args:
        path: The file path to write to
        content: The content to write to the file
    
    Returns:
        A message indicating success with diff if the file was modified, 
        or just success if it was newly created.
    """
    try:
        file_path = Path(path)
        
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # If file exists, show diff before overwriting
        diff_output = ""
        if file_path.exists():
            # Write new content to a temp file for diffing
            temp_path = str(file_path) + ".tmp"
            try:
                Path(temp_path).write_text(content, encoding='utf-8')
                diff_output = show_diff_function(str(file_path), temp_path)
            finally:
                # Clean up temp file
                Path(temp_path).unlink(missing_ok=True)
        
        # Write the content
        file_path.write_text(content, encoding='utf-8')
        
        result = f"Successfully wrote {len(content)} characters to {path}"
        if diff_output and diff_output != "[INFO] No differences found.":
            result += f"\n\nChanges:\n{diff_output}"
        
        return result
        
    except PermissionError as e:
        return f"Permission denied writing to '{path}': {e}"
    except OSError as e:
        return f"Error writing to '{path}': {e}"
    except Exception as e:
        return f"Unexpected error writing to '{path}': {e}"
