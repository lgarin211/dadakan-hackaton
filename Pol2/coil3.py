import re
import os
import shutil
import subprocess
import sys

input_md = "Bab4_5.md"
output_md = "Bab4_5_rendered.md"

def find_mermaid_command():
    """Return a command list prefix to run the mermaid CLI.

    Tries to find `mmdc` on PATH. If not found, falls back to `npx @mermaid-js/mermaid-cli` if `npx` is available.
    Otherwise returns None.
    """
    mmdc_path = shutil.which("mmdc")
    if mmdc_path:
        return [mmdc_path]
    npx_path = shutil.which("npx")
    if npx_path:
        # Use npx to run the mermaid-cli package without requiring a global install
        return [npx_path, "@mermaid-js/mermaid-cli"]
    return None


with open(input_md, "r", encoding="utf-8") as f:
    content = f.read()

blocks = re.findall(r"```mermaid\n(.*?)```", content, re.DOTALL)
cmd_prefix = find_mermaid_command()

if not cmd_prefix:
    sys.stderr.write(
        "ERROR: mermaid CLI not found. Install it with Node/npm and try again.\n"
        "Options:\n"
        "  1) Install globally (recommended): npm install -g @mermaid-js/mermaid-cli\n"
        "  2) Use npx (will auto-download): npx @mermaid-js/mermaid-cli -i diagram.mmd -o diagram.png\n"
    )
    raise SystemExit(2)

for i, block in enumerate(blocks, start=1):
    diagram_file = f"diagram_{i}.mmd"
    image_file = f"diagram_{i}.png"
    with open(diagram_file, "w", encoding="utf-8") as fh:
        fh.write(block)

    cmd = cmd_prefix + ["-i", diagram_file, "-o", image_file]
    try:
        print("Running:", " ".join(cmd))
        subprocess.run(cmd, check=True)
    except FileNotFoundError as e:
        sys.stderr.write(f"Command not found: {e}.\n")
        raise
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"mermaid-cli failed (exit {e.returncode}).\n")
        raise

    # replace the mermaid block with an image reference
    content = content.replace(f"```mermaid\n{block}```", f"![Diagram {i}]({image_file})")

with open(output_md, "w", encoding="utf-8") as f:
    f.write(content)
