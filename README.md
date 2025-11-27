# RoboBrain 2.0 Scripts

This repository contains Python scripts to run inference with the RoboBrain 2.0 model on various tasks.

## Setup

There are two simple ways to prepare a reproducible environment for running the scripts below: (A) conda environment (recommended) or (B) pip-only virtualenv.

### A) Recommended — conda (reproducible)

1. Create the conda environment from `environment.yml`:

```bash
# create (or update) the environment
conda env create -f environment.yml --force

# activate
conda activate robobrain2-env

# install any remaining pip requirements
python -m pip install -r requirements.txt
```

There is a helper script at `scripts/setup_conda_env.sh` to automate this.

### B) Pip-only virtualenv (alternate)

```bash
# create virtualenv
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

2.  **Set Hugging Face Token**:
    *   Copy `.env.example` to `.env`:
        ```bash
        cp .env.example .env
        ```
    *   Edit `.env` and add your Hugging Face User Access Token (starts with `hf_`).
    *   Make sure you have accepted the license for the model `BAAI/RoboBrain2.0-3B` on Hugging Face.

3.  **First Run**:
    *   The first time you run any script, it will clone the `RoboBrain2.0` repository into `RoboBrain2.0_lib` and download the model weights. This may take some time.
    *   If you prefer to pre-clone the repo and inspect demo images before running, you can `git clone https://github.com/FlagOpen/RoboBrain2.0.git` and run scripts afterwards.

## Quick test (example)

After creating/activating the environment and adding your `HF_TOKEN` into `.env`: run the general QA script to verify everything works:

```bash
python scripts/run_general_qa.py
```

## Running Scripts

Each script performs a specific task using demo images from the RoboBrain repository.

*   **General QA**:
    ```bash
    python scripts/run_general_qa.py
    ```

*   **Visual Grounding**:
    ```bash
    python scripts/run_visual_grounding.py
    ```

*   **Affordance**:
    ```bash
    python scripts/run_affordance.py
    ```

*   **Trajectory**:
    ```bash
    python scripts/run_trajectory.py
    ```

*   **Pointing**:
    ```bash
    python scripts/run_pointing.py
    ```

## Results

The output images with visualizations will be saved in the `results/` directory.
