import matplotlib.pyplot as plt
from PIL import Image
import ast
import pathlib
from utils import get_model

def main():
    model, repo_dir = get_model()
    
    # Demo asset
    img_path = str(repo_dir / "assets/demo/grounding.jpg")
    prompt = "the person wearing a red hat"

    print(f"Image: {img_path}")
    print(f"Prompt: {prompt}")

    # Run inference
    pred = model.inference(prompt, img_path, task="grounding", enable_thinking=True, do_sample=True)
    print("=== Grounding ===")
    print(pred)

    # --- Visualization ---
    im = Image.open(img_path)
    plt.figure(figsize=(8,6))
    plt.imshow(im)

    # Parse bounding box
    try:
        bbox = ast.literal_eval(pred["answer"])
    except Exception:
        bbox = []

    if bbox and len(bbox) == 4:
        x1, y1, x2, y2 = bbox
        rect = plt.Rectangle((x1, y1), x2 - x1, y2 - y1,
                             linewidth=2, edgecolor="red", facecolor="none")
        plt.gca().add_patch(rect)
        plt.text(x1, y1-5, f"{bbox}", color="yellow", fontsize=8)

    plt.axis("off")
    plt.title("Grounding prediction overlay")
    
    # Save result
    results_dir = pathlib.Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    output_path = results_dir / "grounding_result.png"
    plt.savefig(output_path)
    print(f"Result saved to {output_path}")

if __name__ == "__main__":
    main()
