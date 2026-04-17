from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.restaurant_table import RestaurantTable
from app.schemas.restaurant_table import (
    RestaurantTableCreate, RestaurantTableUpdate, RestaurantTableResponse,
)

router = APIRouter()
VALID_TABLE_STATUSES = {"Available", "Occupied", "Reserved", "Out of Service"}


# GET /tables/?section=Main+Dining  — all tables, optionally by section
@router.get("/", response_model=List[RestaurantTableResponse])
def list_tables(
    section: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(RestaurantTable)
    if section:
        q = q.filter(RestaurantTable.sectionName == section)
    return q.order_by(RestaurantTable.sectionName, RestaurantTable.tableNumber).all()


# POST /tables/
@router.post("/", response_model=RestaurantTableResponse)
def create_restaurant_table(restaurant_table: RestaurantTableCreate, db: Session = Depends(get_db)):
    if restaurant_table.availabilityStatus not in VALID_TABLE_STATUSES:
        raise HTTPException(400, detail="Invalid availability status")
    if db.query(RestaurantTable).filter(
        RestaurantTable.tableNumber == restaurant_table.tableNumber,
        RestaurantTable.sectionName == restaurant_table.sectionName,
    ).first():
        raise HTTPException(400, detail="Restaurant table already exists")
    obj = RestaurantTable(
        tableNumber=restaurant_table.tableNumber,
        sectionName=restaurant_table.sectionName,
        availabilityStatus=restaurant_table.availabilityStatus,
        capacity=restaurant_table.capacity,
    )
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


# GET /tables/{section_name}/{table_number}
@router.get("/{section_name}/{table_number}", response_model=RestaurantTableResponse)
def get_restaurant_table(section_name: str, table_number: int, db: Session = Depends(get_db)):
    obj = db.query(RestaurantTable).filter(
        RestaurantTable.sectionName == section_name,
        RestaurantTable.tableNumber == table_number,
    ).first()
    if not obj:
        raise HTTPException(404, detail="Restaurant table not found")
    return obj


# PUT /tables/{section_name}/{table_number}
@router.put("/{section_name}/{table_number}", response_model=RestaurantTableResponse)
def update_restaurant_table(section_name: str, table_number: int, update: RestaurantTableUpdate, db: Session = Depends(get_db)):
    if update.availabilityStatus not in VALID_TABLE_STATUSES:
        raise HTTPException(400, detail="Invalid availability status")
    obj = db.query(RestaurantTable).filter(
        RestaurantTable.sectionName == section_name,
        RestaurantTable.tableNumber == table_number,
    ).first()
    if not obj:
        raise HTTPException(404, detail="Restaurant table not found")
    obj.availabilityStatus = update.availabilityStatus
    obj.capacity = update.capacity
    db.commit(); db.refresh(obj)
    return obj


# DELETE /tables/{section_name}/{table_number}
@router.delete("/{section_name}/{table_number}")
def delete_restaurant_table(section_name: str, table_number: int, db: Session = Depends(get_db)):
    obj = db.query(RestaurantTable).filter(
        RestaurantTable.sectionName == section_name,
        RestaurantTable.tableNumber == table_number,
    ).first()
    if not obj:
        raise HTTPException(404, detail="Restaurant table not found")
    db.delete(obj); db.commit()
    return {"message": "Restaurant table successfully deleted"}