from datetime import datetime
from random import randint
from typing import Any

from fastapi import FastAPI, HTTPException, Request

app = FastAPI(root_path="/api/v1")


@app.get("/")
async def root():
    return {"message": "Hello World"}


data: Any = [
    {
        "campaign_id": 1,
        "name": "semester breaks",
        "due_date": datetime.now(),
        "created_at": datetime.now(),
    },
    {
        "campaign_id": 2,
        "name": "coffe breaks",
        "due_date": datetime.now(),
        "created_at": datetime.now(),
    },
    {
        "campaign_id": 3,
        "name": "enjoy",
        "due_date": datetime.now(),
        "created_at": datetime.now(),
    },
    {
        "campaign_id": 69,
        "name": "lets get rustty",
        "due_date": datetime.now(),
        "created_at": datetime.now(),
    },
    {
        "campaign_id": 44,
        "name": "rusty",
        "due_date": datetime.now(),
        "created_at": datetime.now(),
    },
]


@app.get("/campaigns")
async def read_campaigns():
    return {"campaigns": data}


@app.get("/campaigns/{id}")
async def read_campaign_id(id: int):
    for campaign in data:
        if campaign.get("campaign_id") == id:
            return {"campaigns": campaign}
    raise HTTPException(status_code=404)


@app.post("/campaigns")
async def create_campaign(body: dict[str, Any]):

    new: Any = {
        "campaign_id": randint(100, 1000),
        "name": body.get("name"),
        "due_date": body.get("due_date"),
        "created_at": datetime.now(),
    }

    data.append(new)
    return {"campaign": new}
