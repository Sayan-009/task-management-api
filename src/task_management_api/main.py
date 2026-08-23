from fastapi import FastAPI

from task_management_api.users.router import router as users_router
from task_management_api.tasks.router import router as tasks_router
from task_management_api.comments.router import task_router, comment_router

app = FastAPI()

app.include_router(users_router)
app.include_router(tasks_router)
app.include_router(task_router)
app.include_router(comment_router) 



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
    