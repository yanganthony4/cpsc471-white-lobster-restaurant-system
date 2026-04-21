from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import CustomerAccount
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerLogin, CustomerUpdate
from app.security import hash_password, verify_password

router = APIRouter()


def _make_username(email: str, db: Session) -> str:
    """Auto-generate a unique username from the email prefix."""
    base = email.split("@")[0].lower()
    candidate, suffix = base, 2
    while db.query(CustomerAccount).filter(CustomerAccount.username == candidate).first():
        candidate = f"{base}_{suffix}"; suffix += 1
    return candidate


@router.post("/", response_model=CustomerResponse)
def create_customer_account(customer_account: CustomerCreate, db: Session = Depends(get_db)):
    if db.query(CustomerAccount).filter(CustomerAccount.email == customer_account.email).first():
        raise HTTPException(400, detail="Customer account already exists")
    obj = CustomerAccount(
        email=customer_account.email,
        name=customer_account.name,
        username=_make_username(customer_account.email, db),  # FIX: was missing
        passwordHash=hash_password(customer_account.password),
        phoneNumber=customer_account.phoneNumber,
    )
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


@router.post("/login", response_model=CustomerResponse)
def login(login_data: CustomerLogin, db: Session = Depends(get_db)):
    acct = db.query(CustomerAccount).filter(CustomerAccount.email == login_data.email).first()
    if not acct or not verify_password(login_data.password, acct.passwordHash):
        raise HTTPException(401, detail="Invalid credentials")
    return acct


@router.get("/{customer_email}", response_model=CustomerResponse)
def get_customer_account_by_email(customer_email: str, db: Session = Depends(get_db)):
    acct = db.query(CustomerAccount).filter(CustomerAccount.email == customer_email).first()
    if not acct:
        raise HTTPException(404, detail="Customer account not found")
    return acct


@router.put("/{customer_email}", response_model=CustomerResponse)
def update_customer_account_by_email(customer_email: str, customer_update: CustomerUpdate, db: Session = Depends(get_db)):
    acct = db.query(CustomerAccount).filter(CustomerAccount.email == customer_email).first()
    if not acct:
        raise HTTPException(404, detail="Customer account not found")
    if customer_update.email != customer_email:
        if db.query(CustomerAccount).filter(CustomerAccount.email == customer_update.email).first():
            raise HTTPException(400, detail="Email already in use")
    acct.email = customer_update.email
    acct.name = customer_update.name
    acct.phoneNumber = customer_update.phoneNumber
    acct.passwordHash = hash_password(customer_update.password)
    db.commit(); db.refresh(acct)
    return acct
