import matplotlib.pyplot as plt
from PIL import Image
import ast
import pathlib
from utils import get_model

def main():
    model, repo_dir = get_model()
    
    img_path = str(repo_dir / "assets/demo/affordance.jpg")
    prompt = "hold the cup"

    print(f"Image: {img_path}")
    print(f"Prompt: {prompt}")

    # Run inference
    pred = model.inference(prompt, img_path, task="affordance", enable_thinking=True, do_sample=True)
    print("=== Affordance ===")
    print(pred)

    # --- Visualization ---
    im = Image.open(img_path)
    plt.figure(figsize=(8,6))
    plt.imshow(im)

    # Parse bounding box from prediction
    try:
        bbox = ast.literal_eval(pred["answer"])
    except Exception:
        bbox = []

    if bbox and len(bbox) == 4:
        x1, y1, x2, y2 = bbox
        # Draw rectangle
        rect = plt.Rectangle((x1, y1), x2 - x1, y2 - y1,
                             linewidth=2, edgecolor="red", facecolor="none")
        plt.gca().add_patch(rect)
        plt.text(x1, y1-5, f"{bbox}", color="yellow", fontsize=8)

    plt.axis("off")
    plt.title("Affordance prediction overlay")
    
    # Save result
    results_dir = pathlib.Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    output_path = results_dir / "affordance_result.png"
    plt.savefig(output_path)
    print(f"Result saved to {output_path}")

if __name__ == "__main__":
    main()
