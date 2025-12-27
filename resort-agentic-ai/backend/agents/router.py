# backend/agents/router.py
from rapidfuzz import fuzz
import logging

from backend.agents.receptionist import receptionist_agent
from backend.agents.restaurant import restaurant_agent, SESSION_ORDERS
from backend.agents.room_service import room_service_agent

# optional LLM router (fallback only)
try:
    from backend.agents.llm_router import llm_router
    LLM_AVAILABLE = True
except Exception:
    LLM_AVAILABLE = False

LOG = logging.getLogger("router")
logging.basicConfig(level=logging.INFO)

ROOM_SERVICE_KEYWORDS = [
    "room service", "clean", "cleaning", "laundry",
    "towel", "towels", "toiletries", "toothpaste",
    "pillow", "blanket", "blankets"
]

RESTAURANT_KEYWORDS = [
    "menu", "order", "food", "eat", "hungry",
    "breakfast", "lunch", "dinner",
    # item-name hints
    "idli", "dosa", "vada", "poha", "paratha", "paneer", "puri", "omelette", "egg", "eggs", "upma"
]

RECEPTIONIST_KEYWORDS = [
    "check in", "check-in", "check out", "check-out",
    "gym", "spa", "pool", "facility", "facilities",
    "room availability", "available room", "room available"
]


def fuzzy_match(words, msg, threshold=75):
    return any(fuzz.partial_ratio(w, msg) >= threshold for w in words)


def route_message(session_id: str, message: str):
    msg = (message or "").lower().strip()
    LOG.info("Routing message: %s", msg)

    try:
        # 1️⃣ If there's an active restaurant session, continue only when it's expecting quantities/room
        if session_id in SESSION_ORDERS:
            stage = SESSION_ORDERS[session_id].get("stage")
            if stage in {"awaiting_quantity", "awaiting_room"}:
                return restaurant_agent(session_id, message)

        # 2️⃣ High-priority room-service interrupts (always allowed)
        if any(k in msg for k in ROOM_SERVICE_KEYWORDS):
            return room_service_agent(session_id, message)

        # 3️⃣ Receptionist (check-in/availability/facilities)
        if any(k in msg for k in RECEPTIONIST_KEYWORDS):
            return receptionist_agent(session_id, message)

        # 4️⃣ Restaurant (menu / ordering)
        if any(k in msg for k in RESTAURANT_KEYWORDS):
            return restaurant_agent(session_id, message)

        # 5️⃣ fuzzy fallbacks (spelling mistakes)
        if fuzzy_match(ROOM_SERVICE_KEYWORDS, msg):
            return room_service_agent(session_id, message)
        if fuzzy_match(RECEPTIONIST_KEYWORDS, msg):
            return receptionist_agent(session_id, message)
        if fuzzy_match(RESTAURANT_KEYWORDS, msg):
            return restaurant_agent(session_id, message)

        # 6️⃣ LLM fallback (optional)
        if LLM_AVAILABLE:
            return llm_router(session_id, message)

        # 7️⃣ safe fallback
        return (
            "Sorry, I didn't understand that clearly.\n"
            "You can ask about:\n"
            "• Food & menu 🍽️\n"
            "• Room service 🧹\n"
            "• Check-in / facilities 🏨"
        )

    except Exception:
        LOG.exception("Router error")
        return "Backend error. Please try again."
