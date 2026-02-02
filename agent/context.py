import os
import subprocess

class Context:
    def __init__(self, config):
        self.config = config

    def get_context(self):
        """
        Gather current environment context.
        """
        return {
            "cwd": os.getcwd(),
            "shell": os.environ.get("SHELL", "/bin/bash"),
            "history": self._get_history(),
            "user": os.environ.get("USER", "unknown"),
        }

    def _get_history(self, lines=10):
        """
        Attempt to read shell history.
        This is tricky as history is often in memory or specific files.
        """
        shell = os.environ.get("SHELL", "")
        history_file = ""
        
        if "zsh" in shell:
            history_file = os.path.expanduser("~/.zsh_history")
        elif "bash" in shell:
            history_file = os.path.expanduser("~/.bash_history")
            
        if history_file and os.path.exists(history_file):
            try:
                # Read last N lines. Handling potential binary issues in zsh history is complex,
                # this is a simplified text-based read.
                with open(history_file, 'rb') as f:
                    # simplistic approach: read end of file
                    try:
                        f.seek(-2000, 2) # Go back a bit
                    except OSError:
                        f.seek(0)
                    content = f.read().decode('utf-8', errors='ignore')
                    return "\n".join(content.splitlines()[-lines:])
            except Exception:
                return ""
        return ""
