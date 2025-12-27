# Resort Agentic AI System

**Agentic AI System for a Resort**— a chat-based system that routes guest requests to three department agents (Receptionist, Restaurant, Room Service), persists actions in a database, and exposes an operations dashboard for staff.

---

## Table of Contents
1. [Project Overview](#project-overview)  
2. [Features](#features)  
3. [System Architecture](#system-architecture)  
4. [Tech Stack](#tech-stack)  
5. [Repository Structure](#repository-structure)  
6. [Setup & Installation (Step‑by‑Step)](#setup--installation-step%E2%80%91by%E2%80%91step)  
7. [Environment Variables (`.env`)](#environment-variables-env)  
8. [Database Models](#database-models)  
9. [How the Agents Work](#how-the-agents-work)  
10. [Running the System (terminals & ports)](#running-the-system-terminals--ports)  
11. [Sample Conversations](#sample-conversations)  
12. [Testing](#testing)  

---

## Project Overview

This project implements a modular, LLM-driven, multi-turn **Agentic AI System** for a resort. Guests interact with a single chat interface; the system interprets intent and routes requests to specialized agents (Receptionist, Restaurant, Room Service). All actions that change state (orders, room-service requests, room availability) are persisted to a database and shown on an admin dashboard for operations staff.

The objective was to demonstrate: agentic design, LLM orchestration & tool usage, backend engineering, data modeling, and product thinking for a small real-world workflow.

---

## Features

- Single chat interface for guests (supports multi-turn conversations)  
- LLM-based intent routing + keyword fallback for reliability  
- Agents: Receptionist, Restaurant, Room Service (modular code)  
- Persistent storage (SQLite) for: rooms, orders, service requests, menu items  
- Restaurant ordering workflow: menu display → multi-item orders → quantity → room number → billing → DB record  
- Room service workflow: cleaning, laundry, extra amenities → DB record  
- Dashboard (Streamlit): view & update restaurant orders and service requests; room availability grid (color-coded)  
- Fuzzy matching for menu items (tolerates common typos)  


---

## System Architecture (high level)

```
[Chat UI]  <--->  [FastAPI Backend]
                        |
                        +--> [Router (keyword fallback + LLM)]
                              |
                              +--> [Receptionist Agent]  (static answers, room availability)
                              +--> [Restaurant Agent]    (menu, multi-turn ordering, DB writes)
                              +--> [Room Service Agent] (requests, DB writes)
                        |
                        +--> [SQLite Database (resort.db)]
                        |
                        +--> [Streamlit Dashboard] (reads/writes DB)
```

- The **Router** can be a small rule-based classifier and can call the LLM when uncertain (or always use LLM depending on cost/accuracy tradeoff).  
- **Agents** are simple Python modules that accept `(session_id, message)` and return a text response. Agents maintain short-lived session state in memory or persist intermediate state in DB (recommended for multi-instance).

---

## Tech Stack

- **Language:** Python 3.x  
- **Backend:** FastAPI + Uvicorn  
- **LLM:** OpenAI (or compatible) — use API via `openai` or `OpenAI` client  
- **Database:** SQLite (local file `resort.db`), accessible via SQLAlchemy or `sqlite3`  
- **Dashboard:** Streamlit  
- **Utilities:** python-dotenv, pandas (for loading menu), rapidfuzz (fuzzy matching), pydantic (request models)  
- **Testing:** pytest (unit tests for router and agents)  


---

## Repository Structure

```
resort-agentic-ai/
├─ backend/
│  ├─ main.py                 # FastAPI app entry (create tables, start endpoints)
│  ├─ database.py             # engine, SessionLocal, Base (SQLAlchemy)
│  ├─ models/
│  │   ├─ menu.py
│  │   ├─ order.py
│  │   ├─ room.py
│  │   └─ service_request.py
│  ├─ agents/
│  │   ├─ router.py
│  │   ├─ llm_router.py
│  │   ├─ receptionist.py
│  │   ├─ restaurant.py
│  │   └─ room_service.py
│  └─ tools/
│      └─ load_menu.py        # script to import Restaurant_Menu.xlsx into DB
├─ ui/
│  └─ chat_ui.py              # CLI or Streamlit chat client
├─ dashboard/
│  └─ app.py                  # Streamlit admin dashboard (orders, service requests, rooms)
├─ Restaurant_Menu.xlsx
├─ requirements.txt
├─ .env.example
└─ README.md
```

---

## Setup & Installation (Step‑by‑Step)

Follow these commands in order. Commands assume you are in the `resort-agentic-ai` folder.

### 1. Clone repo
```bash
git clone <your-repo-url>
cd resort-agentic-ai
```

### 2. Create & activate a Python virtual environment (venv)
**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**macOS / Linux (bash):**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Why venv?**  
`venv` isolates project dependencies into `venv/` so they don't conflict with other projects or system Python. Always activate the venv before installing packages or running scripts.

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

A typical `requirements.txt` used in this project contains:
```
fastapi
uvicorn[standard]
python-dotenv
openai
sqlalchemy
pydantic
streamlit
pandas
rapidfuzz
pytest
```

### 4. Configure environment variables
Copy `.env.example` to `.env` and add your API key(s):
```bash
cp .env.example .env   # or copy on Windows
# then edit .env to set OPENAI_API_KEY and any other vars
```

Example `.env`:
```
OPENAI_API_KEY=sk-...
```

### 5. Initialize the database & load menu (one-time)
Create tables and load the menu into the DB:

**Option A — if `backend/main.py` auto-creates tables on startup:**  
Start backend (next step) and run the menu loader.

**Option B — run helper script:**  
```bash
python -m backend.tools.load_menu
```

The `load_menu` script reads `Restaurant_Menu.xlsx` and inserts menu items into the `menu_items` table.

### 6. Run the backend (FastAPI)
```bash
uvicorn backend.main:app --reload --port 8000
```

Open the OpenAPI docs at: `http://127.0.0.1:8000/docs` to test the `/chat` endpoint.

### 7. Run the dashboard (Streamlit)
In a new terminal (with venv activated):

```bash
streamlit run dashboard/app.py
```

Open the dashboard at `http://localhost:8501` (default). The dashboard displays restaurant orders, room service requests, and a room availability grid.

### 8. Run the chat UI (CLI or web)
**CLI client** sample:

```bash
python ui/chat_ui.py
```

**Streamlit chat UI** :

```bash
streamlit run ui/chat_ui.py
```

Chat by typing normal messages; the UI will `POST` to `http://127.0.0.1:8000/chat` with JSON:

```json
{ "session_id": "user1", "message": "Show me the menu" }
```

---

## Environment variables (`.env`)

Key variables used by the project (put in `.env`):

- `OPENAI_API_KEY` —  OpenAI API key to call the LLM (required)
- `DATABASE_URL` — e.g. `sqlite:///./resort.db` 
- Any other config (e.g., `LOG_LEVEL`, `PORT`) as needed

---

## Database Models 

1. **menu_items**  
   - `id` (int, PK)  
   - `item_name` (string)  
   - `description` (string)  
   - `price` (float)  
   - `available` (boolean)

2. **orders**  
   - `id` (int, PK)  
   - `room_number` (int)  
   - `items` (string, e.g., "Plain Idli x2, Aloo Paratha x1")  
   - `quantity` (string; semicolon-separated if multiple)  
   - `total_amount` (float)  
   - `status` (string: Pending, Confirmed, Served)  
   - `created_at` (datetime)

3. **service_requests**  
   - `id` (int, PK)  
   - `room_number` (int)  
   - `request_type` (string)  
   - `status` (string: Pending, In Progress, Completed)  
   - `created_at` (datetime)

4. **rooms**  
   - `id` (int, PK)  
   - `room_number` (int, unique)  
   - `is_available` (boolean)

---

## How the Agents Work 

### Router
- First checks for simple keywords (fast, free). Example keywords: `["menu","order","food"]` for restaurant; `["clean","towel","pillow"]` for room service; `["check-in","check out", "gym"]` for receptionist.  
- If the message is ambiguous, call the LLM (router prompt) to decide between `receptionist`, `restaurant`, or `room_service` and return exactly one token indicating the chosen agent. Use a deterministic low-temperature call `temperature=0` for reproducible routing.

### Receptionist Agent
- Returns static answers for common FAQs (check-in/out time, facility hours).  
- For room availability: query `rooms` table and return a user-friendly summary (e.g., "Rooms available: 103, 105, 109").  
- Optionally supports `check-in` action: update `rooms.is_available=False` for that room and confirm (requires explicit guest confirmation).

### Restaurant Agent
- Multi-step flow:
  1. Show menu (optionally with descriptions and prices).
  2. Detect items in user's message using fuzzy matching (RapidFuzz) to tolerate typos.
  3. If multiple items, collect quantities for each item in order (store in `SESSION_ORDERS` keyed by session_id).
  4. Ask for room number if not known (room must be provided to store order).
  5. Compute total and create an `orders` DB row with `status='Confirmed'`.
  6. Optionally, mark the room as occupied (set `is_available=False`) on first order or checkout policy as required.

### Room Service Agent
- Accept requests like `Please clean my room` or `I need two towels`.  
- Ask clarifying questions as needed and create `service_requests` DB entry with `status='Pending'`.

---

## Running the System — Terminals & Ports (recommended)

- **Terminal A — Backend**  
  `uvicorn backend.main:app --reload --port 8000`  
  → FastAPI (OpenAPI docs at `http://127.0.0.1:8000/docs`)

- **Terminal B — Load menu (one-time)**  
  `python -m backend.tools.load_menu`

- **Terminal C — Dashboard**  
  `streamlit run dashboard/app.py`  
  → Admin UI at `http://localhost:8501`

- **Terminal D — Chat UI / CLI**  
  `python ui/chat_ui.py` (or `streamlit run ui/chat_ui.py` for a web chat)

---

## Sample Conversations

**Receptionist (FAQ):**  
```
User: "What time is check-out?"
Bot: "Check-out time is 11:00 AM."
```

**Restaurant (multi-item order):**  
```
User: "Show me the menu."
Bot: "<menu list>"

User: "I want plain idli and aloo paratha."
Bot: "How many Plain Idli would you like?"
User: "2"
Bot: "How many Aloo Paratha would you like?"
User: "1"
Bot: "Please tell me your room number to place the order."
User: "101"
Bot: "Order confirmed! Items: Plain Idli x2, Aloo Paratha x1. Total bill is ₹300."
```
(The order appears on the Streamlit dashboard under Restaurant Orders.)

**Room Service:**  
```
User: "Can I get extra towels?"
Bot: "How many towels would you like?"
User: "2"
Bot: "Request logged. Our staff will bring 2 towels to your room."
```


## Testing

- Unit tests for routing & agents: place tests under `backend/tests/`. Example:
```bash
pytest backend/tests/test_router.py
```

- For tests that call LLMs, mock the OpenAI client to avoid network calls and quota usage. Use `unittest.mock` or `pytest` fixtures to inject a fake LLM response.

---



