"""
Mock Tool Implementations for Travel Planning Scenario
Demonstrates tool registration and execution in Structured Cognitive Loop (SCL)
"""

import random
from typing import Dict, Any


def get_weather(city: str) -> Dict[str, Any]:
    """
    Mock weather API tool
    Returns temperature and condition for specified city
    """
    # Simulate realistic weather data
    weather_db = {
        "San Francisco": {"temp": random.randint(50, 75), "condition": "Partly Cloudy"},
        "Miami": {"temp": random.randint(70, 90), "condition": "Sunny"},
        "Atlanta": {"temp": random.randint(55, 80), "condition": "Clear"},
    }
    
    # Add some variability
    if city in weather_db:
        base_data = weather_db[city]
        return {
            "city": city,
            "temperature_f": base_data["temp"] + random.randint(-5, 5),
            "condition": base_data["condition"],
            "precipitation_chance": random.randint(0, 50),
            "api_ref": f"wx-{city.replace(' ', '').lower()}-001"
        }
    else:
        return {
            "city": city,
            "error": "City not found",
            "temperature_f": None
        }


def send_email(recipient: str, subject: str, body: str) -> Dict[str, Any]:
    """
    Mock email sending tool
    Logs email instead of actually sending
    """
    print(f"\n📧 EMAIL SENT")
    print(f"To: {recipient}")
    print(f"Subject: {subject}")
    print(f"Body: {body[:200]}...")
    
    return {
        "status": "sent",
        "recipient": recipient,
        "subject": subject,
        "timestamp": "2024-01-15T10:30:00Z",
        "message_id": f"msg-{hash(body) % 10000}"
    }


def generate_image(description: str) -> Dict[str, Any]:
    """
    Mock image generation tool
    Returns a placeholder image reference
    """
    print(f"\n🖼️  IMAGE GENERATED")
    print(f"Description: {description}")
    
    return {
        "status": "generated",
        "description": description,
        "image_url": f"https://placeholder.com/weather/{description.replace(' ', '_')}.jpg",
        "format": "JPEG",
        "size": "1024x768"
    }


def cancel_trip(reason: str) -> Dict[str, Any]:
    """
    Mock trip cancellation tool
    """
    print(f"\n✗ TRIP CANCELLED")
    print(f"Reason: {reason}")
    
    return {
        "status": "cancelled",
        "reason": reason,
        "refund_initiated": True
    }


def recommend_snacks(preferences: str = "general") -> Dict[str, Any]:
    """
    Mock snack recommendation tool
    """
    snack_lists = {
        "general": [
            "Honey Butter Chips",
            "Choco Pie",
            "Pepero Sticks",
            "Shin Ramyun Cup",
            "Market O Brownies"
        ],
        "sweet": [
            "Choco Pie",
            "Market O Brownies",
            "Custard Cake",
            "Pepero Almond",
            "Crown Sando"
        ],
        "savory": [
            "Honey Butter Chips",
            "Shin Ramyun Cup",
            "Squid Peanut Snack",
            "Turtle Chips",
            "Seaweed Snack"
        ]
    }
    
    snacks = snack_lists.get(preferences, snack_lists["general"])
    
    print(f"\n🍿 SNACK RECOMMENDATIONS ({preferences})")
    for i, snack in enumerate(snacks, 1):
        print(f"{i}. {snack}")
    
    return {
        "status": "recommended",
        "preference": preferences,
        "snacks": snacks,
        "total_items": len(snacks)
    }


def check_umbrella_needed(city: str, precipitation_chance: int) -> Dict[str, Any]:
    """
    Simple decision tool for umbrella recommendation
    """
    needs_umbrella = precipitation_chance > 30
    
    return {
        "city": city,
        "precipitation_chance": precipitation_chance,
        "recommendation": "Bring umbrella" if needs_umbrella else "No umbrella needed",
        "confidence": "high" if abs(precipitation_chance - 30) > 20 else "medium"
    }
