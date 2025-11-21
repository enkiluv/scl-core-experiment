# Structured Cognitive Loop (SCL) Experiment: Weather-Based Travel Planning

This repository contains the experimental implementation for the paper **"Structured Cognitive Loop: Bridging Symbolic Control and Neural Reasoning in LLM Agents"** by Myung Ho Kim (JEI University).

## Overview

This experiment demonstrates the core architectural principles of **Structured Cognitive Loop (SCL)**, a hybrid intelligence framework that implements:

1. **Modular Decomposition** - Explicit separation of Retrieval, Cognition, Control, Action, and Memory
2. **Soft Symbolic Control** - Adaptive governance through Metaprompt constraints  
3. **Transparent State Management** - Complete audit trails via Memory logging

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                    METAPROMPT                        │
│         (Soft Symbolic Control Layer)                │
└──────────────────────────────────────────────────────┘
                         ↓
           ┌─────────────────────────┐
           │   RETRIEVAL (R - Once)  │
           └──────────┬──────────────┘
                      ↓
           ┌──────────────────────────┐
           │   CCAM LOOP (Repeat)     │
           │  ┌────────────────────┐  │
           │  │    COGNITION (C)   │←─┼─── Metaprompt constraints
           │  └─────────┬──────────┘  │
           │            ↓             │
           │  ┌────────────────────┐  │
           │  │     CONTROL (C)    │  │
           │  └─────────┬──────────┘  │
           │            ↓             │
           │  ┌────────────────────┐  │
           │  │     ACTION (A)     │←─┼─── External tools
           │  └─────────┬──────────┘  │
           │            ↓             │
           │  ┌────────────────────┐  │
           │  │     MEMORY (M)     │  │
           │  └────────────────────┘  │
           └──────────────────────────┘
                      ↓
           ┌──────────────────────────┐
           │      AUDIT LOG           │
           └──────────────────────────┘
```

## R-CCAM Loop Explained

The **R-CCAM** structure represents:
- **R (Retrieval)**: Invoked once at the beginning to gather initial evidence and decompose the task
- **C (Cognition)**: Probabilistic reasoning under symbolic constraints
- **C (Control)**: Validation against Metaprompt rules
- **A (Action)**: Separated, accountable execution of validated actions
- **M (Memory)**: Persistent state storage with complete audit trail

The CCAM loop repeats until the task is complete or maximum iterations are reached.

## Scenario

The experiment implements the weather-based travel planning task described in Section 4.2 of the paper:

> "When the base temperature is 55°F, check the weather in San Francisco, Miami, and Atlanta. If all three regions are above the reference temperature, decide to travel to the coolest one and draw an image. If only two regions are above, choose the cooler one among them and send an email. If only one region is above, travel to that place. If all three regions are below the reference temperature, cancel the trip and recommend a list of convenience store snacks to enjoy at home."

## Files

```
scl_core.py              - Core R-CCAM loop implementation
mock_tools.py            - Tool registry and mock implementations
mock_cognition.py        - Mock LLM cognition engine
run_experiment.py        - Main experiment runner
README.md                - This file
requirements.txt         - Python dependencies
```

## Installation

### Requirements
- Python 3.8+
- No external dependencies (uses only standard library for basic functionality)

### Setup

```bash
# Clone or download the repository
git clone https://github.com/enkiluv/scl-core-experiment.git
cd scl-experiment

# Or if using the standalone files:
# Just ensure all 4 Python files are in the same directory
```

## Running the Experiment

### Basic Execution

```bash
python run_experiment.py
```

This will:
1. Initialize the SCL system with registered tools
2. Execute the weather-based travel planning task
3. Generate audit logs in JSON format
4. Print summary statistics

### Expected Output

```
================================================================================
STRUCTURED COGNITIVE LOOP (SCL) EXPERIMENT
Weather-Based Travel Planning
================================================================================

############################################################
# STRUCTURED COGNITIVE LOOP (SCL) EXECUTION
############################################################

[RETRIEVAL] Initializing task...

[COGNITION] Loop 1
──────────────────────────
Reasoning: Need weather data for San Francisco...
Proposed Action: {'tool_name': 'get_weather', 'parameters': {'city': 'San Francisco'}}

[CONTROL] Validating proposed action...
✓ PASS: PASS

[ACTION] Executing validated action...
Executed: get_weather
Result: {'city': 'San Francisco', 'temperature_f': 60, 'condition': 'Partly Cloudy'}

... (additional loops) ...

