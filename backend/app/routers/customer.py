from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import CustomerAccount
from app.schemas.customer import (
    CustomerCreate,
    CustomerResponse,
    CustomerLogin,
    CustomerUpdate,
)
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
    # Check whether a customer with this email already exists
    existing_customer = (
        db.query(CustomerAccount)
        .filter(CustomerAccount.email == customer_account.email)
        .first()
    )

    # Stop the request if the email is already in use
    if existing_customer is not None:
        raise HTTPException(
            status_code=400,
            detail="Customer account already exists"
        )

    # Hash the plain-text password before storing it in the database
    hashed_password = hash_password(customer_account.password)

    # Create a new CustomerAccount object using the request data
    new_customer = CustomerAccount(
        email=customer_account.email,
        name=customer_account.name,
        passwordHash=hashed_password,
        phoneNumber=customer_account.phoneNumber
    )

    # Add the new customer to the database session
    db.add(new_customer)

    # Save the new customer row to the database
    db.commit()

    # Refresh the object so it includes the latest saved database state
    db.refresh(new_customer)

    # Return the created customer account
    return new_customer


# POST /customers/login
# Logs a customer in by checking email and password
@router.post("/login", response_model=CustomerResponse)
def login(
    login_data: CustomerLogin,
    db: Session = Depends(get_db)
) -> CustomerResponse:
    # Look up the customer account using the provided email
    customer_account = (
        db.query(CustomerAccount)
        .filter(CustomerAccount.email == login_data.email)
        .first()
    )

    # If no matching customer is found, return an invalid credentials error
    if customer_account is None:
        raise HTTPException(
            status_code=404,
            detail="Invalid credentials"
        )

    # Compare the provided password to the stored hashed password
    if not verify_password(login_data.password, customer_account.passwordHash):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    # Return the customer account if login succeeds
    return customer_account


# GET /customers/by-email/{customer_email}
# Retrieves a customer account using the customer's email
@router.get("/{customer_email}", response_model=CustomerResponse)
def get_customer_account_by_email(
    customer_email: str,
    db: Session = Depends(get_db)
) -> CustomerResponse:
    # Find the customer record that matches the email in the URL path
    customer_account = (
        db.query(CustomerAccount)
        .filter(CustomerAccount.email == customer_email)
        .first()
    )

    # Return a not found error if no customer matches the email
    if customer_account is None:
        raise HTTPException(
            status_code=404,
            detail="Customer account not found"
        )

    # Return the matching customer record
    return customer_account


# PUT /customers/by-email/{customer_email}
# Updates an existing customer account using the customer's current email
@router.put("/{customer_email}", response_model=CustomerResponse)
def update_customer_account_by_email(
    customer_email: str,
    customer_update: CustomerUpdate,
    db: Session = Depends(get_db)
) -> CustomerResponse:
    # Find the current customer record using the email in the URL path
    customer_account = (
        db.query(CustomerAccount)
        .filter(CustomerAccount.email == customer_email)
        .first()
    )

    # If the customer does not exist, stop and return an error
    if customer_account is None:
        raise HTTPException(
            status_code=404,
            detail="Customer account not found"
        )

    # Check whether the new email is already used by a different customer
    existing_email = (
        db.query(CustomerAccount)
        .filter(
            CustomerAccount.email == customer_update.email,
            CustomerAccount.email != customer_email
        )
        .first()
    )

    # If the new email belongs to another customer, stop and return an error
    if existing_email is not None:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    # Update the customer's email, name, and phone number
    customer_account.email = customer_update.email
    customer_account.name = customer_update.name
    customer_account.phoneNumber = customer_update.phoneNumber

    # Hash the new password and replace the old stored password hash
    customer_account.passwordHash = hash_password(customer_update.password)

    # Save the updated customer data to the database
    db.commit()

    # Refresh the object so it reflects the current database state
    db.refresh(customer_account)

    # Return the updated customer record
    return customer_account