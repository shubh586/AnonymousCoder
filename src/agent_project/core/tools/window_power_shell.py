import os
import shlex
import subprocess
from typing import Optional

from langchain_core.tools import tool

# Global state to maintain current working directory for PowerShell
_powershell_working_dir: Optional[str] = None

def _get_powershell_working_dir() -> str:
    """Get the current working directory for PowerShell, initializing it if needed."""
    global _powershell_working_dir
    if _powershell_working_dir is None:
        _powershell_working_dir = os.getcwd()
    return _powershell_working_dir

def _set_powershell_working_dir(new_dir: str) -> bool:
    """Set the current working directory for PowerShell if it exists and is accessible."""
    global _powershell_working_dir
    try:
        if os.path.exists(new_dir) and os.path.isdir(new_dir):
            _powershell_working_dir = os.path.abspath(new_dir)
            return True
        return False
    except Exception:
        return False

def _is_powershell_available() -> bool:
    """Check if PowerShell is available on the system."""
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Write-Host 'PowerShell available'"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

@tool
def use_powershell(powershell_cmd: str) -> str:
    """
    Execute PowerShell commands with persistent working directory.
    
    This tool maintains the current working directory across PowerShell commands.
    If you run 'Set-Location C:\\path\\to\\directory', subsequent commands will execute
    in that directory until you change it again.
    
    Args:
        powershell_cmd: The PowerShell command to execute
        
    Returns:
        The output of the command or error message
    """
    try:
        # Check if PowerShell is available
        if not _is_powershell_available():
            return "❌ Error: PowerShell is not available on this system. This tool is designed for Windows systems with PowerShell installed."
        
        current_dir = _get_powershell_working_dir()
        
        # Handle Set-Location (cd) command specially to maintain persistent directory
        cmd_parts = shlex.split(powershell_cmd.strip())
        if cmd_parts and cmd_parts[0].lower() in ['set-location', 'cd', 'sl']:
            if len(cmd_parts) == 1:
                # Set-Location without arguments - go to home directory
                new_dir = os.path.expanduser("~")
            else:
                # Set-Location with path
                target_path = cmd_parts[1]
                if os.path.isabs(target_path):
                    new_dir = target_path
                else:
                    new_dir = os.path.join(current_dir, target_path)
            
            if _set_powershell_working_dir(new_dir):
                return f"✅ Changed PowerShell directory to: {_get_powershell_working_dir()}"
            else:
                return f"❌ Error: Directory '{new_dir}' does not exist or is not accessible"
        
        # Handle Get-Location (pwd) command
        elif cmd_parts and cmd_parts[0].lower() in ['get-location', 'pwd', 'gl']:
            return f"📁 Current PowerShell directory: {_get_powershell_working_dir()}"
        
        # Execute other commands in the current working directory
        else:
            # Use subprocess to run the PowerShell command in the persistent directory
            # Convert the directory to Windows format if needed
            windows_dir = current_dir.replace('/', '\\')
            
            # Create PowerShell command that changes to the directory and executes the command
            full_cmd = f"Set-Location '{windows_dir}'; {powershell_cmd}"
            
            result = subprocess.run(
                ["powershell", "-Command", full_cmd],
                cwd=current_dir,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            output_parts = []
            
            # Add current directory info
            output_parts.append(f"📁 Executed in: {current_dir}")
            
            # Add command info
            output_parts.append(f"🔧 PowerShell Command: {powershell_cmd}")
            
            # Add stdout if present
            if result.stdout:
                output_parts.append(f"📤 Output:\n{result.stdout}")
            
            # Add stderr if present
            if result.stderr:
                output_parts.append(f"⚠️  Errors:\n{result.stderr}")
            
            # Add return code info
            if result.returncode == 0:
                output_parts.append("✅ PowerShell command completed successfully")
            else:
                output_parts.append(f"❌ PowerShell command failed with exit code: {result.returncode}")
            
            return "\n".join(output_parts)
            
    except subprocess.TimeoutExpired:
        return f"❌ Error: PowerShell command timed out after 30 seconds"
    except Exception as e:
        return f"❌ Error executing PowerShell command '{powershell_cmd}': {str(e)}"

@tool
def get_powershell_working_directory() -> str:
    """
    Get the current working directory of the persistent PowerShell session.
    
    Returns:
        The current working directory path
    """
    return f"📁 Current PowerShell directory: {_get_powershell_working_dir()}"

@tool
def reset_powershell_directory() -> str:
    """
    Reset the PowerShell working directory to the system's current working directory.
    
    Returns:
        Confirmation message with the new directory
    """
    global _powershell_working_dir
    _powershell_working_dir = os.getcwd()
    return f"🔄 Reset PowerShell directory to: {_get_powershell_working_dir()}"

@tool
def check_powershell_availability() -> str:
    """
    Check if PowerShell is available on the current system.
    
    Returns:
        Status message about PowerShell availability
    """
    if _is_powershell_available():
        return "✅ PowerShell is available on this system"
    else:
        return "❌ PowerShell is not available on this system. This tool is designed for Windows systems with PowerShell installed."
