-- ============================================
-- DROP TABLES
-- ============================================

DROP TABLE IF EXISTS PAYMENT;
DROP TABLE IF EXISTS BILL_ITEM;
DROP TABLE IF EXISTS BILL;
DROP TABLE IF EXISTS SEATING_ASSIGNMENT;
DROP TABLE IF EXISTS RESERVATION;
DROP TABLE IF EXISTS WAITLIST_ENTRY;
DROP TABLE IF EXISTS MENU_ITEM;
DROP TABLE IF EXISTS PROMOTION;
DROP TABLE IF EXISTS RESTAURANT_TABLE;
DROP TABLE IF EXISTS SECTION;
DROP TABLE IF EXISTS CUSTOMER_ACCOUNT;
DROP TABLE IF EXISTS LOYALTY_PROGRAM;
DROP TABLE IF EXISTS STAFF_USER;


-- ============================================
-- CREATE TABLES
-- ============================================

CREATE TABLE CUSTOMER_ACCOUNT (
    email VARCHAR(255) NOT NULL,
    phoneNumber VARCHAR(50),
    name VARCHAR(100) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL, -- will store bcrypt hash

    PRIMARY KEY (email),
    UNIQUE (username)
);

CREATE TABLE LOYALTY_PROGRAM (
    Loyalty_id INT NOT NULL AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL,
    pointsBalance INT NOT NULL DEFAULT 0,

    PRIMARY KEY (Loyalty_id),
    UNIQUE (email),
    FOREIGN KEY (email) REFERENCES CUSTOMER_ACCOUNT(email),
    CHECK (pointsBalance >= 0)
);

CREATE TABLE STAFF_USER (
    employeeID INT NOT NULL AUTO_INCREMENT,
    role VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,

    PRIMARY KEY (employeeID),
    UNIQUE (username),
    CHECK (role IN ('Host', 'Server', 'Manager', 'Cashier'))
);


