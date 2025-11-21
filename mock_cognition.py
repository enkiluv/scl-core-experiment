"""
Mock Cognition Engine (LLM Simulator)
Demonstrates reasoning under Soft Symbolic Control in Structured Cognitive Loop (SCL)
In production, replace with actual LLM API calls
"""

import json
import re
from typing import Dict, Any, List


class MockCognitionEngine:
    """
    Simulates LLM reasoning for Structured Cognitive Loop
    Implements rule-following behavior as described in the paper
    """
    
    def __init__(self):
        self.call_count = 0
        self.collected_weather = []  # Track collected weather data
        
    def __call__(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main inference method
        Parses state and generates next action following Metaprompt constraints
        """
        self.call_count += 1
        
        # Extract current state from context
        state_summary = context.get("retrieval_plan", {})
        last_action_result = context.get("last_action_result", {})
        
        # Track collected weather by checking last_action_result
        if last_action_result and "temperature_f" in last_action_result:
            city = last_action_result.get("city")
            temp = last_action_result.get("temperature_f")
            
            # Only add if not already collected (avoid duplicates)
            if city and temp is not None:
                existing_cities = [w.get("city") for w in self.collected_weather]
                if city not in existing_cities:
                    self.collected_weather.append(last_action_result)
                    print(f"   [Cognition Engine] Stored weather for {city}: {temp}°F")
        
        # Determine current phase of task
        evidence_needed = state_summary.get("evidence_needed", [])
        base_temp = state_summary.get("base_temperature", 55)
        
        # Phase 1: Gather weather evidence
        if len(self.collected_weather) < 3:
            return self._generate_weather_query(evidence_needed, self.collected_weather)
        
        # Phase 2: Analyze and make decision
        return self._generate_decision(self.collected_weather, base_temp)
    
    def _generate_weather_query(
        self, 
        cities_needed: List[str], 
        already_collected: List[Dict]
    ) -> Dict[str, Any]:
        """Generate next weather query action"""
        collected_cities = [w.get("city") for w in already_collected]
        
        # Map evidence keys to actual city names
        city_map = {
            "SF_weather": "San Francisco",
            "Miami_weather": "Miami",
            "Atlanta_weather": "Atlanta"
        }
        
        # Find next city to query
        for city_key in cities_needed:
            city_name = city_map.get(city_key, city_key)
            if city_name not in collected_cities:
                return {
                    "reasoning": f"Need weather data for {city_name}. Consulting Memory shows no existing data for this city. Will query weather API.",
                    "proposed_action": {
                        "tool_name": "get_weather",
                        "parameters": {"city": city_name}
                    },
                    "evidence_refs": ["retrieval_plan"],
                    "is_final_action": False,
                    "control_validated": False
                }
        
        # All weather collected, move to decision
        return {
            "reasoning": "All weather data collected. Ready to analyze and make travel decision.",
            "proposed_action": None,
            "evidence_refs": ["weather_sf", "weather_miami", "weather_atlanta"],
            "is_final_action": False
        }
    
    def _generate_decision(
        self, 
        weather_data: List[Dict[str, Any]], 
        base_temp: float
    ) -> Dict[str, Any]:
        """
        Generate final decision based on collected weather
        Implements conditional logic from task specification
        """
        print(f"   [Cognition Engine] Making decision with {len(weather_data)} cities' data")
        
        # Use actually collected weather data
        if len(weather_data) < 3:
            return {
                "reasoning": "Not enough weather data collected yet",
                "proposed_action": None,
                "evidence_refs": [],
                "is_final_action": False
            }
        
        # Count cities above base temperature
        above_threshold = [w for w in weather_data if w.get("temperature_f", 0) > base_temp]
        
        print(f"   [Cognition Engine] Cities above {base_temp}°F: {len(above_threshold)}")
        
        # Apply conditional logic as per task specification
        if len(above_threshold) == 3:
            # All three above: go to coolest
            coolest = min(above_threshold, key=lambda x: x["temperature_f"])
            return {
                "reasoning": f"All three cities are above base temperature {base_temp}°F. Per task specification, travel to coolest: {coolest['city']} at {coolest['temperature_f']}°F. Will generate weather image.",
                "proposed_action": {
                    "tool_name": "generate_image",
                    "parameters": {
                        "description": f"{coolest['city']} weather: {coolest['condition']}, {coolest['temperature_f']}°F"
                    }
                },
                "evidence_refs": ["weather_sf", "weather_miami", "weather_atlanta"],
                "decision_branch": "all_above_threshold",
                "is_final_action": True,
                "control_validated": False,
                "destination": coolest['city'],
                "umbrella_needed": coolest.get('precipitation_chance', 0) > 30
            }
        
        elif len(above_threshold) == 2:
            # Two above: choose cooler and send email
            cooler = min(above_threshold, key=lambda x: x["temperature_f"])
            return {
                "reasoning": f"Two cities above base temperature: {[w['city'] for w in above_threshold]}. Per task specification, choose cooler ({cooler['city']} at {cooler['temperature_f']}°F) and send email notification.",
                "proposed_action": {
                    "tool_name": "send_email",
                    "parameters": {
                        "recipient": "test-scl@test.com",
                        "subject": f"Travel Plan Confirmed: {cooler['city']}",
                        "body": f"Based on weather analysis, traveling to {cooler['city']}. Temperature: {cooler['temperature_f']}°F, Condition: {cooler['condition']}. {'Bring umbrella' if cooler.get('precipitation_chance', 0) > 30 else 'No umbrella needed'}."
                    }
                },
                "evidence_refs": ["weather_sf", "weather_miami", "weather_atlanta"],
                "decision_branch": "two_above_threshold",
                "is_final_action": True,
                "control_validated": False,
                "destination": cooler['city'],
                "umbrella_needed": cooler.get('precipitation_chance', 0) > 30
            }
        
        elif len(above_threshold) == 1:
            # One above: go there
            destination = above_threshold[0]
            return {
                "reasoning": f"Only {destination['city']} is above base temperature ({destination['temperature_f']}°F > {base_temp}°F). Per task specification, travel to that location.",
                "proposed_action": {
                    "tool_name": "send_email",
                    "parameters": {
                        "recipient": "test-scl@test.com",
                        "subject": f"Travel Plan: {destination['city']}",
                        "body": f"Traveling to {destination['city']}. Temperature: {destination['temperature_f']}°F. {'Bring umbrella' if destination.get('precipitation_chance', 0) > 30 else 'No umbrella needed'}."
                    }
                },
                "evidence_refs": ["weather_sf", "weather_miami", "weather_atlanta"],
                "decision_branch": "one_above_threshold",
                "is_final_action": True,
                "control_validated": False,
                "destination": destination['city'],
                "umbrella_needed": destination.get('precipitation_chance', 0) > 30
            }
        
        else:
            # None above: cancel and recommend snacks
            temps_str = ", ".join([f"{w['city']}={w['temperature_f']}°F" for w in weather_data])
            return {
                "reasoning": f"All cities are at or below base temperature {base_temp}°F: {temps_str}. Per task specification, cancel trip and recommend convenience store snacks.",
                "proposed_action": {
                    "tool_name": "cancel_trip",
                    "parameters": {
                        "reason": "All destinations below comfortable temperature threshold"
                    }
                },
                "evidence_refs": ["weather_sf", "weather_miami", "weather_atlanta"],
                "decision_branch": "all_below_threshold",
                "is_final_action": False,  # Need to recommend snacks next
                "control_validated": False
            }


class SimplifiedCognitionEngine:
    """
    Even simpler version for initial testing
    Uses hardcoded decision tree
    """
    
    def __init__(self):
        self.phase = "init"
        self.weather_data = {}
        
    def __call__(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """State machine implementation"""
        
        # Phase 1: Collect San Francisco weather
        if "San Francisco" not in self.weather_data:
            return {
                "reasoning": "Need San Francisco weather data first",
                "proposed_action": {
                    "tool_name": "get_weather",
                    "parameters": {"city": "San Francisco"}
                },
                "evidence_refs": [],
                "is_final_action": False
            }
        
        # Phase 2: Collect Miami weather
        if "Miami" not in self.weather_data:
            return {
                "reasoning": "Need Miami weather data",
                "proposed_action": {
                    "tool_name": "get_weather",
                    "parameters": {"city": "Miami"}
                },
                "evidence_refs": ["weather_sf"],
                "is_final_action": False
            }
        
        # Phase 3: Collect Atlanta weather
        if "Atlanta" not in self.weather_data:
            return {
                "reasoning": "Need Atlanta weather data",
                "proposed_action": {
                    "tool_name": "get_weather",
                    "parameters": {"city": "Atlanta"}
                },
                "evidence_refs": ["weather_sf", "weather_miami"],
                "is_final_action": False
            }
        
        # Phase 4: Make decision
        return {
            "reasoning": "All weather data collected. Making travel decision based on temperatures.",
            "proposed_action": {
                "tool_name": "send_email",
                "parameters": {
                    "recipient": "test-scl@test.com",
                    "subject": "Travel Decision",
                    "body": "Decision made based on weather analysis."
                }
            },
            "evidence_refs": ["weather_sf", "weather_miami", "weather_atlanta"],
            "is_final_action": True
        }
    
    def store_weather(self, city: str, data: Dict[str, Any]):
        """Helper to update internal state"""
        self.weather_data[city] = data
