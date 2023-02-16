# app/main.py

import json
from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import ormar

from app.db import ContactInformation, GenderChoice, database, Lifter


app = FastAPI(title="FastAPI, Docker, Alembic and PostgreSQL")

class LifterRequest(BaseModel):
    first_name: str
    family_name: str
    gender: GenderChoice
    id_number: str
    address: str
    postal_code: str
    postal_city: str
    phone: str
    email: str

@app.get("/")
def root():
    return "Stark Lifter database system"

@app.post("/lifter", status_code=status.HTTP_201_CREATED)
async def create_lifter(request: LifterRequest):
    contact_info = await ContactInformation.objects.create(address=request.address, 
                                                           postal_code=request.postal_code, 
                                                           postal_city=request.postal_city, 
                                                           phone=request.phone, 
                                                           email=request.email)
    lifter = await Lifter.objects.create(first_name=request.first_name, family_name=request.family_name, gender=request.gender, id_number=request.id_number, contact_information=contact_info)
    return json.dumps(jsonable_encoder(lifter))

@app.get("/lifter/{id}")
async def read_lifter(id: int):
    lifter = await Lifter.objects.get(id=id)
    return json.dumps(jsonable_encoder(lifter))

@app.put("/lifter/{id}")
async def update_lifter(id: int, request: LifterRequest):
    database = Lifter.Meta.database
    lifter = await Lifter.objects.get(id=id)
    contact_info = lifter.contact_information
    lifter.update_from_dict({"first_name": request.first_name, "family_name": request.family_name, "gender": request.gender, "id_number": request.id_number})
    contact_info.update_from_dict({"address": request.address, "postal_code": request.postal_code, "postal_city": request.postal_city, "phone": request.phone, "email": request.email})
    async with database.transaction():
        await lifter.update()
        await contact_info.update()
    return json.dumps(jsonable_encoder(lifter))

@app.delete("/lifter/{id}")
async def delete_lifter(id: int):
    await Lifter.objects.delete(id=id)
    return f"deleted lifter with id {id}"

@app.get("/lifter")
async def read_lifter_list():
    lifters = await Lifter.objects.all()
    return json.dumps([jsonable_encoder(x) for x in lifters])

@app.on_event("startup")
async def startup():
    if not database.is_connected:
        await database.connect()

@app.on_event("shutdown")
async def shutdown():
    if database.is_connected:
        await database.disconnect()
