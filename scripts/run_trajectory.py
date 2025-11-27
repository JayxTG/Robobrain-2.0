import matplotlib.pyplot as plt
from PIL import Image
import ast
import pathlib
from utils import get_model

def main():
    model, repo_dir = get_model()
    
    img_path = str(repo_dir / "assets/demo/trajectory.jpg")
    prompt = "reach for the banana on the plate"

    print(f"Image: {img_path}")
    print(f"Prompt: {prompt}")

    # Run inference
    pred = model.inference(prompt, img_path, task="trajectory", enable_thinking=True, do_sample=True)
    print("=== Trajectory ===")
    print(pred)

    # --- Visualization ---
    # Load image
    im = Image.open(img_path)
    plt.figure(figsize=(8,6))
    plt.imshow(im)

    # Parse trajectory points from pred['answer']
    try:
        points = ast.literal_eval(pred["answer"])
    except Exception:
        points = []

    if points:
        xs, ys = zip(*points)
        # Draw line and markers
        plt.plot(xs, ys, marker='o', color='red', linewidth=2, markersize=6)
        for (x, y) in points:
            plt.text(x+3, y-3, f"({x},{y})", color="yellow", fontsize=8)

    plt.axis("off")
    plt.title("Trajectory prediction overlay")
    
    # Save result
    results_dir = pathlib.Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    output_path = results_dir / "trajectory_result.png"
    plt.savefig(output_path)
    print(f"Result saved to {output_path}")

if __name__ == "__main__":
    main()
