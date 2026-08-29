from __future__ import annotations

import runpy
import os
import sys
from pathlib import Path


server_value = os.environ.get("DAVINCI_RESOLVE_MCP_SERVER")
if not server_value:
    raise SystemExit(
        "Set DAVINCI_RESOLVE_MCP_SERVER to the local davinci-resolve-mcp server.py path."
    )
SERVER = Path(server_value).expanduser().resolve()


if __name__ == "__main__":
    if not SERVER.is_file():
        raise SystemExit(f"DaVinci Resolve MCP server not found: {SERVER}")
    sys.argv = [str(SERVER), "--self-test"]
    runpy.run_path(str(SERVER), run_name="__main__")
