import matplotlib.pyplot as plt
from PIL import Image
import ast
import pathlib
from utils import get_model

def main():
    model, repo_dir = get_model()
    
    img_path = str(repo_dir / "assets/demo/pointing.jpg")
    prompt = "Identify several spots within the vacant space that's between the two mugs"

    print(f"Image: {img_path}")
    print(f"Prompt: {prompt}")

    # Run inference
    pred = model.inference(prompt, img_path, task="pointing", enable_thinking=True, do_sample=True)
    print("=== Pointing ===")
    print(pred)

    # --- Visualization ---
    im = Image.open(img_path)
    plt.figure(figsize=(8,6))
    plt.imshow(im)

    # Parse coordinates from prediction
    try:
        points = ast.literal_eval(pred["answer"])
    except Exception:
        points = []

    # Plot each point
    if points:
        xs, ys = zip(*points)
        plt.scatter(xs, ys, c="red", s=40, marker="x")
        for (x, y) in points:
            plt.text(x+3, y-3, f"({x},{y})", color="yellow", fontsize=7)

    plt.axis("off")
    plt.title("Pointing prediction overlay")
    
    # Save result
    results_dir = pathlib.Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    output_path = results_dir / "pointing_result.png"
    plt.savefig(output_path)
    print(f"Result saved to {output_path}")

if __name__ == "__main__":
    main()
