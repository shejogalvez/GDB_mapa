from fastapi import FastAPI
from db import db

app = FastAPI()

@app.get("/")
async def root():
    return list(db.get_all_nodes())
