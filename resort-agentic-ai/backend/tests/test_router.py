import pytest
from backend.agents.router import route_message
from backend.agents.restaurant import SESSION_ORDERS

# -----------------------------
# Helper
# -----------------------------


def clear_sessions():
    SESSION_ORDERS.clear()

# -----------------------------
# Tests
# -----------------------------


def test_room_service_routing():
    clear_sessions()
    response = route_message("u1", "I need room cleaning")
    assert "clean" in response.lower() or "service" in response.lower()


def test_restaurant_routing():
    clear_sessions()
    response = route_message("u2", "Show me the menu")
    assert "menu" in response.lower()


def test_receptionist_routing():
    clear_sessions()
    response = route_message("u3", "What is check in time?")
    assert "check" in response.lower()


def test_restaurant_session_continuation():
    clear_sessions()
    route_message("u4", "I want dosa")
    response = route_message("u4", "2")
    assert "order" in response.lower() or "bill" in response.lower()


def test_unknown_message_fallback():
    clear_sessions()
    response = route_message("u5", "asdfghjkl")
    assert "help" in response.lower()
