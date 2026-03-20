
from langchain_core.tools import tool


@tool
def read_file(path:str):
    """Read the contents of a file at the given path.

    Args:
        path: The file path to read

    Returns:
        The file contents as a string, or an error message
    """
    content=""
    try:
        with open(path,mode="r") as f:
            content=f.read()
    except FileNotFoundError:
        return f"File Not found :{path}"
    except PermissionError:
        return f"Permission denied accessing: {path}"
    except Exception as e:
        return f"Error accessing {path}: {str(e)}"
   
    return content