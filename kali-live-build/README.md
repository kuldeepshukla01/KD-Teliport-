# AI-Integrated Kali Linux ISO Build Guide

This directory contains resources to build a custom Kali Linux ISO with the AI agent pre-installed.

## Prerequisites

- A Debian/Kali based system
- `live-build-config` package installed (`sudo apt install live-build-config`)

## Setup

1.  Clone the standard Kali live-build config:
    ```bash
    git clone https://gitlab.com/kalilinux/build-scripts/live-build-config.git
    cd live-build-config
    ```

2.  Copy the hook script from this repo into the live-build config:
    ```bash
    cp /path/to/ai-kali-agent/kali-live-build/hooks/01-install-agent.chroot kali-config/common/hooks/live/
    ```
    *Note: Ensure the hook is executable.*

3.  (Optional) Add `python3` and `python3-pip` to `kali-config/variant-default/package-lists/kali.list.chroot` if not already present.

4.  Build the ISO:
    ```bash
    ./build.sh --verbose
    ```

## What the Hook Does

The `01-install-agent.chroot` script runs during the ISO build process (inside the chroot). It:
1.  Clones the AI Agent repository.
2.  Runs the `install.sh` script to set up the agent globally.
3.  Ensures the agent is available in the path for the live user and installed system.
