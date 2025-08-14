from fastapi import FastAPI,Request
from pydantic import BaseModel , EmailStr
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import os
import secrets

secrets.token_urlsafe()
client_id=os.getenv("CLIENT_ID")
client_secret=os.getenv("CLIENT_SECRET")
redirect_uri=os.getenv("REDIRECT_URI")



app = FastAPI()

app.mount("/static", StaticFiles(directory=r"..\frontend"), name="static")
app.add_middleware(SessionMiddleware,secrets =secrets.token_urlsafe())



@app.get('/')
def root ():
    return "Hello world"


@app.get('/auth')
def signin(request:Request):
    scope = "profile email"
    request.session['state'] = state
    return RedirectResponse(f'https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&state={state}')

@app.post('/auth')
def signin(authorization_code , state):
    if state == state:
        return RedirectResponse()