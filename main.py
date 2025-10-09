from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import asyncio
import os

from models import Notification
from notification_processors import load_processors


processors = [] # load_processors()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup phase
    global processors
    processors = load_processors()
    yield
    # Shutdown phase (optional cleanup)
    print("Shutting down notification server...")

app = FastAPI(lifespan=lifespan)

@app.post("/notify")
async def receive_notification(notification: Notification):
    # Dispatch notification to all processors concurrently
    await asyncio.gather(*(p.process(notification) for p in processors))

    return JSONResponse(
        content={"status": "forwarded", "processors": [p.__class__.__name__ for p in processors]},
        status_code=200,
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
