from fastapi import FastAPI, Response, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler
)
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlmodel import Session, select, SQLModel
from dotenv import load_dotenv
import os
from .db import get_session
import json

app = FastAPI()

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    print(f'HTTP Error:  {repr(exc)})')
    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def custom_http_exception_handler(request, exc):
    print(f'Validation Error:  {repr(exc)})')
    return await request_validation_exception_handler(request, exc)


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
    statement = session.select(data)
    print(statement)
    get_cards = session.exec(statement).all()
    if not get_cards:
        raise HTTPException(status_code=410, detail="No cards found")
    results = [card for card in get_cards]
    return JSONResponse(content=jsonable_encoder(results))



