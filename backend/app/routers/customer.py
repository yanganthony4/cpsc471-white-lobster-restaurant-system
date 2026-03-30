from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import CustomerAccount
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerLogin
from app.security import hash_password, verify_password

# Create a router object to group all customer-related endpoints together
router = APIRouter()


# POST /customers/
# Creates a new customer account
@router.post("/", response_model=CustomerResponse)
def create_customer_account(
    customer_account: CustomerCreate,
    db: Session = Depends(get_db)
) -> CustomerResponse:
    # Check if a customer account already exists with the same email
    existing_customer = (
        db.query(CustomerAccount)
        .filter(CustomerAccount.email == customer_account.email)
        .first()
    )

    # If an account with this email already exists, stop and return an error
    if existing_customer is not None:
        raise HTTPException(
            status_code=400,
            detail="Customer account already exists"
        )

    # Check if the chosen username is already taken
    existing_username = (
        db.query(CustomerAccount)
        .filter(CustomerAccount.username == customer_account.username)
        .first()
    )

    # If the username is already in use, stop and return an error
    if existing_username is not None:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    # Hash the plain-text password before storing it in the database
    hashed_password = hash_password(customer_account.password)

    # Create a new CustomerAccount object using the validated request data
    new_customer = CustomerAccount(
        email=customer_account.email,
        name=customer_account.name,
        username=customer_account.username,
        passwordHash=hashed_password,
        phoneNumber=customer_account.phoneNumber
    )

    # Add the new customer object to the current database session
    db.add(new_customer)

    # Save the new customer row to the database
    db.commit()

    # Refresh the object so it reflects the current database state
    db.refresh(new_customer)

    # Return the created customer account as the API response
    return new_customer


# POST /customers/login
# Logs a customer in by checking username and password
@router.post("/login", response_model=CustomerResponse)
def login(
    login_data: CustomerLogin,
    db: Session = Depends(get_db)
) -> CustomerResponse:
    # Look up the customer account by username
    customer_account = (
        db.query(CustomerAccount)
        .filter(CustomerAccount.username == login_data.username)
        .first()
    )

    # If no matching account is found, return an invalid credentials error
    if customer_account is None:
        raise HTTPException(
            status_code=404,
            detail="Invalid credentials"
        )

    # Compare the entered password with the stored hashed password
    # If they do not match, return an invalid credentials error
    if not verify_password(login_data.password, customer_account.passwordHash):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    # Return the customer account if login is successful
    return customer_account