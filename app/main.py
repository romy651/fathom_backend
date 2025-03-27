from typing import Optional
from fastapi import FastAPI

from routes import files
from fastapi.middleware.cors import CORSMiddleware
from starlette.formparsers import MultiPartParser

app = FastAPI(
    title="LangChain File Processor",
    description="A FastAPI app for processing files using LangChain.",
    version="1.0.0",
)

MultiPartParser.max_part_size = 10 * 1024 * 1024
MultiPartParser.max_file_size = 10 * 1024 * 1024

app.include_router(files.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_methods=["*"],
    allow_headers=["*"],
)