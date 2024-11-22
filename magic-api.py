from fastapi import FastAPI, Response
from sqlalchemy import text
import database

app = FastAPI()

@app.get("/cards/")
async def read_cards:
    all_cards = text('SELECT * FROM all_cards')
    results = engine.execute(all_cards)
