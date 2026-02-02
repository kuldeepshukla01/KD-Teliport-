# KD - AI Terminal Agent for Kali Linux

**KD** is an advanced AI-powered terminal assistant designed specifically for offensive security workflows on Kali Linux. It acts as your pair programmer, tool builder, and safety guard.

## Core Features

### 🧠 Intelligent Assistance
*   **Natural Language Command Execution**: Ask KD to "scan the network" or "find SUID binaries," and it will propose the correct commands.
*   **Context Aware**: KD knows your shell history, current directory, and tracks your engagement scope via an internal database.
*   **Self-Healing**: If a command fails, KD intercepts the error, analyzes it, and proposes a fix automatically.

### 🛠️ Advanced Tool Synthesis
*   **Auto-Code Tools**: Tell KD to "Create a Python keylogger" or "Write a port scanner," and it will generate full multi-file projects with `requirements.txt` and proper structure.
    *   Command: `KD "make a tool that..." --mode generate`
*   **Database Registration**: Generated tools are automatically registered and tracked.

### 🛡️ Safety & Security
*   **Strict Deletion Protocol**: KD prevents accidental data loss. If a command involves deletion (`rm`, `unlink`), KD:
    1.  Inspects the file content.
    2.  Explains *what* is inside and *why* it's being deleted.
    3.  Requires you to explicitly type `yes`.
*   **Human-in-the-loop**: You always have the final say before execution.

## Installation

1.  **Prerequisites**:
    *   Python 3.10+
    *   A running local LLM (e.g., `ollama serve` or LocalAI) at `http://localhost:8080/v1`.

2.  **Install**:
    ```bash
    git clone https://github.com/your-repo/KD-Teliport-.git
    cd KD-Teliport-
    sudo ./scripts/install.sh
    ```
    *This will install the `KD` binary to `/usr/local/bin`.*

## Usage

**Basic Command Suggestion:**
```bash
KD "scan 192.168.1.10 for common vulnerabilities"
```

**Generate a New Tool:**
```bash
KD "Create a python script to brute force SSH using a wordlist" --mode generate
```

**Auto-Correction:**
Just run a command via KD. If it fails, KD will help you fix it.

## Configuration
Edit `~/.config/kali-ai-agent/config.toml` to customize:
*   LLM Endpoint & Model
*   System Prompt (Persona)
*   Safety Settings

## Building a Custom Kali ISO
Check the `kali-live-build/` directory for hooks to include KD pre-installed in your custom Kali Linux ISO.