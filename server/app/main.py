from fastapi import FastAPI
from uvicorn import run
from api.router import router

app = FastAPI()
app.include_router(router)


if __name__=="__main__":
    run("main:app", reload=True)