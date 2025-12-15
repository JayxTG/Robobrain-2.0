#!/usr/bin/env python3
"""
Planning Chat with RoboBrain 2.0

A dedicated planning-focused chat script that uses ShareRobot-style templates
for various planning task types including:
- Planning Task (next step for a goal)
- Planning with Context (next step given completed tasks)
- Planning Remaining Steps (next N steps)
- Future Prediction (what happens after a task)
- Success Detection (was task completed?)
- Affordance Detection (can/is task be done?)
- Past Description (what was the last task?)

Usage:
    python scripts/planning_chat.py
    python scripts/planning_chat.py --image path/to/image.jpg
"""

import argparse
import sys
import pathlib
import re
import json
import os
import random
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

# Add scripts directory to path
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from utils import get_model
from conversation_memory import MultiTurnInference

# Try to import visualization libraries
try:
    import cv2
    import numpy as np
    from PIL import Image
    HAS_VIS = True
except ImportError:
    HAS_VIS = False
    print("Warning: cv2/PIL not available. Visualization disabled.")

# Results directory
RESULTS_BASE_DIR = pathlib.Path(__file__).parent.parent / "results" / "planning"

# ============================================================================
# PLANNING QUESTION TEMPLATES (from ShareRobot)
# ============================================================================

PLANNING_TEMPLATES = {
    "planning": {
        "description": "Determine the next step to achieve a long-horizon goal",
        "templates": [
            "The objective is {goal}, what should be the next step to move forward?",
            "In pursuit of achieving {goal}, what's the next action to take?",
            "To reach the goal of {goal}, which task should be prioritized next?",
            "Given the goal of {goal}, what is the most logical next move?",
            "With the aim of {goal}, what should you focus on next?"
        ]
    },
    "planning_with_context": {
        "description": "Determine next step given completed tasks",
        "templates": [
            "So far, you've completed these steps: {completed_steps}. What's the next move to achieve the goal of {goal}?",
            "With the following steps completed: {completed_steps}. What is the next logical step toward {goal}?",
            "Considering the goal of {goal}, and having done {completed_steps}, what should you do next?",
            "You are working towards {goal}. After completing steps {completed_steps}, what's the next immediate task?",
            "Given your progress so far ({completed_steps}), what's the next step toward achieving {goal}?"
        ]
    },
    "planning_remaining": {
        "description": "Determine the next N steps to complete a goal",
        "templates": [
            "With {goal} as the goal and the steps {completed_steps} completed, what are the next {num_steps} things to do?",
            "To work toward {goal}, what are the next {num_steps} steps after completing {completed_steps}?",
            "Here's what's been done so far: {completed_steps}. What are the next {num_steps} tasks to take toward the goal of {goal}?",
            "The goal is {goal}. After completing {completed_steps}, what are the next {num_steps} steps you should take?",
            "Given the progress so far: {completed_steps}, what's the next set of {num_steps} steps to move closer to {goal}?"
        ]
    },
    "future_prediction": {
        "description": "Predict what will happen after a task",
        "templates": [
            "Based on the current situation, what is expected to happen after {last_task}?",
            "What do you think will happen after {last_task} is completed?",
            "Considering the current sequence of tasks, what's likely to occur after {last_task}?",
            "Given the context, what will most likely happen following {last_task}?",
            "After {last_task}, what's the most probable next event?"
        ]
    },
    "success_detection": {
        "description": "Determine if a task was completed successfully",
        "templates": [
            "Was {task} completed successfully?",
            "Has {task} been fully carried out?",
            "Has {task} reached completion?",
            "Was {task} finalized?",
            "Can we say that {task} was accomplished?"
        ]
    },
    "affordance_positive": {
        "description": "Determine if a task can be done right now",
        "templates": [
            "Is {task} something that can be accomplished right now?",
            "Can {task} be initiated at this moment?",
            "Is it feasible to begin {task} immediately?",
            "Is now a suitable time to carry out {task}?",
            "Can you proceed with {task} given the current conditions?"
        ]
    },
    "affordance_negative": {
        "description": "Determine if a specific task is currently being done",
        "templates": [
            "Is {task} what you're working on at the moment?",
            "Are you currently engaged in {task}?",
            "Is this {task} you're focused on right now?",
            "Is this {task} you're handling at present?",
            "Are you doing {task} at this very moment?"
        ]
    },
    "generative_affordance": {
        "description": "Determine what actions are possible right now",
        "templates": [
            "What can you do at this moment?",
            "Which task is possible to start right now?",
            "Given the current situation, what action can be taken?",
            "What's the next available action?",
            "Considering the circumstances, what task can you begin now?"
        ]
    },
    "past_description": {
        "description": "Describe what task was just completed",
        "templates": [
            "What was the last task completed?",
            "What just occurred?",
            "What was the most recent action taken?",
            "What task did you just finish?",
            "What happened immediately before this?"
        ]
    }
}


