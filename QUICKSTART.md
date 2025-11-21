# Quick Start Guide - Structured Cognitive Loop (SCL) Experiment

## 5-Minute Setup

### Step 1: Verify Python

```bash
python --version  # Should be 3.8 or higher
```

### Step 2: Run the Experiment

```bash
python run_experiment.py
```

That's it! The experiment will:
- ✅ Check weather in San Francisco, Miami, and Atlanta
- ✅ Apply conditional branching logic via R-CCAM loop
- ✅ Execute actions through structured modules
- ✅ Generate complete audit logs

### Expected Runtime
- **Duration**: 1-2 seconds
- **Loops**: 4-6 CCAM cycles
- **Output files**: 2 JSON files

### Verify Success

Look for this output:
```
✅ Experiment complete!

Generated files:
  • experiment_results.json      - Full audit log
  • paper_figure_trace.json      - Simplified trace (Figure 2 format)
```

## Understanding the Output

### File: experiment_results.json

Complete execution trace with:
- Every Cognition decision
- Every Control validation  
- Every Action execution
- Every Memory update

**Sample structure:**
```json
{
  "experiment": "Weather-Based Travel Planning",
  "architecture": "Structured Cognitive Loop (R-CCAM)",
  "task": "When the base temperature is 55°F...",
  "policies": [
    "must_cite_stored_evidence",
    "no_final_answer_without_control_pass",
    "single_final_action"
  ],
  "execution_log": [
    {
      "loop_id": "R-001",
      "module": "Retrieval",
      "timestamp": "2024-01-15T10:30:00Z",
      ...
    }
  ]
}
```

### File: paper_figure_trace.json

Simplified format matching Figure 2 from the paper:
```json
{
  "task": "Check San Francisco, Miami, and Atlanta weather...",
  "policies": ["must_cite_stored_evidence", ...],
  "log": [
    {
      "loop": "San Francisco",
      "phases": ["Cognition", "Control", "Action", "Memory"],
      "res": {"city": "San Francisco", "temp_F": 64, ...}
    }
  ]
}
```

## Architecture Components

### R (Retrieval)
- **Called**: Once at start
- **Purpose**: Gather initial evidence and decompose task
- **Output**: Retrieval plan stored in Memory

### CCAM Loop
The following four modules repeat until task completion:

#### C (Cognition)
- **Purpose**: Generate reasoning and propose actions
- **Constraints**: Governed by Metaprompt
- **Output**: Proposed action with evidence citations

#### C (Control)
- **Purpose**: Validate proposed actions
- **Mechanism**: Check against symbolic rules
- **Output**: PASS/FAIL validation

#### A (Action)
- **Purpose**: Execute validated tools
- **Safety**: Only runs after Control approval
- **Output**: Tool execution results

#### M (Memory)
- **Purpose**: Store state and evidence
- **Persistence**: Maintains across all loops
- **Output**: Audit trail entries

## Troubleshooting

### Error: "ModuleNotFoundError"

**Problem**: Missing Python file

**Solution**: Ensure all 4 files are in the same directory:
- scl_core.py
- mock_tools.py
- mock_cognition.py
- run_experiment.py

### Error: "No module named 'json'"

**Problem**: Using Python < 3.0

**Solution**: Upgrade Python to 3.8+

### Infinite Loop

**Problem**: Mock cognition engine stuck

**Solution**: Check max_loops setting in run_experiment.py:
```python
scl_system = StructuredCognitiveLoop(
    ...
    max_loops=20  # Increase if needed
)
```

### Policy Violations

**Problem**: High number of violations in summary

**Possible causes**:
- Cognition not citing evidence
- Missing Control validation
- Redundant tool calls

**Solution**: Check Metaprompt rules and Cognition logic

## Modifying the Experiment

### Change Base Temperature

In `run_experiment.py`, modify the task string:
```python
task = """
When the base temperature is 60°F,  # Changed from 55°F
check the weather...
"""
```

### Add New Cities

1. Update task description with new cities
2. Add city mappings in mock_cognition.py:
```python
city_map = {
    "SF_weather": "San Francisco",
    "Miami_weather": "Miami",
    "Atlanta_weather": "Atlanta",
    "Seattle_weather": "Seattle"  # New city
}
```
3. Update retrieval plan in scl_core.py

