# AI-Integrated Kali Linux Agent

An AI-powered terminal assistant designed for Kali Linux.

## Features
- **Suggest & Execute**: Ask questions or request commands in natural language.
- **Safety First**: Commands are reviewed by you before execution.
- **Local LLM Support**: Designed to work with LocalAI, Ollama, or any OpenAI-compatible local API.
- **Tool Generation**: (Coming Soon) Auto-generate Bash/Python scripts from your workflow.

## Installation

1.  **Prerequisites**:
    - Python 3.10+
    - A running local LLM (e.g., `ollama serve` or LocalAI) at `http://localhost:8080/v1` (configurable).

2.  **Install**:
    ```bash
    git clone https://github.com/your-repo/ai-kali-agent.git
    cd ai-kali-agent
    sudo ./scripts/install.sh
    ```

## Usage

Run the agent from anywhere:

```bash
agent "scan local network for open ports"
```

Or enter interactive mode (if implemented):
```bash
agent
```

## Configuration
Edit `~/.config/kali-ai-agent/config.toml` to change the LLM endpoint, model, or safety settings.

## Kali Live ISO Build
See `kali-live-build/` for instructions on how to build a custom Kali ISO with this agent pre-installed.