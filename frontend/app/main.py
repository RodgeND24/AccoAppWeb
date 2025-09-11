from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import httpx
from uvicorn import run

from api.routes import router as router_page

app = FastAPI(title="AccoApp client")
app.include_router(router_page)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Logic
@app.on_event("startup")
async def startup_app():
    app.state.http_client = httpx.AsyncClient()

@app.on_event("shutdown")
async def shutdown_app():
    await app.state.http_client.aclose()

if __name__=="__main__":
    run("main:app", host="localhost", port=8080, reload=True)
