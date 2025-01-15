from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, FileResponse, JSONResponse, Response
import logging
import base64
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

app = FastAPI()

# --- Database Setup ---
DATABASE_URL = "sqlite:///./clicks.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Click(Base):
    __tablename__ = "clicks"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    ip = Column(String)
    event_type = Column(String)  # 'open' or 'click'
    timestamp = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 1x1 Transparent GIF (Base64 Encoded) ---
ONE_PIXEL_GIF_BASE64 = "R0lGODlhAQABAPAAAAAAAAAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=="
ONE_PIXEL_GIF = base64.b64decode(ONE_PIXEL_GIF_BASE64)


# --- Root Endpoint ---
@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Email Tracker API. Use /track_email?email=youremail@example.com to track email clicks."
    }


# --- Track Email Open ---
@app.get("/track_open")
def track_open(request: Request, email: str = ""):
    client_ip = request.client.host
    logger.info(f"Email opened by: {email} from IP: {client_ip}")

    # Log to database
    db = SessionLocal()
    click = Click(email=email, ip=client_ip, event_type="open")
    db.add(click)
    db.commit()
    db.refresh(click)
    db.close()

    # Return 1x1 Transparent GIF
    return Response(content=ONE_PIXEL_GIF, media_type="image/gif")


# --- Track Link Click ---
@app.get("/track_click")
def track_click(request: Request, email: str = ""):
    client_ip = request.client.host
    logger.info(f"Link clicked by: {email} from IP: {client_ip}")

    # Log to database
    db = SessionLocal()
    click = Click(email=email, ip=client_ip, event_type="click")
    db.add(click)
    db.commit()
    db.refresh(click)
    db.close()

    # Redirect to the actual signup page
    return RedirectResponse(url="https://yourcourse.com/signup?email={}".format(email))


# --- Optional: Retrieve Click Data ---
@app.get("/clicks")
def get_clicks():
    db = SessionLocal()
    clicks = db.query(Click).all()
    db.close()
    return [
        {
            "id": click.id,
            "email": click.email,
            "ip": click.ip,
            "event_type": click.event_type,
            "timestamp": click.timestamp,
        }
        for click in clicks
    ]
