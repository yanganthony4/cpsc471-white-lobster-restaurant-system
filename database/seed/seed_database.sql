-- ============================================
-- SEED DATA
-- ============================================

INSERT INTO CUSTOMER_ACCOUNT (
    email,
    phoneNumber,
    name,
    username,
    password
) VALUES (
    'jane.customer@example.com',
    '403-555-1111',
    'Jane Customer',
    'janecustomer',
    'Customer123!'
);

INSERT INTO LOYALTY_PROGRAM (
    Loyalty_id,
    email,
    pointsBalance
) VALUES (
    1,
    'jane.customer@example.com',
    100
);

INSERT INTO STAFF_USER (
    employeeID,
    role,
    name,
    username,
    password
) VALUES (
    101,
    'Host',
    'Michael Staff',
    'mstaff',
    'Staff123!'
);

INSERT INTO SECTION (sectionName, employeeID) VALUES
('Main Dining', 101),
('Patio', 102),
('Bar', 103);

INSERT INTO RESTAURANT_TABLE (tableNumber, sectionName, availabilityStatus, capacity) VALUES
(1, 'Main Dining', 'Available', 2),
(2, 'Main Dining', 'Reserved', 4),
(3, 'Patio', 'Occupied', 4),
(4, 'Bar', 'Available', 2);

INSERT INTO WAITLIST_ENTRY (waitlistID, email, specialRequests, joinTime, entryStatus, partySize, estimatedWaitTime) VALUES
(201, 'carla@example.com', 'Window seat if possible', '2026-03-28 18:05:00', 'Waiting', 2, 20),
(202, 'bob@example.com', NULL, '2026-03-28 18:10:00', 'Waiting', 4, 35);

INSERT INTO RESERVATION (reservationID, email, specialRequests, partySize, reservationTime, scheduledDateTime) VALUES
(301, 'alice@example.com', 'Birthday dinner', 2, '18:30:00', '2026-03-28 18:30:00'),
(302, 'bob@example.com', NULL, 4, '19:00:00', '2026-03-28 19:00:00');

INSERT INTO SEATING_ASSIGNMENT (assignmentID, reservationID, waitlistID, sectionName, tableNumber, employeeID, currentStatus, startTime) VALUES
(401, 301, NULL, 'Main Dining', 2, 101, 'Seated', '2026-03-28 18:25:00'),
(402, NULL, 201, 'Bar', 4, 102, 'Seated', '2026-03-28 18:20:00');

INSERT INTO PROMOTION (promoID, startDate, endDate, discountAmount, eligibilityRules) VALUES
(501, '2026-03-01', '2026-03-31', 5.00, 'Applies to bills over $30'),
(502, '2026-03-15', '2026-04-15', 10.00, 'Loyalty members only');

INSERT INTO MENU_ITEM (menuItemID, description, currentPrice, name) VALUES
(601, 'Classic cheeseburger with fries', 14.99, 'Cheeseburger Combo'),
(602, 'Caesar salad with grilled chicken', 12.50, 'Chicken Caesar Salad'),
(603, 'Fresh lemonade', 3.99, 'Lemonade'),
(604, 'Chocolate lava cake', 6.50, 'Lava Cake');

INSERT INTO BILL (invoiceID, promoID, assignmentID, totalAmount, taxesAndFees, isSettled) VALUES
(701, 501, 401, 28.48, 1.42, FALSE),
(702, NULL, 402, 18.98, 0.95, TRUE);

INSERT INTO BILL_ITEM (invoiceID, menuItemID, quantity, priceAtOrder) VALUES
(701, 601, 1, 14.99),
(701, 603, 2, 3.99),
(702, 602, 1, 12.50),
(702, 604, 1, 6.50);

INSERT INTO PAYMENT (paymentID, invoiceID, paymentMethod, timeStamp, amount) VALUES
(801, 702, 'Credit', '2026-03-28 18:45:00', 19.93);