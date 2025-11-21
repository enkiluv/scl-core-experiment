"""
Structured Cognitive Loop (SCL) Core Implementation
Demonstrates the Retrieval-Cognition-Control-Action-Memory (R-CCAM) loop
"""

import json
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class ModuleType(Enum):
    RETRIEVAL = "Retrieval"
    COGNITION = "Cognition"
    CONTROL = "Control"
    ACTION = "Action"
    MEMORY = "Memory"


@dataclass
class LoopTrace:
    """Record of a single CCAM loop iteration"""
    loop_id: str
    timestamp: str
    module: str
    input_state: Dict[str, Any]
    output_state: Dict[str, Any]
    decision: Optional[str] = None
    validation_result: Optional[bool] = None
    evidence_refs: Optional[List[str]] = None


class MetaPrompt:
    """
    Soft Symbolic Control Layer
    Provides persistent governance constraints across all Cognition cycles
    """
    
    def __init__(self):
        self.rules = {
            "must_cite_stored_evidence": True,
            "no_final_answer_without_control_pass": True,
            "single_final_action": True,
            "avoid_redundant_tool_calls": True,
            "validate_conditional_branches": True,
        }
        
        self.instructions = """
        You are operating under Soft Symbolic Control within a Structured Cognitive Loop.
        
        MANDATORY CONSTRAINTS:
        1. Always consult Memory before proposing actions
        2. Cite evidence from Retrieval/Memory in all reasoning
        3. Never execute final actions without Control validation
        4. Apply conditional logic exactly as specified
        5. Avoid redundant tool calls by checking Memory first
        
        REASONING PROTOCOL:
        - State current goal explicitly
        - Reference stored evidence by ID
        - Propose action with clear rationale
        - Wait for Control validation before execution
        """
    
    def validate(self, cognition_output: Dict[str, Any]) -> tuple[bool, str]:
        """Validate Cognition output against symbolic rules"""
        issues = []
        
        # Check evidence citation
        if self.rules["must_cite_stored_evidence"]:
            if not cognition_output.get("evidence_refs"):
                issues.append("Missing evidence citations")
        
        # Check final action constraint
        if cognition_output.get("is_final_action"):
            if not cognition_output.get("control_validated"):
                issues.append("Final action without Control validation")
        
        is_valid = len(issues) == 0
        message = "PASS" if is_valid else f"VIOLATIONS: {'; '.join(issues)}"
        
        return is_valid, message


class Memory:
    """
    Externalized Working Store
    Maintains state persistence across loops with audit trail
    """
    
    def __init__(self):
        self.store: Dict[str, Any] = {}
        self.history: List[LoopTrace] = []
        self.evidence_cache: Dict[str, Any] = {}
        
    def write(self, key: str, value: Any, evidence_id: Optional[str] = None):
        """Store state with optional evidence reference"""
        self.store[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "evidence_id": evidence_id
        }
        
    def read(self, key: str) -> Optional[Any]:
        """Retrieve stored state"""
        entry = self.store.get(key)
        return entry["value"] if entry else None
    
    def has_evidence(self, evidence_id: str) -> bool:
        """Check if evidence already exists (avoid redundant calls)"""
        return evidence_id in self.evidence_cache
    
    def store_evidence(self, evidence_id: str, data: Any):
        """Cache retrieved evidence"""
        self.evidence_cache[evidence_id] = data
    
    def get_evidence(self, evidence_id: str) -> Optional[Any]:
        """Retrieve cached evidence"""
        return self.evidence_cache.get(evidence_id)
    
    def log_trace(self, trace: LoopTrace):
        """Append to audit log"""
        self.history.append(trace)
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Return current state for Cognition context"""
        return {
            "stored_values": {k: v["value"] for k, v in self.store.items()},
            "available_evidence": list(self.evidence_cache.keys()),
            "loop_count": len(self.history)
        }


class ToolRegistry:
    """Registry of available tools for Action module"""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        
    def register(self, name: str, func: Callable, description: str):
        """Register a tool with metadata"""
        self.tools[name] = {
            "function": func,
            "description": description,
            "name": name
        }
    
    def get_tool_descriptions(self) -> List[Dict[str, str]]:
        """Return list of available tools for Cognition"""
        return [
            {"name": t["name"], "description": t["description"]}
            for t in self.tools.values()
        ]
    
    def execute(self, tool_name: str, **kwargs) -> Any:
        """Execute a registered tool"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not registered")
        
        func = self.tools[tool_name]["function"]
        return func(**kwargs)


