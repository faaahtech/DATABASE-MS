from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from repositories.postgres_conn import engine
from sqlalchemy import text

app = FastAPI()

#set CORS config for deploy

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000"], 
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)


@app.get("/healthcheck")
def healthcheck_database():
    return {"Status": "Online","Service": "API" , "Version": "1.0.0","Current_Time": datetime.today()}


@app.get("/healthcheck/database")
async def healthcheck_database():
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return {"Status": "Online","Service": "Database", "Version": "1.0.0","Current_Time": datetime.today()}
    except:
        return {"Status": "Offline","Service": "Database" ,"Version": "1.0.0","Current_Time": datetime.today()}
