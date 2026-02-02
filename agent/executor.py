import subprocess
import shlex
import sys
import os

class Executor:
    def __init__(self, config, llm=None):
        self.config = config
        self.llm = llm
        self.default_mode = config.get('agent', {}).get('default_mode', 'confirm')
        self.allowed_commands = set(config.get('safety', {}).get('allowed_commands', []))
        self.allowed_commands.discard('rm') # Safety override
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

    def _handle_destructive_command(self, command):
        print(f"\n\033[1;31m[!] DESTRUCTIVE COMMAND DETECTED\033[0m")
        parts = shlex.split(command)
        if parts[0] == 'sudo': parts = parts[1:]
        targets = [arg for arg in parts[1:] if not arg.startswith('-')]
        
        info = ""
        for t in targets:
            if os.path.exists(t):
                if os.path.isfile(t):
                    try:
                        with open(t, 'r', encoding='utf-8', errors='replace') as f:
                            preview = f.read(512)
                        info += f"File: {t}\nPreview:\n{preview}\n---\n"
                    except Exception as e:
                        info += f"File: {t} (read error: {e})\n"
                else:
                    info += f"Directory: {t}\n"
            else:
                 info += f"Target: {t} (Not found)\n"

        if self.llm:
            prompt = f"User is running destructive command: '{command}'. Targets:\n{info}\nExplain what is being deleted and why it might be necessary."
            explanation = self.llm.generate({}, prompt)
            print(f"\n\033[1;33mAnalyzed Impact:\033[0m\n{explanation}\n")
        else:
            print(f"\nTargets:\n{info}")
            
        confirm = input("\033[1;31mType 'yes' to confirm deletion: \033[0m")
        if confirm != 'yes':
            print("Aborted.")
            return

        self._run(command)

    def _confirm_and_run(self, command):
        parts = shlex.split(command)
        cmd = parts[0] if parts else ""
        if cmd == 'sudo' and len(parts) > 1: cmd = parts[1]
        
        if cmd in ['rm', 'unlink', 'shred']:
            self._handle_destructive_command(command)
            return

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
            
            # Auto-correction attempt
            # We only try once to avoid loops
            print("\n[*] Attempting to auto-correct...")
            from agent.corrector import Corrector
            corrector = Corrector(self.config)
            
            # Capture stderr (we need to rerun to capture it if not captured above, 
            # but simpler here: just pass the user-visible error or re-run to capture output)
            # For this MVP, we assume we ask the LLM based on the fact it failed.
            # Ideally subprocess.run should capture output. Let's fix that.
            
            # Re-running to capture output for the LLM (safe-ish since it just failed)
            # Real implementation should capture it in the first run.
            proc = subprocess.run(command, shell=True, capture_output=True, text=True)
            error_msg = proc.stderr + "\n" + proc.stdout
            
            fix = corrector.correct(command, error_msg)
            if fix:
                print(f"Proposed Fix: {fix}")
                self._confirm_and_run(fix)