CREATE TABLE SECTION (
    sectionName VARCHAR(100) NOT NULL,
    employeeID INT,

    PRIMARY KEY (sectionName),
    FOREIGN KEY (employeeID) REFERENCES STAFF_USER(employeeID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);


CREATE TABLE RESTAURANT_TABLE (
    tableNumber INT NOT NULL,
    sectionName VARCHAR(100) NOT NULL,
    availabilityStatus VARCHAR(50) NOT NULL DEFAULT 'Available',
    capacity INT NOT NULL,

    PRIMARY KEY (tableNumber, sectionName),
    FOREIGN KEY (sectionName) REFERENCES SECTION(sectionName)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CHECK (capacity > 0),
    CHECK (availabilityStatus IN ('Available', 'Occupied', 'Reserved', 'Out of Service'))
);


CREATE TABLE WAITLIST_ENTRY (
    waitlistID INT NOT NULL AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL,
    specialRequests VARCHAR(255),
    joinTime TIME NOT NULL DEFAULT CURRENT_TIME,
    entryStatus VARCHAR(50) NOT NULL DEFAULT 'Waiting',
    partySize INT NOT NULL,
    estimatedWaitTime INT DEFAULT 10,

    PRIMARY KEY (waitlistID),
    FOREIGN KEY (customerID) REFERENCES CUSTOMER_ACCOUNT(customerID) -- fk
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CHECK (partySize > 0),
    CHECK (estimatedWaitTime >= 0),
    CHECK (entryStatus IN ('Waiting', 'Seated', 'Cancelled', 'Removed'))
);


CREATE TABLE RESERVATION (
    reservationID INT NOT NULL AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL,
    specialRequests VARCHAR(255),
    partySize INT NOT NULL,
    reservationDateTime TIMESTAMP NOT NULL,

    PRIMARY KEY (reservationID),
    FOREIGN KEY (customerID) REFERENCES CUSTOMER_ACCOUNT(customerID)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CHECK (partySize > 0),
    CHECK (status IN ('Pending', 'Confirmed', 'Seated', 'Cancelled', 'No-Show'))
);


CREATE TABLE SEATING_ASSIGNMENT (
    assignmentID INT NOT NULL AUTO_INCREMENT,
    reservationID INT,
    waitlistID INT,
    sectionName VARCHAR(100) NOT NULL,
    tableNumber INT NOT NULL,
    employeeID INT NOT NULL,
    currentStatus VARCHAR(50) NOT NULL DEFAULT 'Seated',
    startTime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (assignmentID),

    UNIQUE (reservationID),
    UNIQUE (waitlistID),

    FOREIGN KEY (reservationID) REFERENCES RESERVATION(reservationID),
    FOREIGN KEY (waitlistID) REFERENCES WAITLIST_ENTRY(waitlistID),
    FOREIGN KEY (sectionName) REFERENCES SECTION(sectionName),
    FOREIGN KEY (employeeID) REFERENCES STAFF_USER(employeeID),
    FOREIGN KEY (tableNumber, sectionName)
        REFERENCES RESTAURANT_TABLE(tableNumber, sectionName),

    CHECK (currentStatus IN ('Seated', 'Completed', 'Cancelled')),

    CHECK (
        (reservationID IS NOT NULL AND waitlistID IS NULL)
        OR
        (reservationID IS NULL AND waitlistID IS NOT NULL)
    )
);

CREATE TABLE PROMOTION (
    promoID INT NOT NULL AUTO_INCREMENT,
    startDate DATE NOT NULL,
    endDate DATE NOT NULL,
    discountAmount DECIMAL(10,2) NOT NULL,
    eligibilityRules VARCHAR(255),

    PRIMARY KEY (promoID),
    CHECK (discountAmount >= 0),
    CHECK (endDate >= startDate)
);


CREATE TABLE MENU_ITEM (
    menuItemID INT NOT NULL AUTO_INCREMENT,
    description VARCHAR(255),
    currentPrice DECIMAL(10,2) NOT NULL,
    name VARCHAR(100) NOT NULL,

    PRIMARY KEY (menuItemID),
    CHECK (currentPrice >= 0)
);


CREATE TABLE BILL (
    invoiceID INT NOT NULL AUTO_INCREMENT,
    promoID INT,
    assignmentID INT NOT NULL,
    totalAmount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    taxesAndFees DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    isSettled BOOLEAN NOT NULL DEFAULT FALSE,

    PRIMARY KEY (invoiceID),
    UNIQUE (assignmentID),

    FOREIGN KEY (promoID) REFERENCES PROMOTION(promoID)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    FOREIGN KEY (assignmentID) REFERENCES SEATING_ASSIGNMENT(assignmentID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CHECK (totalAmount >= 0),
    CHECK (taxesAndFees >= 0)
);


CREATE TABLE BILL_ITEM (
    invoiceID INT NOT NULL,
    menuItemID INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    priceAtOrder DECIMAL(10,2) NOT NULL,

    PRIMARY KEY (invoiceID, menuItemID),

    FOREIGN KEY (invoiceID) REFERENCES BILL(invoiceID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    FOREIGN KEY (menuItemID) REFERENCES MENU_ITEM(menuItemID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CHECK (quantity > 0),
    CHECK (priceAtOrder >= 0)
);


CREATE TABLE PAYMENT (
    paymentID INT NOT NULL AUTO_INCREMENT,
    invoiceID INT NOT NULL,
    paymentMethod VARCHAR(50) NOT NULL,
    timeStamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    amount DECIMAL(10,2) NOT NULL,
    idempotencyKey VARCHAR(255) UNIQUE NOT NULL, -- NEW: Prevents double charges

    PRIMARY KEY (paymentID),
    FOREIGN KEY (invoiceID) REFERENCES BILL(invoiceID)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ============================================
-- Indexes
-- ============================================

CREATE INDEX idx_reservation_date ON RESERVATION(scheduledDateTime, status);
CREATE INDEX idx_waitlist_time ON WAITLIST_ENTRY(joinTime, entryStatus);

DELIMITER //
CREATE TRIGGER chk_capacity_before_insert_seating
BEFORE INSERT ON SEATING_ASSIGNMENT
FOR EACH ROW
BEGIN
    DECLARE table_cap INT;
    DECLARE party_sz INT;

    -- Get capacity
    SELECT capacity INTO table_cap FROM RESTAURANT_TABLE 
    WHERE tableNumber = NEW.tableNumber AND sectionName = NEW.sectionName;

    -- Get party size based on intent
    IF NEW.reservationID IS NOT NULL THEN
        SELECT partySize INTO party_sz FROM RESERVATION WHERE reservationID = NEW.reservationID;
    ELSE
        SELECT partySize INTO party_sz FROM WAITLIST_ENTRY WHERE waitlistID = NEW.waitlistID;
    END IF;

    IF party_sz > table_cap THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Party size exceeds table capacity.';
    END IF;
END;
//
DELIMITER ;
