import os
import queue
import select
import subprocess
import threading
from typing import Optional


class PersistentShell:
    def __init__(self, shell_type: str = None):
        """Initialize persistent shell session"""
        self.shell_type = shell_type or self._detect_shell()
        self.process: Optional[subprocess.Popen] = None
        self.output_queue = queue.Queue()
        self.input_queue = queue.Queue()
        self.is_running = False
        
    def _detect_shell(self) -> str:
        """Auto-detect appropriate shell"""
        if os.name == 'nt':  # Windows
            return 'cmd'
        else:  # Unix-like
            return os.environ.get('SHELL', '/bin/bash')
    
    def start_session(self):
        """Start a new persistent shell session"""
        if self.is_running:
            self.stop_session()
            
        # Start shell process with pseudo-terminal for interactivity
        self.process = subprocess.Popen(
            self.shell_type,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=0,  # Unbuffered
            universal_newlines=True
        )
        
        self.is_running = True
        
        # Start output reader thread
        self.output_thread = threading.Thread(
            target=self._read_output, 
            daemon=True
        )
        self.output_thread.start()
        
        print(f"✓ Started new {self.shell_type} session")
        
    def stop_session(self):
        """Stop current shell session"""
        if self.process and self.is_running:
            self.is_running = False
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            print("✓ Shell session stopped")
    
    def _read_output(self):
        """Read shell output in background thread"""
        while self.is_running and self.process.poll() is None:
            try:
                # Use select on Unix, polling on Windows
                if hasattr(select, 'select') and os.name != 'nt':
                    ready, _, _ = select.select([self.process.stdout], [], [], 0.1)
                    if ready:
                        output = self.process.stdout.read(1)
                        if output:
                            self.output_queue.put(output)
                else:
                    # Windows fallback - read with timeout
                    output = self.process.stdout.read(1)
                    if output:
                        self.output_queue.put(output)
            except:
                break
    
    def execute_command(self, command: str, interactive: bool = True) -> str:
        """Execute command in persistent shell
        
        Args:
            command: Shell command to execute
            interactive: If True, allows human interaction for prompts
        
        Returns:
            Command output
        """
        if not self.is_running:
            raise RuntimeError("Shell session not started")
        
        print(f"$ {command}")
        
        # Send command to shell
        self.process.stdin.write(command + '\n')
        self.process.stdin.flush()
        
        output_buffer = ""
        
        if interactive:
            return self._handle_interactive_command(output_buffer)
        else:
            return self._handle_non_interactive_command(output_buffer)
    
    def _handle_interactive_command(self, output_buffer: str) -> str:
        """Handle commands that may need user interaction"""
        import time
        
        last_output_time = time.time()
        waiting_for_input = False
        
        while True:
            # Check for new output
            while not self.output_queue.empty():
                char = self.output_queue.get()
                output_buffer += char
                print(char, end='', flush=True)
                last_output_time = time.time()
                waiting_for_input = False
            
            # Check if we might be waiting for user input
            current_time = time.time()
            if current_time - last_output_time > 2:  # 2 second timeout
                if not waiting_for_input:
                    # Check if last line looks like a prompt
                    lines = output_buffer.strip().split('\n')
                    if lines and self._looks_like_prompt(lines[-1]):
                        waiting_for_input = True
                        print("\n[Waiting for input...]")
                        user_input = input()
                        
                        # Send user input to shell
                        self.process.stdin.write(user_input + '\n')
                        self.process.stdin.flush()
                        last_output_time = time.time()
                        waiting_for_input = False
                else:
                    # Command seems to be finished
                    break
            
            time.sleep(0.1)
        
        return output_buffer
    
    def _handle_non_interactive_command(self, output_buffer: str) -> str:
        """Handle non-interactive commands with timeout"""
        import time
        
        start_time = time.time()
        timeout = 30  # 30 second timeout
        
        while time.time() - start_time < timeout:
            while not self.output_queue.empty():
                output_buffer += self.output_queue.get()
            
            # Simple heuristic: if no output for 1 second, assume done
            if output_buffer and time.time() - start_time > 1:
                break
                
            time.sleep(0.1)
        
        print(output_buffer)
        return output_buffer
    
    def _looks_like_prompt(self, line: str) -> bool:
        """Heuristic to detect if line is asking for input"""
        prompt_indicators = [
            '?', ':', '[Y/n]', '[y/N]', 'password', 'Password',
            'continue?', 'proceed?', 'confirm', 'enter', 'input',
            'choose', 'select'
        ]
        line_lower = line.lower()
        return any(indicator.lower() in line_lower for indicator in prompt_indicators)
    
    def get_current_directory(self) -> str:
        """Get current working directory of shell"""
        if os.name == 'nt':
            result = self.execute_command('cd', interactive=False)
        else:
            result = self.execute_command('pwd', interactive=False)
        return result.strip()
    
    def change_directory(self, path: str) -> str:
        """Change directory in persistent shell"""
        return self.execute_command(f'cd "{path}"', interactive=False)

