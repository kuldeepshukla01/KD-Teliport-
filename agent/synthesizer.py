import os
import re
import json
from pathlib import Path
from agent.llm import LLM

class Synthesizer:
    def __init__(self, config):
        self.config = config
        self.llm = LLM(config)
        self.tools_dir = Path(config.get('agent', {}).get('tools_dir', "~/.agent-tools")).expanduser()
        self.tools_dir.mkdir(parents=True, exist_ok=True)

    def synthesize(self, prompt, existing_tools=None):
        """
        Generates a tool based on the user prompt.
        Handles both single-file scripts and multi-file projects.
        """
        print(f"[*] Synthesizing tool for: {prompt}")
        
        system_msg = """You are an expert offensive security tool developer. 
        Your job is to create robust, working security tools based on user requests.
        
        If the request requires a complex tool (e.g., C2, RAT, Keylogger, sophisticated scanner), 
        YOU MUST GENERATE A MULTI-FILE PROJECT structure.
        
        Output Format:
        You must return a JSON object wrapped in <tool_json> tags.
        
        Structure:
        <tool_json>
        {
            "name": "tool_name",
            "type": "single_file" OR "project",
            "description": "Short description",
            "install_commands": ["list", "of", "commands", "to", "install", "deps"],
            "files": [
                {
                    "path": "filename.py",
                    "content": "code here..."
                },
                {
                    "path": "requirements.txt",
                    "content": "requests\n..."
                }
            ]
        }
        </tool_json>
        
        Constraints:
        - For Python tools, always include a `requirements.txt` if external deps are needed.
        - Code MUST be production-ready, with error handling and help text.
        - DO NOT put placeholders like 'insert payload here'. Generate a functional example payload.
        """
        
        user_msg = f"Create a tool that does the following: {prompt}"
        
        # Override system prompt for this specific call
        original_prompt = self.llm.system_prompt
        self.llm.system_prompt = system_msg
        
        try:
            response = self.llm.generate({}, user_msg)
        finally:
             # Restore prompt
            self.llm.system_prompt = original_prompt

        # Parse output
        try:
            json_match = re.search(r'<tool_json>(.*?)</tool_json>', response, re.DOTALL)
            if json_match:
                tool_data = json.loads(json_match.group(1))
                return self._save_tool(tool_data)
            else:
                # Fallback: maybe it returned just raw code? 
                print("[!] LLM did not return structured JSON. Saving raw output as notes.")
                return None
        except Exception as e:
            print(f"[!] Error parsing generated tool: {e}")
            return None

    def _save_tool(self, tool_data):
        name = tool_data.get('name', 'generated_tool')
        tool_type = tool_data.get('type', 'single_file')
        
        if tool_type == "project":
            base_path = self.tools_dir / name
            base_path.mkdir(exist_ok=True)
            print(f"[*] Creating project at: {base_path}")
        else:
            base_path = self.tools_dir
            
        files = tool_data.get('files', [])
        saved_paths = []
        
        for f in files:
            file_path = base_path / f['path']
            # Ensure subdirectories exist if path has them
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w') as out:
                out.write(f['content'])
            
            if file_path.suffix == '.sh' or file_path.suffix == '.py':
                os.chmod(file_path, 0o755)
                
            saved_paths.append(str(file_path))
            print(f"    -> Created {f['path']}")
            
        # Post-install info
        cmds = tool_data.get('install_commands', [])
        if cmds:
            print("\n[*] Installation Commands (Run these manually for safety):")
            for c in cmds:
                print(f"    {c}")
                
        # Register in DB
        try:
            from agent.db import Database
            db = Database()
            # Determine primary language
            lang = "python"
            if any(str(p).endswith('.sh') for p in saved_paths):
                lang = "bash"
                
            db.add_tool_metadata(
                name=name,
                description=tool_data.get('description', 'Auto-generated tool'),
                language=lang,
                path=str(base_path),
                tags=["auto-generated", tool_type]
            )
            print(f"[*] Tool registered in database.")
        except Exception as e:
            print(f"[!] Semantic DB registration failed: {e}")
        
        return base_path
