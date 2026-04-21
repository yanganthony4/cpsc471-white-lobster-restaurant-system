-- Temporarily disable foreign key checks so we can cleanly drop tables
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================
-- DROP TABLES (dependency order)
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

CREATE TABLE STAFF_USER (
    employeeID   INT          NOT NULL AUTO_INCREMENT,
    role         VARCHAR(50)  NOT NULL,
    name         VARCHAR(100) NOT NULL,
    username     VARCHAR(50)  NOT NULL,
    passwordHash VARCHAR(255) NOT NULL,

    PRIMARY KEY (employeeID),
    UNIQUE  (username),
    CHECK (role IN ('Host', 'Server', 'Manager', 'Cashier'))
);

CREATE TABLE LOYALTY_PROGRAM (
    Loyalty_id    INT NOT NULL AUTO_INCREMENT,
    email         VARCHAR(255) NOT NULL,
    pointsBalance INT NOT NULL DEFAULT 0,

    PRIMARY KEY (Loyalty_id),
    UNIQUE  (email),
    CHECK (pointsBalance >= 0)
);

CREATE TABLE CUSTOMER_ACCOUNT (
    email        VARCHAR(255) NOT NULL,
    phoneNumber  VARCHAR(50),
    name         VARCHAR(100) NOT NULL,
    username     VARCHAR(50)  NOT NULL,
    passwordHash VARCHAR(255) NOT NULL,

    PRIMARY KEY (email),
    UNIQUE (username)
);

