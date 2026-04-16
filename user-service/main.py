from fastapi import FastAPI

app = FastAPI()

@app.get("/heath")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "User service is running"}