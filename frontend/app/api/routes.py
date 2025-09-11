from fastapi import APIRouter, HTTPException, Request, Response, Depends, Cookie, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
import httpx
from dotenv import load_dotenv
import os

router = APIRouter()
templates = Jinja2Templates("templates")

load_dotenv()
API_URL = os.getenv("API_URL")
ACCESS_COOKIE_NAME = os.getenv("JWT_ACCESS_COOKIE_NAME")
REFRESH_COOKIE_NAME = os.getenv("JWT_REFRESH_COOKIE_NAME")
ACCESS_TOKEN_EXPIRES = os.getenv("JWT_ACCESS_TOKEN_EXPIRES_IN_MINUTES")
REFRESH_TOKEN_EXPIRES = os.getenv("JWT_REFRESH_TOKEN_EXPIRES_IN_HOURS")

async def get_current_auth_user(access_token: str = Cookie(None)):
    if not access_token:
        return None
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get(f"{API_URL}/users/me", headers=headers)
            if response.status_code == 200:
                return response.json()["username"]
    
    except httpx.RequestError:
        return None
    
    return None

def auth_required(current_user: str = Depends(get_current_auth_user)):
    if not current_user:
        raise HTTPException(status_code=303, headers={"Location": "/"})
    return current_user

@router.get("/", response_class= HTMLResponse | RedirectResponse)
def root(request: Request, current_user: str = Depends(get_current_auth_user), error: str = None):
    
    if current_user:
        return RedirectResponse(url="/accounting", status_code=303)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "current_user": current_user,
        "error": error
    })

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login_user(user_data: LoginRequest):

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{API_URL}/auth/login', 
                headers= {'Content-Type': 'application/json'},
                json={
                    "username": user_data.username,
                    "password": user_data.password},
                timeout=10.0
                )
            print(response.status_code)
            if response.status_code == 200:
                token_data = response.json()
                
                try:
                    redirect_response = RedirectResponse(url="/accounting", status_code=302)
                except:
                    return RedirectResponse(url="/?error=redirect_error", status_code=302)
                
                # set cookies
                redirect_response.set_cookie(
                    key=ACCESS_COOKIE_NAME,
                    value=token_data["access_token"],
                    httponly=True,
                    max_age=ACCESS_TOKEN_EXPIRES * 60,
                    samesite="lax",
                )
                redirect_response.set_cookie(
                    key=REFRESH_COOKIE_NAME,
                    value=token_data["refresh_token"],
                    httponly=True,
                    max_age=REFRESH_TOKEN_EXPIRES * 60 * 60,
                    samesite="lax",
                )
                
                return redirect_response
            else:
                RedirectResponse(url=f"/?error=auth_failed&message={response.json().get('detail','Unknown error')}", status_code=303)
                
    except:
        RedirectResponse(url="/?error=service_unavailable", status_code=303)
        return None

@router.post("/logout")
async def logout():
    redirect_response = RedirectResponse(url="/", status_code=303)
    redirect_response.delete_cookie(key=ACCESS_COOKIE_NAME)
    redirect_response.delete_cookie(key=REFRESH_COOKIE_NAME)
    return redirect_response


@router.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_api(path: str, request: Request, access_token: str = Cookie(None), current_user: str = Depends(auth_required)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"}
    body = await request.body() if request.method in ["POST", "PUT", "DELETE"] else None

    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
            method=request.method,
            url=f"{API_URL}/{path}",
            headers=headers,
            content=body,
            params=request.query_params
            )

            if response.status_code >= 400:
                return JSONResponse(status_code=response.status_code, content=response.json())
    
            return response.json()
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Service unavailable")

@router.get("/accounting", response_class=HTMLResponse)
def root(request: Request, current_user: str = Depends(auth_required)):
    return templates.TemplateResponse("accounting.html", {
        "request": request, 
        "current_user": current_user
        }
    )