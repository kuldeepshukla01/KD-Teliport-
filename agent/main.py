import argparse
import sys
import os
import toml
from pathlib import Path

# Add the parent directory to sys.path so we can import the agent package if running locally
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def load_config(config_path=None):
    if not config_path:
        # Default paths to check
        paths = [
            Path("config/default.toml"),
            Path("~/.config/kali-ai-agent/config.toml").expanduser(),
        ]
        for p in paths:
            if p.exists():
                return toml.load(p)
        return {}
    return toml.load(config_path)

def main():
    parser = argparse.ArgumentParser(description="AI-Integrated Kali Linux Agent")
    parser.add_argument("prompt", nargs="*", help="The command or question for the agent")
    parser.add_argument("--mode", choices=["explain", "suggest", "execute"], default="suggest", help="Operation mode")
    parser.add_argument("--config", help="Path to configuration file")
    
    args = parser.parse_args()
    
    config = load_config(args.config)
    
    if not args.prompt:
        parser.print_help()
        return

    user_query = " ".join(args.prompt)
    print(f"Agent received: {user_query}")
    print(f"Mode: {args.mode}")
    print(f"Config loaded: {config.get('agent', {}).get('default_mode', 'unknown')}")

    from agent.llm import LLM
    from agent.context import Context
    from agent.executor import Executor

    llm = LLM(config)
    context = Context(config)
    executor = Executor(config)
    
    # Get context data
    ctx_data = context.get_context()
    
    print("Thinking...")
    response = llm.generate(ctx_data, user_query)
    
    executor.handle(response, mode=args.mode)

if __name__ == "__main__":
    main()
