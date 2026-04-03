from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

# Import the database engine so we can test whether the app can reach MySQL
from app.database import engine

# Import all router files that contain grouped API endpoints
from app.routers import (
    bill,
    bill_item,
    customer,
    loyalty,
    menu_item,
    payment,
    promotion,
    reservation,
    restaurant_table,
    section,
    seating_assignment,
    staff,
    waitlistentry,
)

# Create the main FastAPI application object
app = FastAPI(title="Restaurant System API")

# Add CORS middleware so the React frontend can make requests to this backend
# This is especially important when frontend and backend run on different ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the customer router
# All routes inside customer.router will now be available under /customers
app.include_router(customer.router, prefix="/customers", tags=["Customers"])

# Register the loyalty router
# All routes inside loyalty.router will now be available under /loyalty
app.include_router(loyalty.router, prefix="/loyalty", tags=["Loyalty"])

# Register the staff router
app.include_router(staff.router, prefix="/staff", tags=["Staff"])

# Register the reservation router
app.include_router(reservation.router, prefix="/reservation", tags=["Reservations"])

# Register the waitlist router
app.include_router(waitlistentry.router, prefix="/waitlist", tags=["Waitlist"])

# Register the section router
app.include_router(section.router, prefix="/sections", tags=["Sections"])

# Register the restaurant table router
app.include_router(restaurant_table.router, prefix="/tables", tags=["Restaurant Tables"])

# Register the seating assignment router
app.include_router(seating_assignment.router, prefix="/seating-assignments", tags=["Seating Assignments"])

# Register the promotion router
app.include_router(promotion.router, prefix="/promotions", tags=["Promotions"])

# Register the menu item router
app.include_router(menu_item.router, prefix="/menu-items", tags=["Menu Items"])

# Register the bill router
app.include_router(bill.router, prefix="/bills", tags=["Bills"])

# Register the bill item router
app.include_router(bill_item.router, prefix="/bill-items", tags=["Bill Items"])

# Register the payment router
app.include_router(payment.router, prefix="/payments", tags=["Payments"])


# Basic root route
# This is just a simple test route to confirm the backend is running
@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Restaurant System API is running"}


# Database health check route
# This confirms that FastAPI can connect to the MySQL database
@app.get("/health/db")
def check_database() -> dict[str, str]:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"message": "Database connection successful"}