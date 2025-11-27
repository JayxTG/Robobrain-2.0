import sys
import importlib
import os

print("Environment verification script — basic checks")
print("--------------------------")
print(f"Python: {sys.version.splitlines()[0]}")

try:
    import torch
    print(f"torch: {torch.__version__} — cuda available: {torch.cuda.is_available()}")
except Exception as e:
    print("torch: not available or failed to import —", e)

packages = [
    "transformers",
    "huggingface_hub",
    "timm",
    "matplotlib",
    "PIL",
]

for pkg in packages:
    try:
        mod = importlib.import_module(pkg)
        ver = getattr(mod, "__version__", "unknown")
        print(f"{pkg}: installed — version {ver}")
    except Exception as e:
        print(f"{pkg}: NOT installed or failed to import — {e}")

# Show CONDA env name if available
conda_env = os.environ.get("CONDA_DEFAULT_ENV")
print(f"Conda env active: {conda_env or 'none detected'}")

print("--------------------------")
print("Quick pip freeze tail (last 20 lines)\n")
try:
    import subprocess
    out = subprocess.check_output([sys.executable, "-m", "pip", "freeze"]).decode("utf-8")
    lines = out.strip().splitlines()
    for l in lines[-20:]:
        print(l)
except Exception as e:
    print("pip freeze failed:", e)
