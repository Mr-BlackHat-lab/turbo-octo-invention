from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Annotated, Any, Generic, List, Optional, TypeVar
from annotated_types import T
from typing_extensions import Type

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, func, select


class Campaign(SQLModel, table=True):
    campaign_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    due_date: datetime | None = Field(default=None, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=True, index=True
    )
class CampaignCreate(SQLModel):
    name:str
    due_date: datetime | None = None

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        if not session.exec(select(Campaign)).first():
            session.add_all([
                Campaign(name="somthing", due_date=datetime.now()),
                Campaign(name="free 415 v points", due_date=datetime.now()),
                Campaign(name="something is goning on", due_date=datetime.now()),
            ])
            session.commit()

    yield


app = FastAPI(root_path="/api/v1", lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}

T = TypeVar("T")

class Response(BaseModel, Generic[T]):
    data: T
class PaginatedResponse(BaseModel, Generic[T]):
    data:T
    next: Optional[str]
    prev: Optional[str]
    count: int


@app.get("/campaigns", response_model=PaginatedResponse[list[Campaign]])
async def read_campaigns(request:Request, session: SessionDep, page: int = Query(1, ge=1), page_size: int = Query(5, ge=1)):
    limitt = page_size
    offset = (page-1)*limitt
    data = session.exec(select(Campaign).order_by(Campaign.campaign_id).offset(offset).limit(limitt)).all() #type: ignore
    base_url = str(request.url).split('?')[0]
    total = session.exec(select(func.count()).select_from(Campaign)).one()
    if offset+limitt < total:
        next_url = f"{base_url}?page={page+1}&page_size={page_size}"
    else:
        next_url = None
    if page>1:
        prev_url = f"{base_url}?page={page-1}&page_size={page_size}"
    else:
        prev_url = None
    print(base_url)
    return {
        "count":total,
        "next":next_url,
        "prev":prev_url,
        "data": data
    }



@app.get("/campaigns/{id}", response_model=Response[Campaign])
async def read_campaign(id: int, session: SessionDep):
    data = session.get(Campaign, id)
    if not data:
        raise HTTPException(status_code=404)
    return {"data": data}

@app.post("/campaigns", status_code=201, response_model=Response[Campaign])
async def create_campaign(campaign: CampaignCreate, session: SessionDep):
    db_campaign = Campaign.model_validate(campaign)
    session.add(db_campaign)
    session.commit()
    session.refresh(db_campaign)
    return {"data": db_campaign}


@app.put("/campaigns/{id}",response_model=Response[Campaign])
async def update_campaign(campaign_id: int, campaign:CampaignCreate, session:SessionDep):
    data = session.get(Campaign,campaign_id)
    if not data:
        raise HTTPException(status_code=404)
    data.name = campaign.name
    data.due_date = campaign.due_date
    session.add(data)
    session.commit()
    session.refresh(data)
    return {"data":data}


@app.delete("/campaigns/{id}", status_code=204)
async def delete_campaigns(campaign_id: int, session:SessionDep):
    data = session.get(Campaign,campaign_id)
    if not data:
        raise HTTPException(status_code=404)
    session.delete(data)
    session.commit()