[COMPLETION] Task finished in 4 loops
```

### Generated Files

After execution, the following files are created:

- **experiment_results.json** - Complete audit log with all loop traces
- **paper_figure_trace.json** - Simplified trace in the format shown in Figure 2 of the paper

## Key Features Demonstrated

### 1. Modular Decomposition

Each module has a distinct responsibility:
- **Retrieval (R)**: Initial evidence gathering and task decomposition (invoked once)
- **Cognition (C)**: Probabilistic reasoning under symbolic constraints  
- **Control (C)**: Validation against Metaprompt rules
- **Action (A)**: Separated, accountable execution
- **Memory (M)**: Persistent state with audit logging

### 2. Soft Symbolic Control

The Metaprompt enforces rules such as:
```python
{
    "must_cite_stored_evidence": True,
    "no_final_answer_without_control_pass": True,
    "single_final_action": True,
    "avoid_redundant_tool_calls": True,
    "validate_conditional_branches": True
}
```

These constraints guide Cognition **without replacing** its probabilistic reasoning.

### 3. Transparent State Management

Every loop iteration is logged:
```json
{
  "loop_id": "CCAM-003",
  "timestamp": "2024-01-15T10:30:45Z",
  "module": "Action",
  "input_state": {"tool_name": "get_weather", ...},
  "output_state": {"result": {"temperature_f": 60, ...}},
  "evidence_refs": ["api:wx-001"]
}
```

This enables **post-hoc auditing** and **explainability**.

## Customization

### Adding New Tools

Register tools in `run_experiment.py`:

```python
tool_registry.register(
    "your_tool_name",
    your_function,
    "Description of what this tool does"
)
```

### Modifying Metaprompt Rules

Edit `MetaPrompt` class in `scl_core.py`:

```python
self.rules = {
    "your_custom_rule": True,
    ...
}
```

### Changing the Task

Modify the `task` string in `run_experiment.py` with your scenario.

## Replacing Mock Components

For production use, replace mock components with real implementations:

### Real LLM Integration

Replace `MockCognitionEngine` with actual LLM API calls:

```python
def real_cognition_engine(prompt: str, context: Dict) -> Dict:
    # Call GPT-4/5, Claude, or other LLM
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}]
    )
    return parse_response(response)
```

### Real Tools

Replace mock tools with actual API calls:

```python
def get_weather(city: str) -> Dict:
    response = requests.get(
        f"https://api.weather.com/v1/current?city={city}",
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    return response.json()
```

## Validation Metrics

The experiment tracks:

- **Total CCAM loops**: Number of cognition-control-action-memory cycles
- **Policy violations**: Count of Metaprompt rule violations  
- **Success rate**: `(1 - violations / loops) × 100%`
- **Evidence persistence**: All tool results cached in Memory

## Comparison with Other Approaches

| Feature | ReAct/AutoGPT | MemGPT/TME | **SCL (R-CCAM)** |
|---------|---------------|------------|------------------|
| Modular architecture | ❌ Entangled | ⚠️ Partial | ✅ Full R-CCAM |
| Symbolic constraints | ❌ None | ❌ None | ✅ Metaprompt |
| Memory integration | ❌ Token-based | ✅ External | ✅ + Control loop |
| Audit trail | ❌ Limited | ⚠️ Storage only | ✅ Complete |
| Redundancy prevention | ❌ No | ⚠️ Heuristic | ✅ Control-enforced |

## Extending to Tier 2 and Tier 3

This Tier 1 implementation can be extended:

**Tier 2** - Multi-model, multi-language:
- Test across GPT-4, Claude, Llama
- Evaluate in non-English languages
- Compare architectural robustness

**Tier 3** - Multimodal:
- Add vision tools (image analysis)
- Include audio processing
- Test cross-modal reasoning

## Citation

If you use this code in your research, please cite:

```bibtex
@techreport{kim2025scl,
  title={Structured Cognitive Loop: Bridging Symbolic Control and Neural Reasoning in LLM Agents},
  author={Kim, Myung Ho},
  institution={JEI University},
  year={2025}
}
```

## Live Demo

See the full implementation in action at:
https://scl-travel-planner.streamlit.app/

## Contact

For questions or collaborations:
- Author: Myung Ho Kim
- Email: enkiluv@gmail.com  
- Institution: JEI University
- ORCID: 0009-0001-3709-7622

## License

MIT License - See LICENSE file for details

## Acknowledgments

This work builds on:
- Expert Systems tradition (MYCIN, XCON)
- Cognitive Architectures (ACT-R, CLARION, Soar)
- Modern LLM agents (ReAct, Reflexion)
- Information geometry (Amari, 1985)

---

**Note**: This is a research prototype demonstrating architectural principles. For production use, integrate with real LLMs, robust error handling, and security measures.
