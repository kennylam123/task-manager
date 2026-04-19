from fastapi import FastAPI
from pydantic import BaseModel
import os

app = FastAPI()

class Notification(BaseModel):
    email: str
    message: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/notify")
def notify(notification: Notification):
    print(f"Sending notification to {notification.email}: {notification.message}")
    return {"status": "notification sent", "email": notification.email}