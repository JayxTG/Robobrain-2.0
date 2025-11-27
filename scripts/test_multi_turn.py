#!/usr/bin/env python3
"""
Test script for multi-turn conversation memory.

This script demonstrates and tests the conversation memory system
with a sequence of related queries about the same image.
"""

import sys
import pathlib
import gc
import torch

sys.path.insert(0, str(pathlib.Path(__file__).parent))

from utils import get_model
from conversation_memory import MultiTurnInference, ConversationMemory


def clear_gpu_memory():
    """Clear GPU memory cache."""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        gc.collect()


def test_conversation_memory_unit():
    """Unit tests for ConversationMemory class (no model needed)."""
    print("="*60)
    print("TEST 1: ConversationMemory Unit Tests")
    print("="*60)
    
    memory = ConversationMemory()
    
    # Test adding turns
    memory.add_user_turn("What objects are on the table?", "test_image.jpg", "general")
    memory.add_assistant_turn("There is a cup and a banana on the table.")
    
    assert len(memory) == 2, f"Expected 2 turns, got {len(memory)}"
    assert memory.current_image == "test_image.jpg"
    print("✅ Adding turns works correctly")
    
    # Test context generation
    context = memory.get_context_prompt()
    assert "cup" in context.lower() or "User" in context
    print("✅ Context prompt generation works")
    
    # Test save/load
    test_path = "/tmp/test_conversation.json"
    memory.save(test_path)
    
    memory2 = ConversationMemory()
    memory2.load(test_path)
    assert len(memory2) == 2
    print("✅ Save/Load works correctly")
    
    # Test clear
    memory.clear()
    assert len(memory) == 0
    assert memory.current_image is None
    print("✅ Clear works correctly")
    
    # Test max turns trimming
    memory = ConversationMemory(max_turns=5)
    for i in range(10):
        memory.add_user_turn(f"Question {i}")
        memory.add_assistant_turn(f"Answer {i}")
    assert len(memory) == 5, f"Expected 5 turns after trimming, got {len(memory)}"
    print("✅ History trimming works correctly")
    
    print("\n✅ All unit tests passed!\n")
    return True


def test_multi_turn_with_model(model, repo_dir):
    """Integration test with actual model."""
    print("="*60)
    print("TEST 2: Multi-Turn Inference Integration Test")
    print("="*60)
    
    # Initialize chat with provided model (no reload)
    chat = MultiTurnInference(model, repo_dir)
    
    # Set test image
    test_image = repo_dir / "assets/demo/grounding.jpg"
    if not test_image.exists():
        # Fallback to URL
        test_image = "http://images.cocodataset.org/val2017/000000039769.jpg"
    
    chat.set_image(str(test_image))
    
    print("\n" + "-"*40)
    print("Starting multi-turn conversation test...")
    print("-"*40)
    
    # Turn 1: Ask about the image
    print("\n📝 Turn 1: General question")
    result1 = chat.ask("What do you see in this image? Describe the main objects.", task="general")
    print(f"Answer: {result1.get('answer', 'N/A')[:200]}...")
    
    # Turn 2: Follow-up question (should use context)
    print("\n📝 Turn 2: Follow-up question (testing context)")
    result2 = chat.ask("Can you tell me more about the colors you see?", task="general")
    print(f"Answer: {result2.get('answer', 'N/A')[:200]}...")
    print(f"Context used: {result2.get('context_used', False)}")
    
    # Turn 3: Task-specific question
    print("\n📝 Turn 3: Grounding task")
    result3 = chat.ground("the most prominent object")
    print(f"Answer: {result3.get('answer', 'N/A')}")
    
    # Show history
    chat.show_history()
    
    # Verify memory state
    assert len(chat.memory) == 6, f"Expected 6 turns (3 Q&A pairs), got {len(chat.memory)}"
    print("\n✅ Multi-turn conversation test passed!")
    
    # Test save/load with model context
    print("\n" + "-"*40)
    print("Testing conversation save/load...")
    print("-"*40)
    
    save_path = str(pathlib.Path(__file__).parent.parent / "conversations" / "test_chat.json")
    chat.save_conversation(save_path)
    
    # Create new chat and load (reuse same model)
    chat2 = MultiTurnInference(model, repo_dir)
    chat2.load_conversation(save_path)
    
    assert len(chat2.memory) == len(chat.memory)
    print("✅ Conversation persistence test passed!")
    
    return True


def run_demo_conversation(model, repo_dir):
    """Run a demo showing the multi-turn capability."""
    print("\n" + "="*60)
    print("DEMO: Multi-Turn Conversation")
    print("="*60)
    
    # Reuse the same model instance (no reload)
    chat = MultiTurnInference(model, repo_dir)
    
    # Use demo image
    demo_image = "http://images.cocodataset.org/val2017/000000039769.jpg"
    chat.set_image(demo_image)
    
    # Simulate a realistic conversation
    conversation = [
        ("What animals do you see in this image?", "general"),
        ("How many of them are there?", "general"),
        ("What are they doing?", "general"),
        ("Point to where they are located", "pointing"),
    ]
    
    print(f"\n📷 Analyzing image: {demo_image}\n")
    
    for i, (question, task) in enumerate(conversation, 1):
        print(f"\n👤 User (Turn {i}): {question}")
        result = chat.ask(question, task=task, enable_thinking=False)
        answer = result.get('answer', '')
        if result.get('error'):
            print(f"🤖 RoboBrain: [Error] {result.get('error')[:100]}...")
        else:
            print(f"🤖 RoboBrain: {answer if answer else '(empty response)'}")
    
    print("\n" + "-"*40)
    print("Summary of conversation:")
    print(chat.memory.get_conversation_summary())
    print("-"*40)


if __name__ == "__main__":
    print("\n🧪 RoboBrain Multi-Turn Memory Test Suite\n")
    
    # Run unit tests first (no model needed)
    test_conversation_memory_unit()
    
    # Load model ONCE and reuse for all tests
    print("\n" + "="*60)
    print("Loading model (will be reused for all tests)...")
    print("="*60)
    
    try:
        model, repo_dir = get_model()
        clear_gpu_memory()
        
        # Run integration tests with the loaded model
        test_multi_turn_with_model(model, repo_dir)
        clear_gpu_memory()
        
        # Run demo with the same model
        run_demo_conversation(model, repo_dir)
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED! Multi-turn memory is working correctly.")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
