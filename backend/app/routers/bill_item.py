from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.database import get_db
from app.models.bill import Bill
from app.models.bill_item import BillItem
from app.models.menu_item import MenuItem
from app.schemas.bill_item import BillItemCreate, BillItemResponse, BillItemUpdate

router = APIRouter()


# GET /bill-items/by-invoice/{invoice_id}  — all items on a bill
@router.get("/by-invoice/{invoice_id}", response_model=List[BillItemResponse])
def list_bill_items_for_invoice(invoice_id: int, db: Session = Depends(get_db)):
    return db.query(BillItem).filter(BillItem.invoiceID == invoice_id).all()


# POST /bill-items/
@router.post("/", response_model=BillItemResponse)
def create_bill_item(bill_item: BillItemCreate, db: Session = Depends(get_db)):
    # Without this check a missing invoiceID causes an FK IntegrityError
    if not db.query(Bill).filter(Bill.invoiceID == bill_item.invoiceID).first():
        raise HTTPException(
            status_code=404,
            detail=f"Bill with invoiceID {bill_item.invoiceID} not found.",
        )

    # Without this check a missing menuItemID also causes an FK IntegrityError
    if not db.query(MenuItem).filter(MenuItem.menuItemID == bill_item.menuItemID).first():
        raise HTTPException(
            status_code=404,
            detail=f"Menu item {bill_item.menuItemID} not found.",
        )

    if db.query(BillItem).filter(
        BillItem.invoiceID  == bill_item.invoiceID,
        BillItem.menuItemID == bill_item.menuItemID,
    ).first():
        raise HTTPException(
            status_code=400,
            detail=(
                f"Bill item already exists for invoice {bill_item.invoiceID} "
                f"and menu item {bill_item.menuItemID}."
            ),
        )

    try:
        obj = BillItem(
            invoiceID=bill_item.invoiceID,
            menuItemID=bill_item.menuItemID,
            quantity=bill_item.quantity,
            priceAtOrder=bill_item.priceAtOrder,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Database integrity error: {exc.orig}",
        )


# GET /bill-items/{invoice_id}/{menu_item_id}
@router.get("/{invoice_id}/{menu_item_id}", response_model=BillItemResponse)
def get_bill_item(invoice_id: int, menu_item_id: int, db: Session = Depends(get_db)):
    obj = db.query(BillItem).filter(
        BillItem.invoiceID  == invoice_id,
        BillItem.menuItemID == menu_item_id,
    ).first()
    if obj is None:
        raise HTTPException(status_code=404, detail="Bill item not found.")
    return obj


# PUT /bill-items/{invoice_id}/{menu_item_id}
@router.put("/{invoice_id}/{menu_item_id}", response_model=BillItemResponse)
def update_bill_item(
    invoice_id: int,
    menu_item_id: int,
    update: BillItemUpdate,
    db: Session = Depends(get_db),
):
    obj = db.query(BillItem).filter(
        BillItem.invoiceID  == invoice_id,
        BillItem.menuItemID == menu_item_id,
    ).first()
    if obj is None:
        raise HTTPException(status_code=404, detail="Bill item not found.")
    obj.quantity     = update.quantity
    obj.priceAtOrder = update.priceAtOrder
    db.commit()
    db.refresh(obj)
    return obj


# DELETE /bill-items/{invoice_id}/{menu_item_id}
@router.delete("/{invoice_id}/{menu_item_id}")
def delete_bill_item(
    invoice_id: int,
    menu_item_id: int,
    db: Session = Depends(get_db),
):
    obj = db.query(BillItem).filter(
        BillItem.invoiceID  == invoice_id,
        BillItem.menuItemID == menu_item_id,
    ).first()
    if obj is None:
        raise HTTPException(status_code=404, detail="Bill item not found.")
    db.delete(obj)
    db.commit()
    return {"message": "Bill item successfully deleted"}