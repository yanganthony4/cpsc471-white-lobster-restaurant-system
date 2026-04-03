from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.staff import StaffUser
from app.schemas.staff import StaffCreate, StaffLogin, StaffResponse, StaffUpdate
from app.security import hash_password, verify_password

# Create a router object to group all staff-related endpoints together
router = APIRouter()

# List of valid staff roles allowed by the business rules / database constraint
VALID_STAFF_ROLES = {"Host", "Server", "Manager", "Cashier"}


# POST /staff/
# Creates a new staff account
@router.post("/", response_model=StaffResponse)
def create_staff_account(
    staff_account: StaffCreate,
    db: Session = Depends(get_db)
) -> StaffResponse:
    # Make sure the provided role is valid
    if staff_account.role not in VALID_STAFF_ROLES:
        raise HTTPException(
            status_code=400,
            detail="Invalid staff role"
        )

    # Check whether the employee ID already exists
    existing_staff = (
        db.query(StaffUser)
        .filter(StaffUser.employeeID == staff_account.employeeID)
        .first()
    )

    # If a staff account with this employee ID already exists, stop and return an error
    if existing_staff is not None:
        raise HTTPException(
            status_code=400,
            detail="Staff account already exists"
        )

    # Hash the plain-text password before storing it in the database
    hashed_password = hash_password(staff_account.password)

    # Create a new StaffUser object using the validated request data
    new_staff = StaffUser(
        employeeID=staff_account.employeeID,
        role=staff_account.role,
        name=staff_account.name,
        passwordHash=hashed_password
    )

    # Add the new staff object to the current database session
    db.add(new_staff)

    # Save the new staff row to the database
    db.commit()

    # Refresh the object so it reflects the current database state
    db.refresh(new_staff)

    # Return the created staff account without exposing the password hash
    return new_staff


# POST /staff/login
# Logs a staff member in by checking employee ID and password
@router.post("/login", response_model=StaffResponse)
def login_staff(
    login_data: StaffLogin,
    db: Session = Depends(get_db)
) -> StaffResponse:
    # Find the staff account by employee ID
    staff_account = (
        db.query(StaffUser)
        .filter(StaffUser.employeeID == login_data.employeeID)
        .first()
    )

    # If no staff account matches this employee ID, return a login failure
    if staff_account is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    # Compare the entered password with the stored hashed password
    if not verify_password(login_data.password, staff_account.passwordHash):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    # Return the staff account if login succeeds
    return staff_account


# GET /staff/{employee_id}
# Retrieves a staff account by employee ID
@router.get("/{employee_id}", response_model=StaffResponse)
def get_staff_account(
    employee_id: int,
    db: Session = Depends(get_db)
) -> StaffResponse:
    # Query the database for the staff account with this employee ID
    staff_account = (
        db.query(StaffUser)
        .filter(StaffUser.employeeID == employee_id)
        .first()
    )

    # If no staff account is found, return an HTTP 404 error
    if staff_account is None:
        raise HTTPException(
            status_code=404,
            detail="Staff account not found"
        )

    # Return the staff account if found
    return staff_account


# PUT /staff/{employee_id}
# Updates a staff account by employee ID
@router.put("/{employee_id}", response_model=StaffResponse)
def update_staff_account(
    employee_id: int,
    staff_update: StaffUpdate,
    db: Session = Depends(get_db)
) -> StaffResponse:
    # Find the current staff account using the employee ID
    staff_account = (
        db.query(StaffUser)
        .filter(StaffUser.employeeID == employee_id)
        .first()
    )

    # If the staff account does not exist, stop and return an error
    if staff_account is None:
        raise HTTPException(
            status_code=404,
            detail="Staff account not found"
        )

    # Make sure the provided role is valid
    if staff_update.role not in VALID_STAFF_ROLES:
        raise HTTPException(
            status_code=400,
            detail="Invalid staff role"
        )

    # Update the staff account fields
    staff_account.role = staff_update.role
    staff_account.name = staff_update.name
    staff_account.passwordHash = hash_password(staff_update.password)

    # Save the updated staff data to the database
    db.commit()

    # Refresh the object so it reflects the current database state
    db.refresh(staff_account)

    # Return the updated staff account
    return staff_account