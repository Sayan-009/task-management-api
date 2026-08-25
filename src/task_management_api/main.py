from task_management_api.db import models

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from task_management_api.users.router import router as users_router
from task_management_api.tasks.router import router as tasks_router
from task_management_api.comments.router import task_router, comment_router
from task_management_api.conversations.conversation_router import conv_router
from task_management_api.conversations.message_router import message_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(tasks_router)
app.include_router(task_router)
app.include_router(comment_router) 
app.include_router(conv_router)
app.include_router(message_router)



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
    