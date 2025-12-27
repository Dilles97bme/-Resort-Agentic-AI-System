from backend.database import SessionLocal
from backend.models.menu import MenuItem
from backend.models.order import Order
from backend.models.room import Room
from rapidfuzz import fuzz
import re

# ===============================
# In-memory session store
# ===============================
SESSION_ORDERS = {}

# ===============================
# Number words map
# ===============================
NUM_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20
}

# ===============================
# Utilities
# ===============================


def text_to_number(token: str):
    t = token.lower().strip(".,")
    if t.isdigit():
        return int(t)
    return NUM_WORDS.get(t)


def parse_items_with_qty(msg: str):
    """
    Parses:
    - "two idli and one dosa"
    - "idli and dosa"
    - "2 idli, 1 upma"
    Returns: [(qty_or_None, item_text)]
    """
    parts = re.split(r"\band\b|,|&", msg, flags=re.IGNORECASE)
    results = []

    for part in parts:
        tokens = [t for t in part.strip().split() if t]
        if not tokens:
            continue

        qty = None
        item_tokens = tokens[:]

        # Look for number in first few tokens
        for i in range(min(4, len(tokens))):
            n = text_to_number(tokens[i])
            if n is not None:
                qty = n
                item_tokens = tokens[i + 1:]
                break

        item_text = " ".join(item_tokens).strip()
        if item_text:
            results.append((qty, item_text))

    return results


def find_menu_match(text: str, db, threshold=65):
    items = db.query(MenuItem).filter(MenuItem.available == True).all()
    best = None
    best_score = 0

    for item in items:
        score = fuzz.partial_ratio(item.item_name.lower(), text.lower())
        if score >= threshold and score > best_score:
            best = item
            best_score = score

    return best


# ===============================
# Restaurant Agent
# ===============================
def restaurant_agent(session_id: str, message: str):
    msg = (message or "").strip().lower()
    db = SessionLocal()

    try:
        # ---------------------------
        # Init session
        # ---------------------------
        if session_id not in SESSION_ORDERS:
            SESSION_ORDERS[session_id] = {
                "items": [],
                "stage": "awaiting_items",
                "current_index": 0
            }

        session = SESSION_ORDERS[session_id]

        # ---------------------------
        # Show menu
        # ---------------------------
        if "menu" in msg:
            items = db.query(MenuItem).filter(MenuItem.available == True).all()
            response = "🍽️ **Here is our menu:**\n\n"
            for it in items:
                response += f"- **{it.item_name}** (₹{it.price})\n  {it.description}\n\n"
            return response

        # ---------------------------
        # Parse items in one sentence
        # ---------------------------
        parsed = parse_items_with_qty(msg)
        if parsed:
            session["items"] = []
            for qty, text in parsed:
                menu_item = find_menu_match(text, db)
                if menu_item:
                    session["items"].append({
                        "name": menu_item.item_name,
                        "price": menu_item.price,
                        "qty": qty
                    })

            if not session["items"]:
                return "I couldn't recognize those items. Please check the menu."

            # If any item has missing qty → ask sequentially
            for idx, item in enumerate(session["items"]):
                if item["qty"] is None:
                    session["stage"] = "awaiting_quantity"
                    session["current_index"] = idx
                    return f"How many **{item['name']}** would you like?"

            # All quantities known → ask room
            session["stage"] = "awaiting_room"
            return "🛏️ Please tell me your room number to place the order."

        # ---------------------------
        # Awaiting quantity
        # ---------------------------
        if session["stage"] == "awaiting_quantity":
            qty = None
            for w, n in NUM_WORDS.items():
                if re.search(rf"\b{w}\b", msg):
                    qty = n
                    break
            m = re.search(r"\b(\d{1,2})\b", msg)
            if m:
                qty = int(m.group(1))

            if not qty or qty < 1:
                return "Please enter a valid quantity (e.g., 1, 2, two)."

            idx = session["current_index"]
            session["items"][idx]["qty"] = qty

            # Check for next missing quantity
            for i, it in enumerate(session["items"]):
                if it["qty"] is None:
                    session["current_index"] = i
                    return f"How many **{it['name']}** would you like?"

            session["stage"] = "awaiting_room"
            return "🛏️ Please tell me your room number to place the order."

        # ---------------------------
        # Awaiting room number
        # ---------------------------
        if session["stage"] == "awaiting_room":
            m = re.search(r"\b(10[0-9])\b", msg)
            if not m:
                return "Please provide a valid room number (e.g., 101)."

            room_number = int(m.group(1))
            room = db.query(Room).filter(
                Room.room_number == room_number).first()
            if not room:
                return "❌ Invalid room number."

            total = sum(it["price"] * it["qty"] for it in session["items"])
            item_summary = ", ".join(
                f"{it['name']} x{it['qty']}" for it in session["items"]
            )

            order = Order(
                room_number=room_number,
                items=item_summary,
                quantity="; ".join(str(it["qty"]) for it in session["items"]),
                total_amount=total,
                status="Confirmed"
            )

            db.add(order)
            db.commit()
            SESSION_ORDERS.pop(session_id, None)

            return f"✅ Order confirmed for room {room_number}: {item_summary}. Total ₹{total}"

        # ---------------------------
        # Single item fallback
        # ---------------------------
        item = find_menu_match(msg, db)
        if item:
            session["items"] = [{
                "name": item.item_name,
                "price": item.price,
                "qty": None
            }]
            session["stage"] = "awaiting_quantity"
            session["current_index"] = 0
            return f"How many **{item.item_name}** would you like?"

        return "You can ask for the menu or name an item to order."

    finally:
        db.close()
