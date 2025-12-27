import streamlit as st
import requests
import uuid

API_URL = "http://127.0.0.1:8000/chat"

st.set_page_config(page_title="Resort AI Assistant", layout="centered")
st.title("🏨 Resort AI Assistant")

# -------------------------
# Session handling
# -------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -------------------------
# Display chat history
# -------------------------
for role, msg in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(msg)

# -------------------------
# User input
# -------------------------
user_input = st.chat_input("Type your message...")

if user_input:
    # Show user message
    st.session_state.chat_history.append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call backend
    payload = {
        "session_id": st.session_state.session_id,
        "message": user_input
    }

    response = requests.post(API_URL, json=payload)

    try:
        bot_reply = response.json().get("response", "Sorry, something went wrong.")
    except Exception:
        bot_reply = "Backend error. Please try again."

    # Show bot message
    st.session_state.chat_history.append(("assistant", bot_reply))
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