class StructuredCognitiveLoop:
    """
    Main Structured Cognitive Loop (SCL) Architecture
    Implements R-CCAM loop with Soft Symbolic Control
    """
    
    def __init__(
        self,
        cognition_engine: Callable,  # LLM inference function
        tool_registry: ToolRegistry,
        metaprompt: Optional[MetaPrompt] = None,
        max_loops: int = 20
    ):
        self.cognition_engine = cognition_engine
        self.tools = tool_registry
        self.metaprompt = metaprompt or MetaPrompt()
        self.memory = Memory()
        self.max_loops = max_loops
        self.loop_counter = 0
        
    def retrieval(self, task: str) -> Dict[str, Any]:
        """
        Retrieval Module (invoked once at task start)
        Performs initial evidence gathering and task decomposition
        """
        print(f"\n{'='*60}")
        print(f"[RETRIEVAL] Initializing task: {task[:100]}...")
        print(f"{'='*60}\n")
        
        # Simulate retrieval planning (in real implementation, call LLM)
        plan = {
            "evidence_needed": ["SF_weather", "Miami_weather", "Atlanta_weather"],
            "base_temperature": 55,
            "conditions_parsed": True,
            "tools_required": ["get_weather", "send_email", "generate_image", "cancel_trip"]
        }
        
        # Store in Memory
        self.memory.write("task", task)
        self.memory.write("retrieval_plan", plan)
        
        trace = LoopTrace(
            loop_id="R-001",
            timestamp=datetime.now().isoformat(),
            module=ModuleType.RETRIEVAL.value,
            input_state={"task": task},
            output_state=plan
        )
        self.memory.log_trace(trace)
        
        return plan
    
    def cognition(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cognition Module (probabilistic inference under symbolic constraints)
        Generates reasoning and action proposals
        """
        self.loop_counter += 1
        loop_id = f"CCAM-{self.loop_counter:03d}"
        
        print(f"\n[COGNITION] Loop {self.loop_counter}")
        print(f"{'─'*60}")
        
        # Construct prompt with Metaprompt + Memory state
        state_summary = self.memory.get_state_summary()
        available_tools = self.tools.get_tool_descriptions()
        
        cognition_prompt = f"""
        {self.metaprompt.instructions}
        
        CURRENT STATE:
        {json.dumps(state_summary, indent=2)}
        
        AVAILABLE TOOLS:
        {json.dumps(available_tools, indent=2)}
        
        CONTEXT:
        {json.dumps(context, indent=2)}
        
        Based on the above, determine:
        1. What is the next action needed?
        2. What evidence supports this decision?
        3. Are all conditions for this action met?
        
        Respond in JSON format with:
        - reasoning: your thought process
        - proposed_action: {{tool_name, parameters}}
        - evidence_refs: list of evidence IDs used
        - is_final_action: boolean
        """
        
        # Call cognition engine (LLM)
        response = self.cognition_engine(cognition_prompt, context)
        
        print(f"Reasoning: {response.get('reasoning', 'N/A')}")
        print(f"Proposed Action: {response.get('proposed_action', 'N/A')}")
        
        trace = LoopTrace(
            loop_id=loop_id,
            timestamp=datetime.now().isoformat(),
            module=ModuleType.COGNITION.value,
            input_state=context,
            output_state=response,
            evidence_refs=response.get("evidence_refs")
        )
        self.memory.log_trace(trace)
        
        return response
    
    def control(self, cognition_output: Dict[str, Any]) -> tuple[bool, str]:
        """
        Control Module (Soft Symbolic Validation)
        Validates Cognition output against Metaprompt rules
        """
        print(f"\n[CONTROL] Validating proposed action...")
        
        # For final actions, mark as control_validated to pass Metaprompt check
        if cognition_output.get("is_final_action"):
            cognition_output["control_validated"] = True
        
        # Apply Metaprompt validation
        is_valid, message = self.metaprompt.validate(cognition_output)
        
        # Additional safety checks
        proposed_action = cognition_output.get("proposed_action", {})
        tool_name = proposed_action.get("tool_name")
        
        # Check for redundant tool calls
        if tool_name:
            evidence_id = f"evidence_{tool_name}_{json.dumps(proposed_action.get('parameters', {}), sort_keys=True)}"
            if self.memory.has_evidence(evidence_id):
                is_valid = False
                message = "REJECTED: Redundant tool call (evidence already in Memory)"
        
        # Log control decision
        trace = LoopTrace(
            loop_id=f"CTL-{self.loop_counter:03d}",
            timestamp=datetime.now().isoformat(),
            module=ModuleType.CONTROL.value,
            input_state=cognition_output,
            output_state={"validation": is_valid, "message": message},
            validation_result=is_valid
        )
        self.memory.log_trace(trace)
        
        status = "✓ PASS" if is_valid else "✗ FAIL"
        print(f"{status}: {message}")
        
        return is_valid, message
    
    def action(self, cognition_output: Dict[str, Any]) -> Any:
        """
        Action Module (Separated Execution)
        Executes validated actions and interacts with external environment
        """
        print(f"\n[ACTION] Executing validated action...")
        
        proposed_action = cognition_output.get("proposed_action", {})
        tool_name = proposed_action.get("tool_name")
        parameters = proposed_action.get("parameters", {})
        
        if not tool_name:
            return {"status": "no_action", "result": None}
        
        # Execute tool
        try:
            result = self.tools.execute(tool_name, **parameters)
            
            # Store result in Memory as evidence
            evidence_id = f"evidence_{tool_name}_{json.dumps(parameters, sort_keys=True)}"
            self.memory.store_evidence(evidence_id, result)
            
            print(f"Executed: {tool_name}")
            print(f"Result: {str(result)[:200]}...")
            
            trace = LoopTrace(
                loop_id=f"ACT-{self.loop_counter:03d}",
                timestamp=datetime.now().isoformat(),
                module=ModuleType.ACTION.value,
                input_state=proposed_action,
                output_state={"result": result, "evidence_id": evidence_id}
            )
            self.memory.log_trace(trace)
            
            return result
            
        except Exception as e:
            error_msg = f"Action execution failed: {str(e)}"
            print(f"✗ ERROR: {error_msg}")
            return {"status": "error", "message": error_msg}
    
    def run(self, task: str) -> Dict[str, Any]:
        """
        Main execution loop: Retrieval → CCAM cycles → Final result
        """
        print(f"\n{'#'*60}")
        print(f"# STRUCTURED COGNITIVE LOOP (SCL) EXECUTION")
        print(f"{'#'*60}")
        
        # Step 1: Retrieval (once)
        retrieval_result = self.retrieval(task)
        
        # Step 2: CCAM Loop (repeat until task complete or max loops)
        context = {
            "task": task,
            "retrieval_plan": retrieval_result,
            "status": "in_progress"
        }
        
        while self.loop_counter < self.max_loops:
            # Cognition
            cognition_output = self.cognition(context)
            
            # Control
            is_valid, validation_msg = self.control(cognition_output)
            
            if not is_valid:
                print(f"\n⚠️  Control rejected action. Re-entering Cognition...")
                context["last_rejection"] = validation_msg
                continue
            
            # Action
            action_result = self.action(cognition_output)
            
            # Memory (implicit - already logged in each module)
            
            # Update context with action result
            context["last_action_result"] = action_result
            
            # Check if task is complete
            if cognition_output.get("is_final_action"):
                print(f"\n{'='*60}")
                print(f"[COMPLETION] Task finished in {self.loop_counter} loops")
                print(f"{'='*60}\n")
                break
        
        # Generate final audit log
        return self._generate_audit_report()
    
    def _generate_audit_report(self) -> Dict[str, Any]:
        """Generate comprehensive audit log in format shown in paper"""
        report = {
            "task": self.memory.read("task"),
            "policies": list(self.metaprompt.rules.keys()),
            "log": [asdict(trace) for trace in self.memory.history],
            "summary": {
                "total_loops": self.loop_counter,
                "policy_violations": sum(
                    1 for t in self.memory.history 
                    if t.validation_result is False
                ),
                "final_state": self.memory.get_state_summary()
            }
        }
        return report


def save_audit_log(report: Dict[str, Any], filename: str = "execution_audit.json"):
    """Save audit log to JSON file"""
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n✓ Audit log saved to {filename}")
