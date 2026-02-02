import subprocess
import shlex
import sys

class Executor:
    def __init__(self, config):
        self.config = config
        self.default_mode = config.get('agent', {}).get('default_mode', 'confirm')
        self.allowed_commands = set(config.get('safety', {}).get('allowed_commands', []))
        self.blocked_commands = config.get('safety', {}).get('blocked_commands', [])

    def handle(self, response, mode=None):
        """
        Process the response from the LLM. 
        For now, we assume the LLM response *is* the command if it's a short single line, 
        or we try to extract code blocks.
        """
        if not response:
            print("No response from agent.")
            return

        current_mode = mode if mode else self.default_mode
        
        # Simple heuristic: if response starts with #, it's a comment/explanation.
        if response.strip().startswith('#') or '\n' in response.strip():
             # Likely an explanation or multi-line script
             print(f"\nAgent suggests:\n{response}")
             if current_mode == "execute":
                 print("\n[!] Multi-line or explanation detected. Not executing automatically.")
             return

        command = response.strip()
        
        if current_mode == "explain":
            print(f"Proposed Command: {command}")
            return

        if self._is_blocked(command):
            print(f"[!] Command blocked by safety policy: {command}")
            return

        if current_mode == "auto":
            # Check if allowed
            cmd_base = shlex.split(command)[0]
            if cmd_base in self.allowed_commands:
                self._run(command)
            else:
                self._confirm_and_run(command)
        else:
            # Default to confirm
            self._confirm_and_run(command)

    def _is_blocked(self, command):
        for blocked in self.blocked_commands:
            if blocked in command:
                return True
        return False

    def _confirm_and_run(self, command):
        print(f"\nProposing command: \033[1m{command}\033[0m")
        choice = input("Execute? [y/N/e(dit)]: ").lower()
        if choice == 'y':
            self._run(command)
        elif choice == 'e':
            new_cmd = input("Edit command: ")
            self._run(new_cmd)
        else:
            print("Aborted.")

    def _run(self, command):
        print(f"Executing: {command}")
        try:
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
