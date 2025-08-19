from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run
from api.router import router
from db.database import init_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    await init_db()

app.include_router(router)


if __name__=="__main__":
    run("main:app", reload=True)