from .create_or_delete_files import create_file, delete_file
from .diff_files import show_diff
from .edit_file import edit_file
from .get_current_directory import get_current_directory
from .get_directory_tree import get_directory_tree
from .get_framework_context_tool import get_framework_context_tool
from .grep_code import grep_code
from .read_file import read_file
from .vector_database_tools import (VECTOR_STORE_TOOLS, add_texts,
                                    delete_text, similarity_search,
                                    update_text)
from .write_code_to_file_path import write_code_to_file

FILE_SYS_TOOLS = [
    create_file,
    delete_file,
    show_diff,
    edit_file,
    read_file,
    write_code_to_file,
    grep_code,
    get_directory_tree,
    get_current_directory,
    get_framework_context_tool,
]

# Shell tools for persistent shell sessions
# SHELL_TOOLS = [
#     use_shell,
#     get_shell_working_directory,
#     reset_shell_directory,
# ]

# PowerShell tools for Windows systems
POWERSHELL_TOOLS = [
    use_powershell,
    get_powershell_working_directory,
    reset_powershell_directory,
    check_powershell_availability,
]

MEMORY_TOOLS=[
    update_memories,
    get_user_memory
]

VECTOR_STORE_TOOLS=[
    add_texts,
    delete_text,
    update_text,
    similarity_search
]


SHELL_TOOLS=[
    
]