# ============================================================================
# PLANNING SESSION MANAGER
# ============================================================================

class PlanningSession:
    """Manages a planning session with task history and goal tracking."""
    
    def __init__(self):
        self.goal = None
        self.completed_tasks = []
        self.current_task = None
        self.task_history = []  # Full history with timestamps
        self.run_dir = None
    
    def set_goal(self, goal: str):
        """Set the long-horizon goal for this planning session."""
        self.goal = goal
        self.completed_tasks = []
        self.current_task = None
        print(f"[GOAL SET] {goal}")
    
    def add_completed_task(self, task: str):
        """Mark a task as completed."""
        self.completed_tasks.append(task)
        self.task_history.append({
            "task": task,
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        })
        print(f"[TASK COMPLETED] {len(self.completed_tasks)}. {task}")
    
    def set_current_task(self, task: str):
        """Set the current task being worked on."""
        self.current_task = task
        print(f"[CURRENT TASK] {task}")
    
    def get_completed_steps_str(self) -> str:
        """Get completed steps as a formatted string."""
        if not self.completed_tasks:
            return "none"
        return ", ".join([f"{i+1}-{task}" for i, task in enumerate(self.completed_tasks)])
    
    def get_last_task(self) -> str:
        """Get the last completed task."""
        if self.completed_tasks:
            return self.completed_tasks[-1]
        return "starting the task"
    
    def reset(self):
        """Reset the planning session."""
        self.goal = None
        self.completed_tasks = []
        self.current_task = None
        self.task_history = []
        print("[SESSION RESET]")
    
    def show_status(self):
        """Display current planning session status."""
        print("\n" + "="*60)
        print("[PLANNING SESSION STATUS]")
        print("="*60)
        print(f"Goal: {self.goal or 'Not set'}")
        print(f"Current Task: {self.current_task or 'None'}")
        print(f"Completed Tasks ({len(self.completed_tasks)}):")
        for i, task in enumerate(self.completed_tasks):
            print(f"  {i+1}. {task}")
        print("="*60 + "\n")


# ============================================================================
# PLANNING EXECUTOR
# ============================================================================

