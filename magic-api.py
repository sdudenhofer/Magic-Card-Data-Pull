from fastapi import FastAPI, Response, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import PlainTextResponse
from sqlmodel import Session, select, SQLModel
from dotenv import load_dotenv
import os
from .db import get_session
import json

app = FastAPI()

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=400)

class CardData(SQLModel):
    name: str
    type_line: str
    set_name: str
    rarity: str
    mana_cost: str
    arena_id: int

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

@app.get("/cards/", response_model=list[CardData])
def get_all_cards(all_cards, session: Session = Depends(get_session)):
    data = "all_cards"
    statement = select(data)
    get_cards = session.exec(statement).all()
    if not get_cards:
        raise HTTPException(status_code=404, detail="No cards found")
    results = [card for card in get_cards]
    return JSONResponse(content=jsonable_encoder(results))



