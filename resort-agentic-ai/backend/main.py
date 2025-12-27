# =========================
# Environment
# =========================
from backend.agents.router import route_message
from backend.models.room import Room
from backend.models import room, order, service_request, menu
from backend.database import engine, Base, SessionLocal
from pydantic import BaseModel
from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()

# =========================
# Standard Imports
# =========================

# =========================
# Database Imports
# =========================

# =========================
# Agent Router
# =========================

# =========================
# Create FastAPI App
# =========================
app = FastAPI(title="Resort Agentic AI")

# =========================
# Database Setup
# =========================
Base.metadata.create_all(bind=engine)

# =========================
# Room Initialization
# =========================


def initialize_rooms():
    db = SessionLocal()

    if db.query(Room).count() == 0:
        rooms = [
            Room(room_number=room_no, is_available=True)
            for room_no in range(101, 111)
        ]
        db.add_all(rooms)
        db.commit()

    db.close()


@app.on_event("startup")
def startup_event():
    initialize_rooms()

# =========================
# API Schemas
# =========================


class ChatRequest(BaseModel):
    session_id: str
    message: str

# =========================
# Routes
# =========================


@app.get("/")
def home():
    return {"message": "Resort Agentic AI Backend Running"}


@app.post("/chat")
def chat(req: ChatRequest):
    response = route_message(req.session_id, req.message)
    return {"response": response}
