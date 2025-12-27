from backend.database import SessionLocal
from backend.models.service_request import ServiceRequest


def room_service_agent(session_id: str, message: str):
    msg = message.lower()
    db = SessionLocal()

    request_type = None

    # Detect request types
    if "clean" in msg:
        request_type = "Room Cleaning"

    elif "laundry" in msg:
        request_type = "Laundry Service"

    elif "towel" in msg:
        request_type = "Extra Towels"

    elif "toothpaste" in msg or "toiletries" in msg:
        request_type = "Toiletries"

    elif "pillow" in msg:
        request_type = "Extra Pillow"

    elif "blanket" in msg:
        request_type = "Extra Blanket"

    if request_type:
        request = ServiceRequest(
            room_number=101,
            request_type=request_type,
            status="Pending"
        )

        db.add(request)
        db.commit()
        db.close()

        return f"{request_type} request has been placed successfully."

    db.close()
    return "I can help with room cleaning, laundry, towels, toiletries, pillows, or blankets."
