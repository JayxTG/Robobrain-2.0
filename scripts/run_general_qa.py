import pprint
from utils import get_model

def main():
    model, _ = get_model()
    
    prompt = "What is shown in this image?"
    image = "http://images.cocodataset.org/val2017/000000039769.jpg"

    print(f"Image: {image}")
    print(f"Prompt: {prompt}")

    print("Running inference (no thinking)...")
    pred_no_thinking = model.inference(prompt, image, task="general", enable_thinking=False, do_sample=True)
    
    print("Running inference (with thinking)...")
    pred_thinking = model.inference(prompt, image, task="general", enable_thinking=True, do_sample=True)

    print("\n=== General (no thinking) ===")
    pprint.pprint(pred_no_thinking)
    print("\n=== General (with thinking) ===")
    pprint.pprint(pred_thinking)

if __name__ == "__main__":
    main()
