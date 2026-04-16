from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.bill_item import BillItem
from app.schemas.bill_item import BillItemCreate, BillItemResponse, BillItemUpdate

# Create a router object to group all bill item-related endpoints together
router = APIRouter()


# POST /bill-items/
# Creates a new bill item
@router.post("/", response_model=BillItemResponse)
def create_bill_item(
    bill_item: BillItemCreate,
    db: Session = Depends(get_db)
) -> BillItem:
    # Check whether this exact invoiceID + menuItemID pair already exists
    existing_bill_item = (
        db.query(BillItem)
        .filter(
            BillItem.invoiceID == bill_item.invoiceID,
            BillItem.menuItemID == bill_item.menuItemID
        )
        .first()
    )

    # Since the composite key must be unique, reject duplicates
    if existing_bill_item is not None:
        raise HTTPException(
            status_code=400,
            detail="Bill item already exists for this invoice and menu item"
        )

    # Create a new BillItem object from the validated request data
    new_bill_item = BillItem(
        invoiceID=bill_item.invoiceID,
        menuItemID=bill_item.menuItemID,
        quantity=bill_item.quantity,
        priceAtOrder=bill_item.priceAtOrder
    )

    # Add the new bill item to the current database session
    db.add(new_bill_item)

    # Save the new row to the database
    db.commit()

    # Refresh the object so it reflects the current database state
    db.refresh(new_bill_item)

    # Return the created bill item
    return new_bill_item


# GET /bill-items/{invoice_id}/{menu_item_id}
# Retrieves one bill item using its composite primary key
@router.get("/{invoice_id}/{menu_item_id}", response_model=BillItemResponse)
def get_bill_item(
    invoice_id: int,
    menu_item_id: int,
    db: Session = Depends(get_db)
) -> BillItem:
    # Find the bill item using both invoice ID and menu item ID
    bill_item = (
        db.query(BillItem)
        .filter(
            BillItem.invoiceID == invoice_id,
            BillItem.menuItemID == menu_item_id
        )
        .first()
    )

    # If the bill item does not exist, return an HTTP 404 error
    if bill_item is None:
        raise HTTPException(
            status_code=404,
            detail="Bill item not found"
        )

    # Return the bill item if found
    return bill_item


# PUT /bill-items/{invoice_id}/{menu_item_id}
# Updates an existing bill item
@router.put("/{invoice_id}/{menu_item_id}", response_model=BillItemResponse)
def update_bill_item(
    invoice_id: int,
    menu_item_id: int,
    update: BillItemUpdate,
    db: Session = Depends(get_db)
) -> BillItem:
    # Find the bill item using both invoice ID and menu item ID
    bill_item = (
        db.query(BillItem)
        .filter(
            BillItem.invoiceID == invoice_id,
            BillItem.menuItemID == menu_item_id
        )
        .first()
    )

    # If the bill item does not exist, return an HTTP 404 error
    if bill_item is None:
        raise HTTPException(
            status_code=404,
            detail="Bill item not found"
        )

    # Apply the updated values
    bill_item.quantity = update.quantity
    bill_item.priceAtOrder = update.priceAtOrder

    # Save the updated bill item
    db.commit()

    # Refresh the object so it reflects the latest database state
    db.refresh(bill_item)

    # Return the updated bill item
    return bill_item


# DELETE /bill-items/{invoice_id}/{menu_item_id}
# Deletes a bill item using its composite primary key
@router.delete("/{invoice_id}/{menu_item_id}")
def delete_bill_item(
    invoice_id: int,
    menu_item_id: int,
    db: Session = Depends(get_db)
) -> dict[str, str]:
    # Find the bill item using both invoice ID and menu item ID
    bill_item = (
        db.query(BillItem)
        .filter(
            BillItem.invoiceID == invoice_id,
            BillItem.menuItemID == menu_item_id
        )
        .first()
    )

    # If the bill item does not exist, return an HTTP 404 error
    if bill_item is None:
        raise HTTPException(
            status_code=404,
            detail="Bill item not found"
        )

    # Delete the bill item from the database
    db.delete(bill_item)

    # Commit the delete operation
    db.commit()

    # Return a simple success message
    return {"message": "Bill item successfully deleted"}