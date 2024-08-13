from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from fastapi_tailwind import tailwind
from contextlib import asynccontextmanager

static_files = StaticFiles(directory = "static")

@asynccontextmanager
async def lifespan(app: FastAPI):
    process = tailwind.watch(static_files.directory + "/output.css")

    yield

    process.terminate()

app = FastAPI(
    lifespan = lifespan
)

@app.get("/")
def index():
    return FileResponse("./index.html")

app.mount("/static", static_files, name = "static")