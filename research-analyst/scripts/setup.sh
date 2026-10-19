#!/usr/bin/env bash
# Installs the Python packages the scripts need. pypandoc_binary bundles pandoc, so no system install is needed.
# Usage: bash "${CLAUDE_PLUGIN_ROOT}/scripts/setup.sh"
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
python3 -c "import numpy, websocket, docx" 2>/dev/null && { command -v pandoc >/dev/null || python3 -c "import pypandoc; pypandoc.get_pandoc_path()" 2>/dev/null; } && { echo "ready"; exit 0; }
python3 -m pip install -q -r "$HERE/requirements.txt" || python3 -m pip install -q --user -r "$HERE/requirements.txt" || python3 -m pip install -q --break-system-packages -r "$HERE/requirements.txt"
echo "installed"
