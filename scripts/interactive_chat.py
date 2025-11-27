#!/usr/bin/env python3
"""
Interactive Multi-Turn Chat with RoboBrain 2.0

Run this script to have a conversation with RoboBrain about images.
The model remembers previous exchanges and maintains context.

Usage:
    python scripts/interactive_chat.py
    python scripts/interactive_chat.py --image path/to/image.jpg
"""

import argparse
import sys
import pathlib

# Add scripts directory to path
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from utils import get_model
from conversation_memory import MultiTurnInference


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║         🤖 RoboBrain 2.0 Interactive Chat 🤖                ║
║                                                              ║
║  Commands:                                                   ║
║    /image <path>  - Set a new image                         ║
║    /task <type>   - Set task (general/grounding/affordance/ ║
║                     trajectory/pointing)                     ║
║    /history       - Show conversation history               ║
║    /clear         - Clear conversation memory               ║
║    /save <file>   - Save conversation to file               ║
║    /load <file>   - Load conversation from file             ║
║    /thinking on   - Enable thinking mode                    ║
║    /thinking off  - Disable thinking mode                   ║
║    /help          - Show this help                          ║
║    /quit          - Exit                                    ║
║                                                              ║
║  Just type your question to chat!                           ║
╚══════════════════════════════════════════════════════════════╝
""")


def main():
    parser = argparse.ArgumentParser(description="Interactive chat with RoboBrain 2.0")
    parser.add_argument("--image", "-i", type=str, help="Initial image to analyze")
    parser.add_argument("--no-thinking", action="store_true", help="Disable thinking mode")
    args = parser.parse_args()
    
    print_banner()
    
    # Load model
    print("Loading RoboBrain model...")
    model, repo_dir = get_model()
    
    # Initialize multi-turn chat
    chat = MultiTurnInference(model, repo_dir)
    
    # Settings
    current_task = "general"
    enable_thinking = not args.no_thinking
    
    # Set initial image if provided
    if args.image:
        chat.set_image(args.image)
    else:
        # Use a demo image by default
        demo_image = repo_dir / "assets/demo/grounding.jpg"
        if demo_image.exists():
            chat.set_image(str(demo_image))
            print(f"📷 Using demo image: {demo_image}")
        else:
            print("⚠️  No image set. Use /image <path> to set one.")
    
    print(f"\n🎯 Current task: {current_task}")
    print(f"🧠 Thinking mode: {'ON' if enable_thinking else 'OFF'}")
    print("\nType your question or /help for commands.\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye! 👋")
            break
        
        if not user_input:
            continue
        
        # Handle commands
        if user_input.startswith("/"):
            parts = user_input.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""
            
            if cmd == "/quit" or cmd == "/exit" or cmd == "/q":
                print("Goodbye! 👋")
                break
            
            elif cmd == "/help":
                print_banner()
            
            elif cmd == "/image":
                if arg:
                    # Check if file exists
                    if pathlib.Path(arg).exists() or arg.startswith("http"):
                        chat.set_image(arg)
                    else:
                        print(f"❌ Image not found: {arg}")
                else:
                    print(f"📷 Current image: {chat.memory.current_image}")
            
            elif cmd == "/task":
                valid_tasks = ["general", "grounding", "affordance", "trajectory", "pointing"]
                if arg.lower() in valid_tasks:
                    current_task = arg.lower()
                    print(f"🎯 Task set to: {current_task}")
                else:
                    print(f"❌ Invalid task. Choose from: {', '.join(valid_tasks)}")
            
            elif cmd == "/history":
                chat.show_history()
            
            elif cmd == "/clear":
                chat.reset()
            
            elif cmd == "/save":
                filepath = arg or "conversations/chat_history.json"
                chat.save_conversation(filepath)
            
            elif cmd == "/load":
                if arg:
                    try:
                        chat.load_conversation(arg)
                    except FileNotFoundError:
                        print(f"❌ File not found: {arg}")
                else:
                    print("Usage: /load <filepath>")
            
            elif cmd == "/thinking":
                if arg.lower() == "on":
                    enable_thinking = True
                    print("🧠 Thinking mode: ON")
                elif arg.lower() == "off":
                    enable_thinking = False
                    print("🧠 Thinking mode: OFF")
                else:
                    print(f"🧠 Thinking mode: {'ON' if enable_thinking else 'OFF'}")
            
            elif cmd == "/context":
                if arg.lower() == "on":
                    chat.use_context = True
                    print("📝 Context mode: ON (using conversation history)")
                elif arg.lower() == "off":
                    chat.use_context = False
                    print("📝 Context mode: OFF (each query is independent)")
                else:
                    print(f"📝 Context mode: {'ON' if chat.use_context else 'OFF'}")
            
            else:
                print(f"❌ Unknown command: {cmd}. Type /help for available commands.")
            
            continue
        
        # Regular chat message
        if not chat.memory.current_image:
            print("⚠️  No image set. Use /image <path> to set one first.")
            continue
        
        print(f"\n🤖 Thinking... (task: {current_task})")
        
        result = chat.ask(
            user_input,
            task=current_task,
            enable_thinking=enable_thinking
        )
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            # Show thinking if available
            if enable_thinking and result.get("thinking"):
                print(f"\n💭 Thinking: {result['thinking'][:300]}{'...' if len(result.get('thinking', '')) > 300 else ''}")
            
            print(f"\n🤖 Answer: {result['answer']}")
            
            if result.get("context_used"):
                print(f"   (Using conversation context from {result['turn_number']} turns)")
        
        print()


if __name__ == "__main__":
    main()
