from fastapi import FastAPI
from database import engine, Base
from src.app.models import *
app = FastAPI()


@app.get("/")
async def root():
    engine.echo = False
    Base.metadata.drop_all(engine)
    engine.echo = True
    # Base.metadata.create_all(engine)
    return {"message": "Hello World"}