class PlanningExecutor:
    """Executes planning queries using RoboBrain."""
    
    def __init__(self, model, repo_dir):
        self.chat = MultiTurnInference(model, repo_dir)
        self.session = PlanningSession()
        self.run_dir = None
    
    def set_image(self, image_path: str):
        """Set the image for planning queries."""
        self.chat.set_image(image_path)
        # Create per-run results directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = RESULTS_BASE_DIR / f"run_{timestamp}"
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.session.run_dir = self.run_dir
        print(f"[IMAGE SET] {image_path}")
        print(f"[OUTPUT] Results will be saved to: {self.run_dir}")
    
    def generate_prompt(self, query_type: str, **kwargs) -> str:
        """Generate a planning prompt from templates."""
        if query_type not in PLANNING_TEMPLATES:
            return kwargs.get("custom_prompt", "Describe what you see.")
        
        templates = PLANNING_TEMPLATES[query_type]["templates"]
        template = random.choice(templates)
        
        # Fill in template variables
        replacements = {
            "goal": kwargs.get("goal", self.session.goal or "complete the task"),
            "completed_steps": kwargs.get("completed_steps", self.session.get_completed_steps_str()),
            "last_task": kwargs.get("last_task", self.session.get_last_task()),
            "task": kwargs.get("task", self.session.current_task or "the current task"),
            "num_steps": kwargs.get("num_steps", "5")
        }
        
        for key, value in replacements.items():
            template = template.replace("{" + key + "}", str(value))
        
        return template
    
    def ask_planning(self, query_type: str, enable_thinking: bool = False, **kwargs) -> Dict[str, Any]:
        """Execute a planning query."""
        prompt = self.generate_prompt(query_type, **kwargs)
        
        print(f"\n{'='*60}")
        print(f"[PLANNING QUERY] Type: {query_type}")
        print(f"[PROMPT] {prompt}")
        print("="*60)
        
        result = self.chat.ask(
            prompt,
            task="general",  # Planning uses general task
            enable_thinking=enable_thinking
        )
        
        answer = result.get("answer", "")
        thinking = result.get("thinking", "")
        
        print(f"\n[ANSWER] {answer}")
        
        if thinking and enable_thinking:
            print(f"[THINKING] {thinking[:200]}...")
        
        return {
            "query_type": query_type,
            "prompt": prompt,
            "answer": answer,
            "thinking": thinking,
            "success": True
        }
    
    def ask_custom(self, prompt: str, enable_thinking: bool = False) -> Dict[str, Any]:
        """Execute a custom planning query."""
        print(f"\n{'='*60}")
        print(f"[CUSTOM QUERY]")
        print(f"[PROMPT] {prompt}")
        print("="*60)
        
        result = self.chat.ask(
            prompt,
            task="general",
            enable_thinking=enable_thinking
        )
        
        answer = result.get("answer", "")
        thinking = result.get("thinking", "")
        
        print(f"\n[ANSWER] {answer}")
        
        return {
            "query_type": "custom",
            "prompt": prompt,
            "answer": answer,
            "thinking": thinking,
            "success": True
        }
    
    def run_planning_pipeline(self, goal: str, enable_thinking: bool = False) -> Dict[str, Any]:
        """Run a full planning pipeline for a goal."""
        self.session.set_goal(goal)
        
        results = {
            "goal": goal,
            "steps": [],
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
        
        # Step 1: What can we do now?
        print("\n" + "="*60)
        print("[PIPELINE STEP 1/4] Checking available actions...")
        print("="*60)
        step1 = self.ask_planning("generative_affordance", enable_thinking=enable_thinking)
        results["steps"].append(step1)
        self._show_intermediate_result(1, "Available Actions", step1)
        
        # Step 2: What's the first step?
        print("\n" + "="*60)
        print("[PIPELINE STEP 2/4] Determining first step...")
        print("="*60)
        step2 = self.ask_planning("planning", enable_thinking=enable_thinking, goal=goal)
        results["steps"].append(step2)
        self._show_intermediate_result(2, "First Step", step2)
        
        # Extract the suggested first task
        first_task = self._extract_task_from_answer(step2["answer"])
        if first_task:
            self.session.set_current_task(first_task)
        
        # Step 3: Can we do this task now?
        print("\n" + "="*60)
        print("[PIPELINE STEP 3/4] Checking if first task is feasible...")
        print("="*60)
        step3 = self.ask_planning("affordance_positive", enable_thinking=enable_thinking, 
                                  task=first_task or "the first step")
        results["steps"].append(step3)
        self._show_intermediate_result(3, "Feasibility Check", step3)
        
        # Step 4: What are the remaining steps?
        print("\n" + "="*60)
        print("[PIPELINE STEP 4/4] Planning remaining steps...")
        print("="*60)
        step4 = self.ask_planning("planning_remaining", enable_thinking=enable_thinking,
                                  goal=goal, num_steps="5")
        results["steps"].append(step4)
        self._show_intermediate_result(4, "Remaining Steps", step4)
        
        # Save pipeline results to file
        self._save_pipeline_results(results)
        
        # Show summary
        self._show_pipeline_summary(results)
        
        return results
    
    def _show_intermediate_result(self, step_num: int, step_name: str, result: Dict[str, Any]):
        """Display intermediate result in a formatted way."""
        print("\n" + "-"*60)
        print(f"INTERMEDIATE RESULT - Step {step_num}: {step_name}")
        print("-"*60)
        print(f"Query Type: {result.get('query_type', 'N/A')}")
        print(f"Prompt: {result.get('prompt', 'N/A')}")
        print("-"*30)
        print(f"Response:")
        print(f"  {result.get('answer', 'No answer')}")
        if result.get('thinking'):
            print("-"*30)
            print(f"Thinking (truncated):")
            thinking = result['thinking'][:300] + "..." if len(result.get('thinking', '')) > 300 else result.get('thinking', '')
            print(f"  {thinking}")
        print("-"*60 + "\n")
    
    def _save_pipeline_results(self, results: Dict[str, Any]):
        """Save pipeline results to JSON file."""
        if not self.run_dir:
            return
        
        # Save full results
        results_file = self.run_dir / "pipeline_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"[SAVED] Pipeline results: {results_file}")
        
        # Save human-readable summary
        summary_file = self.run_dir / "pipeline_summary.txt"
        with open(summary_file, 'w') as f:
            f.write("="*60 + "\n")
            f.write("PLANNING PIPELINE SUMMARY\n")
            f.write("="*60 + "\n\n")
            f.write(f"Goal: {results['goal']}\n")
            f.write(f"Timestamp: {results.get('timestamp', 'N/A')}\n\n")
            
            for i, step in enumerate(results['steps'], 1):
                f.write("-"*40 + "\n")
                f.write(f"Step {i}: {step.get('query_type', 'N/A')}\n")
                f.write("-"*40 + "\n")
                f.write(f"Prompt: {step.get('prompt', 'N/A')}\n\n")
                f.write(f"Answer:\n{step.get('answer', 'N/A')}\n\n")
                if step.get('thinking'):
                    f.write(f"Thinking:\n{step.get('thinking', '')}\n\n")
        
        print(f"[SAVED] Pipeline summary: {summary_file}")
    
    def _show_pipeline_summary(self, results: Dict[str, Any]):
        """Display a summary of the pipeline execution."""
        print("\n" + "="*60)
        print("PIPELINE EXECUTION SUMMARY")
        print("="*60)
        print(f"Goal: {results['goal']}")
        print(f"Total Steps: {len(results['steps'])}")
        print("-"*60)
        
        for i, step in enumerate(results['steps'], 1):
            query_type = step.get('query_type', 'N/A')
            answer = step.get('answer', '')
            # Truncate answer for summary
            short_answer = answer[:100] + "..." if len(answer) > 100 else answer
            print(f"\nStep {i} ({query_type}):")
            print(f"  {short_answer}")
        
        print("\n" + "="*60)
        if self.run_dir:
            print(f"Full results saved to: {self.run_dir}")
        print("="*60 + "\n")
    
    def _extract_task_from_answer(self, answer: str) -> Optional[str]:
        """Try to extract a task description from an answer."""
        # Simple extraction - take first sentence or line
        lines = answer.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:
                # Remove common prefixes
                for prefix in ["The next step is to ", "You should ", "First, ", "1. ", "- "]:
                    if line.startswith(prefix):
                        line = line[len(prefix):]
                return line[:100]  # Limit length
        return None
    
    def reset(self):
        """Reset the executor and session."""
        self.chat.reset()
        self.session.reset()


# ============================================================================
# MAIN CHAT INTERFACE
# ============================================================================

def print_banner():
    print("""
====================================================================
   RoboBrain 2.0 PLANNING Chat (ShareRobot-style Templates)
====================================================================

This chat uses planning-focused question templates for robot task
planning, progress tracking, and action prediction.

Planning Query Types:
  * planning          - What's the next step for a goal?
  * planning_context  - Next step given completed tasks
  * planning_remain   - Next N steps to reach goal
  * future            - What happens after a task?
  * success           - Was the task completed?
  * affordance_pos    - Can this task be done now?
  * affordance_neg    - Is this task being done?
  * affordance_gen    - What can be done now?
  * past              - What was the last task?

Session Commands:
  /goal <description>     - Set the planning goal
  /done <task>            - Mark a task as completed
  /current <task>         - Set current task
  /status                 - Show session status
  /pipeline <goal>        - Run full planning pipeline

General Commands:
  /image <path>           - Set a new image
  /thinking on/off        - Toggle thinking mode
  /clear                  - Reset session
  /help                   - Show this help
  /quit                   - Exit

Examples:
  /goal pick up the red cup and place it on the plate
  /done located the red cup
  planning_context
  affordance_pos grasp the cup
====================================================================
""")


def print_query_help():
    """Print help for available query types."""
    print("\n" + "="*60)
    print("AVAILABLE PLANNING QUERY TYPES")
    print("="*60)
    for qtype, info in PLANNING_TEMPLATES.items():
        print(f"\n{qtype}:")
        print(f"  Description: {info['description']}")
        print(f"  Example: {info['templates'][0][:60]}...")
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Planning chat with RoboBrain 2.0")
    parser.add_argument("--image", "-i", type=str, help="Initial image to analyze")
    parser.add_argument("--no-thinking", action="store_true", help="Disable thinking mode")
    args = parser.parse_args()
    
    print_banner()
    
    # Load model
    print("\nLoading RoboBrain model...")
    model, repo_dir = get_model()
    
    # Initialize executor
    executor = PlanningExecutor(model, repo_dir)
    
    # Settings
    enable_thinking = not args.no_thinking
    
    # Set initial image
    if args.image:
        executor.set_image(args.image)
    else:
        print("[INFO] No image set. Use /image <path> to set one.")
    
    print(f"\n[MODE] Thinking: {'ON' if enable_thinking else 'OFF'}")
    print("\nType a query type (e.g., 'planning', 'future') or a custom question!\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye!")
            break
        
        if not user_input:
            continue
        
        # Handle commands
        if user_input.startswith("/"):
            parts = user_input.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""
            
            if cmd in ["/quit", "/exit", "/q"]:
                print("Goodbye!")
                break
            
            elif cmd == "/help":
                print_banner()
            
            elif cmd == "/types":
                print_query_help()
            
            elif cmd == "/image":
                if arg:
                    if pathlib.Path(arg).exists() or arg.startswith("http"):
                        executor.set_image(arg)
                    else:
                        print(f"[ERROR] Image not found: {arg}")
                else:
                    print(f"[IMAGE] Current: {executor.chat.memory.current_image}")
            
            elif cmd == "/goal":
                if arg:
                    executor.session.set_goal(arg)
                else:
                    print(f"[GOAL] Current: {executor.session.goal or 'Not set'}")
            
            elif cmd == "/done":
                if arg:
                    executor.session.add_completed_task(arg)
                else:
                    print("Usage: /done <task description>")
            
            elif cmd == "/current":
                if arg:
                    executor.session.set_current_task(arg)
                else:
                    print(f"[CURRENT] {executor.session.current_task or 'Not set'}")
            
            elif cmd == "/status":
                executor.session.show_status()
            
            elif cmd == "/pipeline":
                if not executor.chat.memory.current_image:
                    print("[WARNING] No image set. Use /image <path> first.")
                    continue
                goal = arg or executor.session.goal
                if not goal:
                    print("Usage: /pipeline <goal> or set goal with /goal first")
                    continue
                results = executor.run_planning_pipeline(goal, enable_thinking=enable_thinking)
                print(f"\n[PIPELINE COMPLETE] {len(results['steps'])} steps executed")
            
            elif cmd == "/thinking":
                if arg.lower() == "on":
                    enable_thinking = True
                    print("[MODE] Thinking: ON")
                elif arg.lower() == "off":
                    enable_thinking = False
                    print("[MODE] Thinking: OFF")
                else:
                    print(f"[MODE] Thinking: {'ON' if enable_thinking else 'OFF'}")
            
            elif cmd == "/clear":
                executor.reset()
                print("[CLEARED] Session reset")
            
            else:
                print(f"[ERROR] Unknown command: {cmd}. Type /help for available commands.")
            
            continue
        
        # Check image
        if not executor.chat.memory.current_image:
            print("[WARNING] No image set. Use /image <path> to set one first.")
            continue
        
        # Parse query type and optional arguments
        parts = user_input.split(maxsplit=1)
        query_input = parts[0].lower()
        extra_arg = parts[1] if len(parts) > 1 else ""
        
        # Map short names to full query types
        query_map = {
            "planning": "planning",
            "plan": "planning",
            "next": "planning",
            "planning_context": "planning_with_context",
            "context": "planning_with_context",
            "planning_remain": "planning_remaining",
            "remain": "planning_remaining",
            "remaining": "planning_remaining",
            "future": "future_prediction",
            "predict": "future_prediction",
            "success": "success_detection",
            "done": "success_detection",
            "affordance_pos": "affordance_positive",
            "can": "affordance_positive",
            "feasible": "affordance_positive",
            "affordance_neg": "affordance_negative",
            "doing": "affordance_negative",
            "affordance_gen": "generative_affordance",
            "available": "generative_affordance",
            "what_can": "generative_affordance",
            "past": "past_description",
            "last": "past_description",
            "previous": "past_description"
        }
        
        query_type = query_map.get(query_input)
        
        if query_type:
            # Known query type
            kwargs = {}
            if extra_arg:
                # Use extra argument as task or goal depending on query type
                if query_type in ["success_detection", "affordance_positive", "affordance_negative"]:
                    kwargs["task"] = extra_arg
                elif query_type in ["planning", "planning_with_context", "planning_remaining"]:
                    kwargs["goal"] = extra_arg
                elif query_type == "future_prediction":
                    kwargs["last_task"] = extra_arg
            
            result = executor.ask_planning(query_type, enable_thinking=enable_thinking, **kwargs)
        else:
            # Custom query - send directly
            result = executor.ask_custom(user_input, enable_thinking=enable_thinking)
        
        print()


if __name__ == "__main__":
    main()
