# Arog Dashboard

Dense, terminal-aesthetic dashboard for system monitoring, Docker container management, and Python agent interaction.

## Features

- **Docker Container Management**: Auto-detect web UIs, view all containers, control lifecycle
- **System Diagnostics**: Extended metrics (CPU, memory, disk, network, processes, temperatures)
- **Python Agent**: Interactive notebook-style Python execution with persistent namespace and history
- **Real-time Updates**: Server-Sent Events for smooth metrics updates (no polling)
- **Dense UI**: Maximum information density, zero wasted space, terminal aesthetic

## Quick Start

```bash
# Build and run
docker-compose up -d

# Access dashboard
open http://arog:80
# or http://192.168.12.141:80
```

## Architecture

- **Backend**: FastAPI (async, SSE support)
- **Frontend**: htmx + Alpine.js (minimal JS, declarative)
- **Monitoring**: psutil + docker-py
- **Agent**: Python REPL with IPython kernel
- **UI**: Custom CSS, terminal aesthetic, no frameworks

## Development

```bash
# Local development
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload --port 9100

# Build Docker image
docker build -t arog-dashboard .
```

## Configuration

Environment variables (docker-compose.yml):
- `HOST_IP`: Host IP address (default: 192.168.12.141)
- `HOSTNAME`: System hostname (default: arog)

## Python Agent

Interactive Python environment with persistent namespace:

```python
# Pre-loaded modules
import os, sys, json, re, Path, datetime

# Helper functions
help_agent()  # Show available modules
list_vars()   # List all variables in namespace

# Namespace persists between executions
x = 42
# Later...
print(x)  # Works - namespace is persistent
```

## Docker Container UI Detection

Auto-detects web UIs by:
1. Checking container labels (`web.url`)
2. Matching against known patterns (Portainer, Gitea, etc.)
3. Detecting common HTTP ports (80, 443, 8080, etc.)
4. Assuming single-port containers have web UIs

Override detection with label:
```yaml
labels:
  web.url: "http://192.168.12.141:8080"
```

## License

MIT License
