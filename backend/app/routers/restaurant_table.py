from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.restaurant_table import RestaurantTable
from app.schemas.restaurant_table import (
    RestaurantTableCreate,
    RestaurantTableUpdate,
    RestaurantTableResponse,
)

# Create a router object to group all restaurant table-related endpoints together
router = APIRouter()

# Allowed status values for restaurant tables
VALID_TABLE_STATUSES = {"Available", "Occupied", "Reserved", "Out of Service"}


# POST /tables/
# Creates a new restaurant table
@router.post("/", response_model=RestaurantTableResponse)
def create_restaurant_table(
    restaurant_table: RestaurantTableCreate,
    db: Session = Depends(get_db)
) -> RestaurantTable:
    # Validate the table availability status
    if restaurant_table.availabilityStatus not in VALID_TABLE_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Invalid availability status"
        )

    # Check if a table with this composite key already exists
    existing_table = (
        db.query(RestaurantTable)
        .filter(
            RestaurantTable.tableNumber == restaurant_table.tableNumber,
            RestaurantTable.sectionName == restaurant_table.sectionName
        )
        .first()
    )

    # If the table already exists, stop and return an error
    if existing_table is not None:
        raise HTTPException(
            status_code=400,
            detail="Restaurant table already exists"
        )

    # Create a new RestaurantTable object from the validated request data
    new_table = RestaurantTable(
        tableNumber=restaurant_table.tableNumber,
        sectionName=restaurant_table.sectionName,
        availabilityStatus=restaurant_table.availabilityStatus,
        capacity=restaurant_table.capacity
    )

    # Add the new table to the database session
    db.add(new_table)

    # Save the new table row to the database
    db.commit()

    # Refresh the object so it reflects the current database state
    db.refresh(new_table)

    # Return the created table
    return new_table


# GET /tables/{section_name}/{table_number}
# Retrieves one restaurant table using its composite primary key
@router.get("/{section_name}/{table_number}", response_model=RestaurantTableResponse)
def get_restaurant_table(
    section_name: str,
    table_number: int,
    db: Session = Depends(get_db)
) -> RestaurantTable:
    # Find the table using both section name and table number
    restaurant_table = (
        db.query(RestaurantTable)
        .filter(
            RestaurantTable.sectionName == section_name,
            RestaurantTable.tableNumber == table_number
        )
        .first()
    )

    # If the table does not exist, return an HTTP 404 error
    if restaurant_table is None:
        raise HTTPException(
            status_code=404,
            detail="Restaurant table not found"
        )

    # Return the table if found
    return restaurant_table


# PUT /tables/{section_name}/{table_number}
# Updates a restaurant table's status and capacity
@router.put("/{section_name}/{table_number}", response_model=RestaurantTableResponse)
def update_restaurant_table(
    section_name: str,
    table_number: int,
    update: RestaurantTableUpdate,
    db: Session = Depends(get_db)
) -> RestaurantTable:
    # Validate the updated availability status
    if update.availabilityStatus not in VALID_TABLE_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Invalid availability status"
        )

    # Find the table using both section name and table number
    restaurant_table = (
        db.query(RestaurantTable)
        .filter(
            RestaurantTable.sectionName == section_name,
            RestaurantTable.tableNumber == table_number
        )
        .first()
    )

    # If the table does not exist, return an HTTP 404 error
    if restaurant_table is None:
        raise HTTPException(
            status_code=404,
            detail="Restaurant table not found"
        )

    # Apply the updated values
    restaurant_table.availabilityStatus = update.availabilityStatus
    restaurant_table.capacity = update.capacity

    # Save the updated table
    db.commit()

    # Refresh the object so it reflects the latest database state
    db.refresh(restaurant_table)

    # Return the updated table
    return restaurant_table


# DELETE /tables/{section_name}/{table_number}
# Deletes a restaurant table using its composite primary key
@router.delete("/{section_name}/{table_number}")
def delete_restaurant_table(
    section_name: str,
    table_number: int,
    db: Session = Depends(get_db)
) -> dict[str, str]:
    # Find the table using both section name and table number
    restaurant_table = (
        db.query(RestaurantTable)
        .filter(
            RestaurantTable.sectionName == section_name,
            RestaurantTable.tableNumber == table_number
        )
        .first()
    )

    # If the table does not exist, return an HTTP 404 error
    if restaurant_table is None:
        raise HTTPException(
            status_code=404,
            detail="Restaurant table not found"
        )

    # Delete the table
    db.delete(restaurant_table)

    # Commit the delete operation
    db.commit()

    # Return a simple success message
    return {"message": "Restaurant table successfully deleted"}