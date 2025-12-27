# backend/agents/receptionist.py
from backend.database import SessionLocal
from backend.models.room import Room
import re

# Static resort info
CHECK_IN_TIME = "2:00 PM"
CHECK_OUT_TIME = "11:00 AM"

FACILITIES_INFO = {
    "gym": "🏋️ Our gym is open from 6:00 AM to 10:00 PM.",
    "spa": "💆 Our spa operates from 9:00 AM to 8:00 PM.",
    "pool": "🏊 The swimming pool is open from 7:00 AM to 9:00 PM."
}


def extract_room_number(text: str):
    match = re.search(r"\b(10[0-9])\b", text)
    return int(match.group(1)) if match else None


def receptionist_agent(session_id: str, message: str):
    msg = (message or "").lower().strip()
    db = SessionLocal()
    try:
        # specific room query first
        room_no = extract_room_number(message or "")
        if room_no:
            room = db.query(Room).filter(Room.room_number == room_no).first()
            if not room:
                return "❌ That room does not exist."
            return f"✅ Room **{room_no}** is {'available' if room.is_available else 'occupied'}."

        # check-in / check-out
        if "check in" in msg or "check-in" in msg:
            return f"🕑 Check-in time is **{CHECK_IN_TIME}**."
        if "check out" in msg or "check-out" in msg:
            return f"🕚 Check-out time is **{CHECK_OUT_TIME}**."

        # facilities queries
        for facility, info in FACILITIES_INFO.items():
            if facility in msg:
                return info
        if "facilities" in msg or "facility" in msg:
            return (
                "🏨 **Our facilities include:**\n"
                "• Gym\n"
                "• Spa\n"
                "• Swimming Pool\n\n"
                "Ask about any of them (e.g., 'gym')."
            )

        # room availability (all)
        if "room availability" in msg or "available room" in msg or "room available" in msg:
            rooms = db.query(Room).filter(Room.is_available == True).all()
            if not rooms:
                return "❌ No rooms are currently available."
            room_list = ", ".join(str(r.room_number) for r in rooms)
            return f"✅ Available rooms: {room_list}"

        return (
            "I can help with:\n"
            "• Check-in / Check-out\n"
            "• Facilities\n"
            "• Room availability\n"
            "You can ask a specific room number (e.g. 'Is room 101 available?')."
        )
    finally:
        db.close()
