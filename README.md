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

---

## 🧠 Multi-Turn Conversation Memory

RoboBrain 2.0 now supports **multi-turn conversations** where the model maintains context across multiple queries about the same image or scene.

### Features

- **Conversation History**: The model remembers previous questions and answers
- **Context-Aware Responses**: Follow-up questions can reference earlier discussion
- **Save/Load Conversations**: Persist conversations to JSON files
- **Multiple Task Types**: Switch between general QA, grounding, affordance, trajectory, and pointing within the same conversation

### Interactive Chat

Start an interactive conversation session:

```bash
python scripts/interactive_chat.py

# Or with a specific image:
python scripts/interactive_chat.py --image path/to/your/image.jpg
```

**Available commands in chat:**

| Command | Description |
|---------|-------------|
| `/image <path>` | Set a new image to analyze |
| `/task <type>` | Switch task type (general/grounding/affordance/trajectory/pointing) |
| `/history` | Show conversation history |
| `/clear` | Clear conversation memory |
| `/save <file>` | Save conversation to JSON file |
| `/load <file>` | Load a previous conversation |
| `/thinking on/off` | Toggle thinking mode |
| `/help` | Show all commands |
| `/quit` | Exit |

### Example Conversation

```
You: What objects do you see in this image?
🤖 RoboBrain: I can see a cup, a banana, and a remote control on the table.

You: Which one should I grab to drink water?
🤖 RoboBrain: You should grab the cup. It appears to be a drinking vessel.

You: /task grounding
🎯 Task set to: grounding

You: the cup
🤖 RoboBrain: [142, 89, 256, 198]
```

### Programmatic Usage

Use multi-turn memory in your own scripts:

```python
from scripts.utils import get_model
from scripts.conversation_memory import MultiTurnInference

# Load model
model, repo_dir = get_model()

# Initialize multi-turn chat
chat = MultiTurnInference(model, repo_dir)

# Set image
chat.set_image("path/to/image.jpg")

# Have a conversation
response1 = chat.ask("What objects are on the table?")
print(response1["answer"])

# Follow-up question (uses context from previous exchange)
response2 = chat.ask("Which one is closest to the edge?")
print(response2["answer"])

# Switch to grounding task
bbox = chat.ground("the red cup")
print(bbox["answer"])  # Returns bounding box coordinates

# Save conversation for later
chat.save_conversation("conversations/my_chat.json")

# Clear and start fresh
chat.reset()
```

### API Reference

**`MultiTurnInference` class:**

| Method | Description |
|--------|-------------|
| `set_image(path)` | Set the current image for conversation |
| `ask(prompt, task="general")` | Ask a question with context |
| `ground(description)` | Shortcut for grounding task |
| `get_affordance(action)` | Shortcut for affordance task |
| `get_trajectory(action)` | Shortcut for trajectory task |
| `point_at(description)` | Shortcut for pointing task |
| `reset()` | Clear conversation memory |
| `save_conversation(path)` | Save to JSON file |
| `load_conversation(path)` | Load from JSON file |
| `show_history()` | Print conversation history |

### Testing

Run the multi-turn memory test suite:

```bash
python scripts/test_multi_turn.py
```

---

## Local Weights

If you have pre-downloaded model weights, place them in the `weights/` folder with the following structure:

```
weights/
├── config.json
├── model-00001-of-00002.safetensors
├── model-00002-of-00002.safetensors
├── model.safetensors.index.json
├── tokenizer.json
├── tokenizer_config.json
└── ... (other config files)
```

The scripts will automatically detect and use local weights instead of downloading from HuggingFace.
