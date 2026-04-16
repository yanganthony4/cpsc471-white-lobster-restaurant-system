from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.menu_item import MenuItem
from app.schemas.menu_item import MenuItemCreate, MenuItemResponse, MenuItemUpdate

# Create a router object to group all menu item endpoints together
router = APIRouter()


# POST /menu-items/
# Creates a new menu item
@router.post("/", response_model=MenuItemResponse)
def create_menu_item(
    menu_item: MenuItemCreate,
    db: Session = Depends(get_db)
) -> MenuItem:
    # Check whether a menu item with the same name already exists
    # Remove this block if duplicate names should be allowed
    existing_menu_item = (
        db.query(MenuItem)
        .filter(MenuItem.name == menu_item.name)
        .first()
    )

    # If a menu item with this name already exists, stop and return an error
    if existing_menu_item is not None:
        raise HTTPException(
            status_code=400,
            detail="Menu item already exists"
        )

    # Create a new MenuItem object from the validated request data
    new_menu_item = MenuItem(
        description=menu_item.description,
        currentPrice=menu_item.currentPrice,
        name=menu_item.name
    )

    # Add the new menu item to the current database session
    db.add(new_menu_item)

    # Save the new row to the database
    db.commit()

    # Refresh the object so the auto-generated menuItemID is available
    db.refresh(new_menu_item)

    # Return the created menu item
    return new_menu_item


# GET /menu-items/{menu_item_id}
# Retrieves one menu item by ID
@router.get("/{menu_item_id}", response_model=MenuItemResponse)
def get_menu_item(
    menu_item_id: int,
    db: Session = Depends(get_db)
) -> MenuItem:
    # Query the database for the menu item with this ID
    menu_item = (
        db.query(MenuItem)
        .filter(MenuItem.menuItemID == menu_item_id)
        .first()
    )

    # If the menu item does not exist, return an HTTP 404 error
    if menu_item is None:
        raise HTTPException(
            status_code=404,
            detail="Menu item not found"
        )

    # Return the menu item if found
    return menu_item


# PUT /menu-items/{menu_item_id}
# Updates an existing menu item
@router.put("/{menu_item_id}", response_model=MenuItemResponse)
def update_menu_item(
    menu_item_id: int,
    update: MenuItemUpdate,
    db: Session = Depends(get_db)
) -> MenuItem:
    # Find the menu item by ID
    menu_item = (
        db.query(MenuItem)
        .filter(MenuItem.menuItemID == menu_item_id)
        .first()
    )

    # If the menu item does not exist, return an HTTP 404 error
    if menu_item is None:
        raise HTTPException(
            status_code=404,
            detail="Menu item not found"
        )

    # Optional duplicate-name check
    existing_name = (
        db.query(MenuItem)
        .filter(
            MenuItem.name == update.name,
            MenuItem.menuItemID != menu_item_id
        )
        .first()
    )

    if existing_name is not None:
        raise HTTPException(
            status_code=400,
            detail="Another menu item already uses this name"
        )

    # Apply the updated values
    menu_item.description = update.description
    menu_item.currentPrice = update.currentPrice
    menu_item.name = update.name

    # Save the updated row
    db.commit()

    # Refresh the object so it reflects the latest database state
    db.refresh(menu_item)

    # Return the updated menu item
    return menu_item


# DELETE /menu-items/{menu_item_id}
# Deletes a menu item by ID
@router.delete("/{menu_item_id}")
def delete_menu_item(
    menu_item_id: int,
    db: Session = Depends(get_db)
) -> dict[str, str]:
    # Find the menu item by ID
    menu_item = (
        db.query(MenuItem)
        .filter(MenuItem.menuItemID == menu_item_id)
        .first()
    )

    # If the menu item does not exist, return an HTTP 404 error
    if menu_item is None:
        raise HTTPException(
            status_code=404,
            detail="Menu item not found"
        )

    # Delete the menu item from the database
    db.delete(menu_item)

    # Commit the delete operation
    db.commit()

    # Return a simple success message
    return {"message": "Menu item successfully deleted"}