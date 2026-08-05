from fastapi import FastAPI

from app.users.router import router as user_router

app = FastAPI()

app.include_router(user_router)



@app.get('/health')
def health():
    return {
        "health": "UP"
    }

@app.get('/')
def root():
    return {
        "service": "Task Management API",
        "version": "1.0.0"
    }
    