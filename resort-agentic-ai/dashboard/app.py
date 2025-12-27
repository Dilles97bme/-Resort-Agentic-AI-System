import os
import streamlit as st
import sqlite3
import pandas as pd

# =============================
# DATABASE PATH
# =============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "resort.db")

st.set_page_config(
    page_title="Resort Operations Dashboard",
    layout="wide"
)

st.title("🏨 Resort Operations Dashboard")

# =============================
# DATABASE CONNECTION
# =============================
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# =====================================================
#  ROOM AVAILABILITY (SINGLE GRID)
# =====================================================
st.header("🛏️ Room Availability")

rooms_df = pd.read_sql_query(
    "SELECT room_number, is_available FROM rooms ORDER BY room_number",
    conn
)

if rooms_df.empty:
    st.warning("No rooms found in database.")
else:
    cols = st.columns(5)

    for idx, row in rooms_df.iterrows():
        with cols[idx % 5]:
            color = "#2ecc71" if row["is_available"] else "#e74c3c"
            status = "Available" if row["is_available"] else "Occupied"

            st.markdown(
                f"""
                <div style="
                    background-color:{color};
                    padding:20px;
                    border-radius:12px;
                    text-align:center;
                    color:white;
                    font-weight:bold;
                    font-size:16px;
                ">
                    Room {row['room_number']}<br>
                    {status}
                </div>
                """,
                unsafe_allow_html=True
            )

st.caption("🟢 Available | 🔴 Occupied")
st.divider()

# =====================================================
# RESTAURANT ORDERS
# =====================================================
st.header("🍽 Restaurant Orders")

orders_df = pd.read_sql_query(
    """
    SELECT id, room_number, items, quantity, total_amount, status, created_at
    FROM orders
    ORDER BY created_at DESC
    """,
    conn
)

if orders_df.empty:
    st.info("No restaurant orders yet.")
else:
    for _, row in orders_df.iterrows():
        col1, col2 = st.columns([6, 2])

        with col1:
            st.markdown(
                f"""
                **Order ID:** {row['id']}  
                **Room:** {row['room_number']}  
                **Items:** {row['items']}  
                **Quantity:** {row['quantity']}  
                **Total Bill:** ₹{row['total_amount']}  
                **Status:** {row['status']}  
                """
            )

        with col2:
            if row["status"] != "Served":
                if st.button(
                    f"🍽 Mark Served",
                    key=f"serve_{row['id']}"
                ):
                    cursor.execute(
                        "UPDATE orders SET status='Served' WHERE id=?",
                        (row["id"],)
                    )
                    conn.commit()
                    st.rerun()

        st.divider()

# =====================================================
#  ROOM SERVICE REQUESTS
# =====================================================
st.header("🧹 Room Service Requests")

service_df = pd.read_sql_query(
    """
    SELECT id, room_number, request_type, status, created_at
    FROM service_requests
    ORDER BY created_at DESC
    """,
    conn
)

if service_df.empty:
    st.info("No room service requests yet.")
else:
    for _, row in service_df.iterrows():
        col1, col2 = st.columns([6, 2])

        with col1:
            st.markdown(
                f"""
                **Request ID:** {row['id']}  
                **Room:** {row['room_number']}  
                **Service:** {row['request_type']}  
                **Status:** {row['status']}  
                """
            )

        with col2:
            if row["status"] != "Completed":
                if st.button(
                    f"🧹 Mark Completed",
                    key=f"complete_{row['id']}"
                ):
                    cursor.execute(
                        "UPDATE service_requests SET status='Completed' WHERE id=?",
                        (row["id"],)
                    )
                    conn.commit()
                    st.rerun()

        st.divider()

conn.close()
