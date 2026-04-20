from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import httpx
import os

app = FastAPI()
security = HTTPBearer()

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "HTTP://localhost:8000")
TASK_SERVICE_URL = os.getenv("USER_SERVICE_URL", "HTTP://localhost:8001")
NOTIFICATION_SERVICE_URL = os.getenv("USER_SERVICE_URL", "HTTP://localhost:8002")

class AuthRequest(BaseModel):
    email: str
    password: str

class TaskRequest(BaseModel):
    title:str
    description: str = None

class UpdateTaskRequest(BaseModel):
    title: str = None
    description: str = None
    complete: bool= None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/auth/login")
async def login(request: AuthRequest):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{USER_SERVICE_URL}/login", json=request.dict())
    return response.json()

@app.post("/api/auth/register")
async def register(request: AuthRequest):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{USER_SERVICE_URL}/register",
            json=request.dict())
    return response.json()

@app.post("/api/tasks")
async def create_task(request: TaskRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{TASK_SERVICE_URL}/tasks",
            json=body,
            headers={"Authorization": f"Bearer {credentials.credentials}"}
        )
    return response.json()

@app.get("/api/tasks")
async def get_tasks(credentials: HTTPAuthorizationCredentials = Depends(security)):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TASK_SERVICE_URL}/tasks",
            headers = {"Authorization": f"Bearer {credentials.credentials}"}
        )

        return response.json()
    
@app.put("/api/tasks/{task_id}")
async def update_task(task_id: int, request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{TASK_SERVICE_URL}/tasks/{task_id}",
            json=body,
            headers = {"Authorization": f"Bearer {credentials.credentials}"}
        )

        return response.json()
    

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    async with httpx.AsyncClient() as client:
        response = await client.delete(
        f"{TASK_SERVICE_URL}/tasks/{task_id}",
            headers = {"Authorization": f"Bearer {credentials.credentials}"}
        )

    return response.json()

@app.post("/api/notify")
async def notify(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        respone = await client.post(f"{NOTIFICATION_SERVICE_URL}/notify", json=body)
    return respone.json()

