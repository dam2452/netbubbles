"""Run all example scripts and save output to example_output/."""

# pylint: disable=duplicate-code
import os
from pathlib import Path
import sys

# Ensure we run from project root
ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

# Ensure output dir exists
OUT = ROOT / "example_output"
OUT.mkdir(exist_ok=True)

scripts = sorted(Path(__file__).resolve().parent.glob("[0-9]*.py"))
scripts = [s for s in scripts if s.name != "generate_all.py"]

print(f"Running {len(scripts)} examples from {ROOT}...\n")

for script in scripts:
    print(f"  {script.name}...", end=" ", flush=True)
    try:
        with open(script, encoding="utf-8") as f:
            code = f.read()
        exec(compile(code, str(script), "exec"), {"__name__": "__main__", "__file__": str(script)})  # pylint: disable=exec-used
    except Exception as e:
        print(f"ERROR: {e}")

print(f"\nDone! {len(list(OUT.glob('*.svg')))} images in {OUT}/")
