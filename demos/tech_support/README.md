# Tech Support Demo

This demo shows how **Stinger** protects AI conversations in real-world scenarios.

## What You'll See

The demo presents realistic tech support conversations and shows how Stinger:
- ✅ **Allows** normal, helpful conversations
- ❌ **Blocks** dangerous requests (hacking, harmful code)
- ⚠️ **Flags** sensitive content (personal info) for human review
- 🛡️ **Protects** both users and AI systems

## Demo Files

### `simple_demo.py` - Real-World Scenarios
Shows 5 realistic tech support scenarios with detailed safety analysis:
- Normal password reset request
- User asking for hacking code
- Personal information accidentally shared
- Toxic user message
- AI trying to generate dangerous code

**Focus**: Demonstrates Stinger's comprehensive protection capabilities.

### `one_liner_demo.py` - Minimal Code
Shows the absolute minimum code needed to use Stinger:
```python
user_result = pipeline.check_input(user_message)
ai_result = pipeline.check_output(ai_response)
```

**Focus**: Proves Stinger is simple to integrate - just two lines of code.

### `demo.py` - Interactive LLM Screening
Screens real LLM conversations using prompts from `prompts.txt`:
- Loads prompts from file
- Calls actual LLM (or mock if no API key)
- Screens both input and output
- Shows real-time safety analysis

**Focus**: Demonstrates Stinger in a real AI conversation workflow.

### `demo_utils.py` - All Boilerplate
Handles all the non-Stinger functionality:
- Pretty printing and formatting
- LLM calls (real or mock)
- File loading
- Presentation logic

**Focus**: Keeps main demos focused purely on Stinger functionality.

## Running the Demos

```bash
# Run the comprehensive demo
python3 simple_demo.py

# Run the minimal demo
python3 one_liner_demo.py

# Run the interactive LLM demo
python3 demo.py
```

## Demo Structure

Each demo follows this pattern:
1. **Initialize** Stinger with configuration
2. **Define** realistic scenarios (or load from file)
3. **Check** both user input and AI output
4. **Show** what happens (allowed/blocked/flagged)
5. **Summarize** the protection results

The demos use `demo_utils.py` for all presentation logic, keeping the main code focused on demonstrating Stinger's core functionality.

## What Makes This Demo Great

✅ **Real-world scenarios** - Not contrived examples  
✅ **Clear outcomes** - Shows exactly what gets blocked/flagged  
✅ **Simple code** - Focuses on Stinger usage, not presentation  
✅ **Natural flow** - Reads like actual conversations  
✅ **Comprehensive** - Covers multiple safety concerns  
✅ **Interactive** - Can use real LLMs or mock responses  
✅ **Modular** - All boilerplate separated into utils  

The demos prove that Stinger is both **powerful** (catches real threats) and **simple** (easy to integrate).

---
This demo is part of Stinger Phase 5c and is intended for system evaluation and developer experience review. 