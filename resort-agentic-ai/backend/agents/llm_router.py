import os
from openai import OpenAI

from backend.agents.receptionist import receptionist_agent
from backend.agents.restaurant import restaurant_agent
from backend.agents.room_service import room_service_agent


def llm_router(session_id: str, message: str):
    """
    LLM-based router that decides which agent should handle the message.

    - Uses OpenAI for intent reasoning
    - Falls back to rule-based routing if OpenAI fails
    - OpenAI client is created lazily to avoid env / reload issues
    """

    # Step 1: Prepare fallback

    msg = message.lower()
    decision = None

    # Step 2: Try LLM routing

    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not found")

        client = OpenAI(api_key=api_key)

        system_prompt = """
You are an AI intent router for a resort chatbot.

Your task:
Classify the user's message into exactly ONE department.

Departments:
1. receptionist
   - check-in, check-out
   - room availability
   - facilities (gym, spa, pool)
   - general resort information

2. restaurant
   - food
   - menu
   - ordering
   - hunger
   - quantities
   - billing

3. room_service
   - room cleaning
   - laundry
   - towels
   - pillows
   - blankets
   - toiletries
   - toothpaste

Rules:
- Return ONLY one word
- No punctuation
- No explanation
- If food or ordering is mentioned → restaurant
- If cleaning or amenities → room_service
- Otherwise → receptionist

Valid outputs:
receptionist
restaurant
room_service
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0
        )

        decision = response.choices[0].message.content.strip().lower()

    except Exception as e:

        # Step 3: Fallback (NO LLM)

        if any(w in msg for w in ["food", "hungry", "menu", "eat", "order"]):
            decision = "restaurant"
        elif any(w in msg for w in ["clean", "laundry", "towel", "toothpaste", "pillow", "blanket"]):
            decision = "room_service"
        else:
            decision = "receptionist"

    # Step 4: Call agent

    if decision == "restaurant":
        return restaurant_agent(session_id, message)

    if decision == "room_service":
        return room_service_agent(session_id, message)

    return receptionist_agent(message)
