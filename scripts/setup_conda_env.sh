#!/usr/bin/env bash
set -euo pipefail

ENV_NAME=robobrain2-env
PY_VERSION=3.10

echo "Creating conda environment '$ENV_NAME' (python $PY_VERSION) and installing requirements..."

# Create environment from environment.yml if it exists
if [[ -f "environment.yml" ]]; then
  echo "Using environment.yml to create environment"
  # Some conda versions don't accept --force. Remove if exists then create.
  if conda env list | grep -q "^${ENV_NAME}\s"; then
    echo "Existing environment detected — removing before create"
    conda env remove -n "$ENV_NAME" -y || true
  fi
  conda env create -f environment.yml -q
else
  conda create -n "$ENV_NAME" python="$PY_VERSION" -y -q
fi

# Activate the environment
# A user running this script should 'conda activate robobrain2-env' afterwards in interactive shells

# Install pip requirements
if [[ -f "requirements.txt" ]]; then
  echo "Installing pip requirements from requirements.txt"
  # Use pip from the newly created env
  conda run -n "$ENV_NAME" python -m pip install -r requirements.txt
fi

echo "Done. To use the environment run:"
echo "  conda activate $ENV_NAME"

echo "If your platform uses 'mamba' you can replace 'conda env create' with 'mamba env create' for speed."