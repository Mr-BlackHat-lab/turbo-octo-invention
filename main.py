from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException

app = FastAPI(root_path="/api/v1")


@app.get("/")
async def root():
    return {"message": "Hello World"}


data: Any = [
    {
        "campaing_id": 1,
        "name": "semester breaks",
        "due_date": datetime.now(),
        "created_at": datetime.now(),
    },
    {
        "campaing_id": 2,
        "name": "coffe breaks",
        "due_date": datetime.now(),
        "created_at": datetime.now(),
    },
    {
        "campaing_id": 3,
        "name": "enjoy",
        "due_date": datetime.now(),
        "created_at": datetime.now(),
    },
    {
        "campaing_id": 69,
        "name": "lets get rustty",
        "due_date": datetime.now(),
        "created_at": datetime.now(),
    },
    {
        "campaing_id": 44,
        "name": "rusty",
        "due_date": datetime.now(),
        "created_at": datetime.now(),
    },
]


@app.get("/campaings")
async def read_campaings():
    return {"campaings": data}


@app.get("/campaings/{id}")
async def read_campaing_id(id: int):
    for campaing in data:
        if campaing.get("campaing_id") == id:
            return {"campaings": campaing}
    raise HTTPException(status_code=404)
