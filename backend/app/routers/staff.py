from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.staff import StaffUser
from app.schemas.staff import StaffCreate, StaffLogin, StaffResponse, StaffUpdate
from app.security import hash_password, verify_password

router = APIRouter()
VALID_STAFF_ROLES = {"Host", "Server", "Manager", "Cashier"}


@router.get("/", response_model=List[StaffResponse])
def list_staff(db: Session = Depends(get_db)):
    return db.query(StaffUser).order_by(StaffUser.employeeID).all()


@router.post("/", response_model=StaffResponse)
def create_staff_account(staff_account: StaffCreate, db: Session = Depends(get_db)):
    if staff_account.role not in VALID_STAFF_ROLES:
        raise HTTPException(400, detail="Invalid staff role")
    if db.query(StaffUser).filter(StaffUser.employeeID == staff_account.employeeID).first():
        raise HTTPException(400, detail="Staff account already exists")
    obj = StaffUser(
        employeeID=staff_account.employeeID,
        role=staff_account.role,
        name=staff_account.name,
        username=f"emp_{staff_account.employeeID}",  # FIX: was missing
        passwordHash=hash_password(staff_account.password),
    )
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


@router.post("/login", response_model=StaffResponse)
def login_staff(login_data: StaffLogin, db: Session = Depends(get_db)):
    acct = db.query(StaffUser).filter(StaffUser.employeeID == login_data.employeeID).first()
    if not acct or not verify_password(login_data.password, acct.passwordHash):
        raise HTTPException(401, detail="Invalid credentials")
    return acct


@router.get("/{employee_id}", response_model=StaffResponse)
def get_staff_account(employee_id: int, db: Session = Depends(get_db)):
    acct = db.query(StaffUser).filter(StaffUser.employeeID == employee_id).first()
    if not acct:
        raise HTTPException(404, detail="Staff account not found")
    return acct


@router.put("/{employee_id}", response_model=StaffResponse)
def update_staff_account(employee_id: int, staff_update: StaffUpdate, db: Session = Depends(get_db)):
    acct = db.query(StaffUser).filter(StaffUser.employeeID == employee_id).first()
    if not acct:
        raise HTTPException(404, detail="Staff account not found")
    if staff_update.role not in VALID_STAFF_ROLES:
        raise HTTPException(400, detail="Invalid staff role")
    acct.role = staff_update.role
    acct.name = staff_update.name
    acct.passwordHash = hash_password(staff_update.password)
    db.commit(); db.refresh(acct)
    return acct
