from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.bill_item import BillItem
from app.schemas.bill_item import BillItemCreate, BillItemResponse, BillItemUpdate

router = APIRouter()


# GET /bill-items/by-invoice/{invoice_id}  — all items on a bill
@router.get("/by-invoice/{invoice_id}", response_model=List[BillItemResponse])
def list_bill_items_for_invoice(invoice_id: int, db: Session = Depends(get_db)):
    return db.query(BillItem).filter(BillItem.invoiceID == invoice_id).all()


# POST /bill-items/
@router.post("/", response_model=BillItemResponse)
def create_bill_item(bill_item: BillItemCreate, db: Session = Depends(get_db)):
    if db.query(BillItem).filter(
        BillItem.invoiceID == bill_item.invoiceID,
        BillItem.menuItemID == bill_item.menuItemID,
    ).first():
        raise HTTPException(400, detail="Bill item already exists for this invoice and menu item")
    obj = BillItem(
        invoiceID=bill_item.invoiceID,
        menuItemID=bill_item.menuItemID,
        quantity=bill_item.quantity,
        priceAtOrder=bill_item.priceAtOrder,
    )
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


# GET /bill-items/{invoice_id}/{menu_item_id}
@router.get("/{invoice_id}/{menu_item_id}", response_model=BillItemResponse)
def get_bill_item(invoice_id: int, menu_item_id: int, db: Session = Depends(get_db)):
    obj = db.query(BillItem).filter(
        BillItem.invoiceID == invoice_id, BillItem.menuItemID == menu_item_id
    ).first()
    if not obj:
        raise HTTPException(404, detail="Bill item not found")
    return obj


# PUT /bill-items/{invoice_id}/{menu_item_id}
@router.put("/{invoice_id}/{menu_item_id}", response_model=BillItemResponse)
def update_bill_item(invoice_id: int, menu_item_id: int, update: BillItemUpdate, db: Session = Depends(get_db)):
    obj = db.query(BillItem).filter(
        BillItem.invoiceID == invoice_id, BillItem.menuItemID == menu_item_id
    ).first()
    if not obj:
        raise HTTPException(404, detail="Bill item not found")
    obj.quantity = update.quantity
    obj.priceAtOrder = update.priceAtOrder
    db.commit(); db.refresh(obj)
    return obj


# DELETE /bill-items/{invoice_id}/{menu_item_id}
@router.delete("/{invoice_id}/{menu_item_id}")
def delete_bill_item(invoice_id: int, menu_item_id: int, db: Session = Depends(get_db)):
    obj = db.query(BillItem).filter(
        BillItem.invoiceID == invoice_id, BillItem.menuItemID == menu_item_id
    ).first()
    if not obj:
        raise HTTPException(404, detail="Bill item not found")
    db.delete(obj); db.commit()
    return {"message": "Bill item successfully deleted"}