CREATE TABLE SECTION (
    sectionName VARCHAR(100) NOT NULL,
    employeeID  INT,

    PRIMARY KEY (sectionName),
    FOREIGN KEY (employeeID) REFERENCES STAFF_USER(employeeID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

CREATE TABLE RESTAURANT_TABLE (
    tableNumber        INT          NOT NULL,
    sectionName        VARCHAR(100) NOT NULL,
    availabilityStatus VARCHAR(50)  NOT NULL DEFAULT 'Available',
    capacity           INT          NOT NULL,

    PRIMARY KEY (tableNumber, sectionName),
    FOREIGN KEY (sectionName) REFERENCES SECTION(sectionName)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CHECK (capacity > 0),
    CHECK (availabilityStatus IN ('Available', 'Occupied', 'Reserved', 'Out of Service'))
);

CREATE TABLE WAITLIST_ENTRY (
    waitlistID        INT          NOT NULL AUTO_INCREMENT,
    email             VARCHAR(255) NOT NULL,
    specialRequests   VARCHAR(255),
    joinTime          TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    entryStatus       VARCHAR(50)  NOT NULL DEFAULT 'Waiting',
    partySize         INT          NOT NULL,
    estimatedWaitTime INT                   DEFAULT 10,

    PRIMARY KEY (waitlistID),
    FOREIGN KEY (email) REFERENCES CUSTOMER_ACCOUNT(email)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CHECK (partySize > 0),
    CHECK (estimatedWaitTime >= 0),
    CHECK (entryStatus IN ('Waiting', 'Seated', 'Cancelled', 'Removed'))
);

CREATE TABLE RESERVATION (
    reservationID      INT          NOT NULL AUTO_INCREMENT,
    email              VARCHAR(255) NOT NULL,
    specialRequests    VARCHAR(255),
    partySize          INT          NOT NULL,
    reservationDateTime DATETIME   NOT NULL,

    PRIMARY KEY (reservationID),
    FOREIGN KEY (email) REFERENCES CUSTOMER_ACCOUNT(email)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CHECK (partySize > 0)
);

CREATE TABLE SEATING_ASSIGNMENT (
    assignmentID  INT          NOT NULL AUTO_INCREMENT,
    reservationID INT,
    waitlistID    INT,
    sectionName   VARCHAR(100) NOT NULL,
    tableNumber   INT          NOT NULL,
    employeeID    INT          NOT NULL,
    currentStatus VARCHAR(50)  NOT NULL DEFAULT 'Seated',
    startTime     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (assignmentID),
    UNIQUE (reservationID),
    UNIQUE (waitlistID),

    -- Removed BOTH "ON DELETE SET NULL" and "ON UPDATE CASCADE" 
    FOREIGN KEY (reservationID) REFERENCES RESERVATION(reservationID),
    FOREIGN KEY (waitlistID) REFERENCES WAITLIST_ENTRY(waitlistID),
        
    FOREIGN KEY (sectionName) REFERENCES SECTION(sectionName)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (employeeID)  REFERENCES STAFF_USER(employeeID)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (tableNumber, sectionName) REFERENCES RESTAURANT_TABLE(tableNumber, sectionName)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CHECK (currentStatus IN ('Seated', 'Completed', 'Cancelled')),
    CHECK (
        (reservationID IS NOT NULL AND waitlistID IS NULL)
        OR
        (reservationID IS NULL AND waitlistID IS NOT NULL)
    )
);

CREATE TABLE PROMOTION (
    promoID          INT            NOT NULL AUTO_INCREMENT,
    startDate        DATE           NOT NULL,
    endDate          DATE           NOT NULL,
    discountAmount   DECIMAL(10, 2) NOT NULL,
    eligibilityRules VARCHAR(255),

    PRIMARY KEY (promoID),
    CHECK (discountAmount >= 0),
    CHECK (endDate >= startDate)
);

CREATE TABLE MENU_ITEM (
    menuItemID   INT            NOT NULL AUTO_INCREMENT,
    description  VARCHAR(255),
    currentPrice DECIMAL(10, 2) NOT NULL,
    name         VARCHAR(100)   NOT NULL,

    PRIMARY KEY (menuItemID),
    CHECK (currentPrice >= 0)
);

CREATE TABLE BILL (
    invoiceID    INT            NOT NULL AUTO_INCREMENT,
    promoID      INT,
    assignmentID INT            NOT NULL,
    totalAmount  DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    taxesAndFees DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    isSettled    BOOLEAN        NOT NULL DEFAULT FALSE,

    PRIMARY KEY (invoiceID),
    UNIQUE (assignmentID),
    FOREIGN KEY (promoID)      REFERENCES PROMOTION(promoID)
        ON DELETE SET NULL  ON UPDATE CASCADE,
    FOREIGN KEY (assignmentID) REFERENCES SEATING_ASSIGNMENT(assignmentID)
        ON DELETE RESTRICT  ON UPDATE CASCADE,
    CHECK (totalAmount  >= 0),
    CHECK (taxesAndFees >= 0)
);

CREATE TABLE BILL_ITEM (
    invoiceID    INT            NOT NULL,
    menuItemID   INT            NOT NULL,
    quantity     INT            NOT NULL DEFAULT 1,
    priceAtOrder DECIMAL(10, 2) NOT NULL,

    PRIMARY KEY (invoiceID, menuItemID),
    FOREIGN KEY (invoiceID)  REFERENCES BILL(invoiceID)
        ON DELETE CASCADE   ON UPDATE CASCADE,
    FOREIGN KEY (menuItemID) REFERENCES MENU_ITEM(menuItemID)
        ON DELETE RESTRICT  ON UPDATE CASCADE,
    CHECK (quantity     > 0),
    CHECK (priceAtOrder >= 0)
);

CREATE TABLE PAYMENT (
    paymentID     INT            NOT NULL AUTO_INCREMENT,
    invoiceID     INT            NOT NULL,
    paymentMethod VARCHAR(50)    NOT NULL,
    timeStamp     TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    amount        DECIMAL(10, 2) NOT NULL,

    PRIMARY KEY (paymentID),
    FOREIGN KEY (invoiceID) REFERENCES BILL(invoiceID)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CHECK (amount > 0),
    CHECK (paymentMethod IN ('Cash', 'Debit', 'Credit', 'Gift Card', 'Online'))
);

-- ============================================
-- Deferred FK
-- ============================================
ALTER TABLE LOYALTY_PROGRAM
    ADD CONSTRAINT fk_loyalty_customer
    FOREIGN KEY (email) REFERENCES CUSTOMER_ACCOUNT(email)
    ON DELETE CASCADE ON UPDATE CASCADE;

-- ============================================
-- Re-enable foreign key checks
-- ============================================
SET FOREIGN_KEY_CHECKS = 1;