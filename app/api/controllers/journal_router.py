import logging
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from api.repositories.postgres_repository import PostgresDB
from api.services import EntryService
from api.loging import logger
from pydantic import BaseModel

router = APIRouter()

class Entry(BaseModel):
    work: str
    struggle: str
    intention: str

async def get_entry_service() -> AsyncGenerator[EntryService, None]:

    async with PostgresDB() as db:
        yield EntryService(db)

@router.post("/entries")
async def create_entry(request: Request, entry: Entry, entry_service: EntryService = Depends(get_entry_service)):
    logger.info("Initiating POST /entries/")
    entry_data = {
        k: v for k, v in entry.model_dump().items()
        if k not in ['id', 'created_at', 'updated_at']
    }
    async with PostgresDB() as db:
        entry_service = EntryService(db)
        try:
            enriched_entry = await entry_service.create_entry(entry_data)
            await entry_service.db.create_entry(enriched_entry)
  
        except HTTPException as e:
          
            if e.status_code == 409:
                raise HTTPException(
                    status_code=409, detail="You already have an entry for today."
                )
            raise e
    return JSONResponse(content={"detail": "Entry created successfully"}, status_code=201)

@router.get("/entries")
async def get_all_entries(request: Request):
    logger.info('Initiating GET /entries')
    async with PostgresDB() as db:
        entry_service = EntryService(db)
        try:
            data = await entry_service.get_all_entries()
            revised_data = []
            for row in data:
                revised_data.append({
                    "id": row["id"],
                    "work": row["data"]["work"],
                    "struggle": row["data"]["struggle"],
                    "intention": row["data"]["intention"]
                })
        except HTTPException as e:
            raise e
        return revised_data

@router.get("/entries/{entry_id}")
async def get_entry(request: Request, entry_id: str):
    logger.info("Initiating GET /entries/:entry_id")
    async with PostgresDB() as db:
        entry_service = EntryService(db)
        try:
            result = await entry_service.get_entry(entry_id)
            revised_result = {
                "id": result["id"],
                "work": result["data"]["work"],
                "struggle": result["data"]["struggle"],
                "intention": result["data"]["intention"]
            }
            return revised_result
        except HTTPException as e:
            if (e.status_code == 404):
                raise HTTPException(
                    status_code=404,
                    detail="Entry not found."
                )

@router.patch("/entries/{entry_id}")
async def update_entry(request: Request, entry_id: str, entry_update: dict):
    logger.info("Initiating PATCH request")
    async with PostgresDB() as db:
        entry_service = EntryService(db)
        result = await entry_service.update_entry(entry_id, entry_update)
    if not result:
    
        raise HTTPException(status_code=404, detail="Entry not found")
  
    return result

@router.delete("/entries/{entry_id}")
async def delete_entry(request: Request, entry_id: str):
    # TODO: Implement delete entry endpoint
    # Hint: Return 404 if entry not found
    logger.info("Initiating DELETE /entries/:id")
    async with PostgresDB() as db:
        entry_service = EntryService(db)
        await entry_service.delete_entry(entry_id)

@router.delete("/entries")
async def delete_all_entries(request: Request):
   
    async with PostgresDB() as db:
        entry_service = EntryService(db)
        await entry_service.delete_all_entries()

    return {"detail": "All entries deleted"}