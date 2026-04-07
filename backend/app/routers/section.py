from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.section import Section
from app.schemas.section import SectionCreate, SectionUpdate, SectionResponse

# Create a router object to group all section-related endpoints together
router = APIRouter()


# POST /sections/
# Creates a new section
@router.post("/", response_model=SectionResponse)
def create_section(
    section: SectionCreate,
    db: Session = Depends(get_db)
) -> Section:
    # Check if a section with this name already exists
    existing_section = (
        db.query(Section)
        .filter(Section.sectionName == section.sectionName)
        .first()
    )

    # If the section already exists, stop and return an error
    if existing_section is not None:
        raise HTTPException(
            status_code=400,
            detail="Section already exists"
        )

    # Create a new Section object from the validated request data
    new_section = Section(
        sectionName=section.sectionName,
        employeeID=section.employeeID
    )

    # Add the new section to the database session
    db.add(new_section)

    # Save the new section row to the database
    db.commit()

    # Refresh the object so it reflects the current database state
    db.refresh(new_section)

    # Return the created section
    return new_section


# GET /sections/{section_name}
# Retrieves a section by section name
@router.get("/{section_name}", response_model=SectionResponse)
def get_section(
    section_name: str,
    db: Session = Depends(get_db)
) -> Section:
    # Look up the section by its primary key
    section = (
        db.query(Section)
        .filter(Section.sectionName == section_name)
        .first()
    )

    # If the section does not exist, return an HTTP 404 error
    if section is None:
        raise HTTPException(
            status_code=404,
            detail="Section not found"
        )

    # Return the section if found
    return section


# PUT /sections/{section_name}
# Updates the employee assigned to a section
@router.put("/{section_name}", response_model=SectionResponse)
def update_section(
    section_name: str,
    update: SectionUpdate,
    db: Session = Depends(get_db)
) -> Section:
    # Find the section by name
    section = (
        db.query(Section)
        .filter(Section.sectionName == section_name)
        .first()
    )

    # If the section does not exist, return an HTTP 404 error
    if section is None:
        raise HTTPException(
            status_code=404,
            detail="Section not found"
        )

    # Update the assigned employee ID
    section.employeeID = update.employeeID

    # Save the updated section
    db.commit()

    # Refresh the object so it reflects the latest database state
    db.refresh(section)

    # Return the updated section
    return section


# DELETE /sections/{section_name}
# Deletes a section by name
@router.delete("/{section_name}")
def delete_section(
    section_name: str,
    db: Session = Depends(get_db)
) -> dict[str, str]:
    # Find the section by name
    section = (
        db.query(Section)
        .filter(Section.sectionName == section_name)
        .first()
    )

    # If the section does not exist, return an HTTP 404 error
    if section is None:
        raise HTTPException(
            status_code=404,
            detail="Section not found"
        )

    # Delete the section
    db.delete(section)

    # Commit the delete operation
    db.commit()

    # Return a simple success message
    return {"message": "Section successfully deleted"}