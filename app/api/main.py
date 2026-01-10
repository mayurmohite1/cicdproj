from fastapi import FastAPI
from dotenv import load_dotenv
from api.controllers import journal_router
from api.loging import logger

load_dotenv()

app = FastAPI(title="Logging API")
app.include_router(journal_router)