### Test Different Scenarios

Create scenario variants:
```python
# Scenario A: All cities cold
def run_cold_scenario():
    # Modify base_temperature to 70°F
    # All cities will be below threshold
    
# Scenario B: Mixed conditions  
def run_mixed_scenario():
    # One city hot, two cold
```

## Understanding the Logs

### Trace Structure

Each loop trace contains:
```python
{
  "loop_id": "CCAM-003",        # Unique identifier
  "timestamp": "...",            # ISO format time
  "module": "Action",            # Which module
  "input_state": {...},          # Input to module
  "output_state": {...},         # Output from module
  "decision": "...",             # Optional decision
  "validation_result": True,     # For Control module
  "evidence_refs": [...]         # Citations
}
```

### Module Flow

1. **Retrieval** (R-001): Task parsing
2. **Cognition** (CCAM-001): "Need SF weather"
3. **Control** (CTL-001): Validates
4. **Action** (ACT-001): Calls get_weather
5. **Memory**: Logs everything
6. Repeat steps 2-5 for Miami, Atlanta
7. **Cognition** (CCAM-004): Makes decision
8. **Control** (CTL-004): Validates final action
9. **Action** (ACT-004): Executes (email/image)
10. Complete

## Next Steps

### For Researchers

1. **Replicate**: Run experiment multiple times
2. **Extend**: Add your own tools and scenarios
3. **Compare**: Test against ReAct, Reflexion
4. **Measure**: Track policy violations and success rates
5. **Contribute**: Share results and improvements

### For Developers

1. **Real LLM**: Replace MockCognitionEngine with GPT-4/Claude
```python
from openai import OpenAI
client = OpenAI(api_key="your-key")

def gpt4_engine(prompt, context):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return parse_json(response.choices[0].message.content)
```

2. **Real APIs**: Use actual weather services
```python
import requests

def get_weather(city: str):
    api_key = "your-weather-api-key"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(url)
    return parse_weather(response.json())
```

3. **Deploy**: Use Streamlit for web interface
```bash
pip install streamlit
streamlit run scl_app.py
```

### For Paper Validation

The experiment validates three claims from Section 4:

**Claim 1**: Modular decomposition improves reliability
- **Metric**: Policy violation rate
- **Expected**: <5% violations

**Claim 2**: Soft Symbolic Control prevents errors
- **Metric**: Redundant tool calls
- **Expected**: 0 redundant calls

**Claim 3**: Memory enables transparency
- **Metric**: Complete audit trail
- **Expected**: 100% trace coverage

## Advanced Usage

### Custom Metaprompt

Create domain-specific rules:
```python
class MedicalMetaPrompt(MetaPrompt):
    def __init__(self):
        super().__init__()
        self.rules.update({
            "require_evidence_quality_check": True,
            "mandate_differential_diagnosis": True,
            "enforce_treatment_guidelines": True
        })
```

### Multi-Agent SCL

Run multiple SCL instances:
```python
researcher_scl = StructuredCognitiveLoop(...)
reviewer_scl = StructuredCognitiveLoop(...)

# Researcher generates
result = researcher_scl.run(research_task)

# Reviewer validates
review = reviewer_scl.run(f"Review: {result}")
```

### Visualization

Generate execution graphs:
```python
import matplotlib.pyplot as plt

def visualize_loops(audit_report):
    loops = [t for t in audit_report["log"] if "CCAM" in t["loop_id"]]
    modules = [t["module"] for t in loops]
    
    plt.figure(figsize=(12, 6))
    plt.plot(range(len(modules)), modules, marker='o')
    plt.title("SCL Execution Flow")
    plt.xlabel("Step")
    plt.ylabel("Module")
    plt.show()
```

## Resources

- **Paper**: "Structured Cognitive Loop: Bridging Symbolic Control and Neural Reasoning in LLM Agents"
- **Live Demo**: https://scl-travel-planner.streamlit.app/
- **GitHub**: [Your repository URL]
- **Contact**: enkiluv@gmail.com

## Support

Having issues? Check:
1. Python version (3.8+)
2. All files present
3. No syntax errors
4. max_loops set appropriately

Still stuck? Open an issue or contact the author.

---

**Happy experimenting with Structured Cognitive Loop!** 🚀
