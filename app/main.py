from fastapi import FastAPI


app = FastAPI()



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
    