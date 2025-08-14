from fastapi import FastAPI
from pydantic import BaseModel , EmailStr



app = FastAPI()



@app.get('/')
def hello ():
    return "Hello world"