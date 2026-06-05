-- use host_management;

-- -- =====================================================
-- -- REFERENCE STUBS (owned by other teams)
-- -- =====================================================

-- CREATE TABLE students (
--     student_id    INT AUTO_INCREMENT PRIMARY KEY,
--     admission_no  VARCHAR(30) UNIQUE,
--     first_name    VARCHAR(100),
--     last_name     VARCHAR(100),
--     gender        ENUM('Male','Female','Other'),
--     dob           DATE,
--     mobile        VARCHAR(15),
--     email         VARCHAR(150),
--     academic_year VARCHAR(20),
--     status        ENUM('Active','Inactive') DEFAULT 'Active',
--     created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- CREATE TABLE users (
--     user_id       INT AUTO_INCREMENT PRIMARY KEY,
--     username      VARCHAR(100) UNIQUE,
--     email         VARCHAR(150) UNIQUE,
--     password_hash VARCHAR(255),
--     first_name    VARCHAR(100),
--     last_name     VARCHAR(100),
--     mobile        VARCHAR(15),
--     status        ENUM('Active','Inactive','Blocked') DEFAULT 'Active',
--     created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- -- =====================================================
-- -- HOSTELS
-- -- =====================================================

-- CREATE TABLE hostels (
--     hostel_id   INT AUTO_INCREMENT PRIMARY KEY,
--     hostel_code VARCHAR(20) UNIQUE NOT NULL,
--     hostel_name VARCHAR(100) NOT NULL,
--     address     TEXT,
--     status      ENUM('Active','Inactive') DEFAULT 'Active'
-- );

-- -- =====================================================
-- -- BLOCKS
-- -- =====================================================

-- CREATE TABLE blocks (
--     block_id   INT AUTO_INCREMENT PRIMARY KEY,
--     hostel_id  INT NOT NULL,
--     block_name VARCHAR(100) NOT NULL,
--     FOREIGN KEY (hostel_id) REFERENCES hostels(hostel_id)
-- );

-- -- =====================================================
-- -- FLOORS
-- -- =====================================================

-- CREATE TABLE floors (
--     floor_id INT AUTO_INCREMENT PRIMARY KEY,
--     block_id INT NOT NULL,
--     floor_no INT NOT NULL,
--     FOREIGN KEY (block_id) REFERENCES blocks(block_id)
-- );

-- -- =====================================================
-- -- ROOMS (implied by room_id FK in room_allocations)
-- -- =====================================================

-- CREATE TABLE rooms (
--     room_id   INT AUTO_INCREMENT PRIMARY KEY,
--     floor_id  INT NOT NULL,
--     room_no   VARCHAR(20) NOT NULL,
--     room_type ENUM('Single','Double','Triple') NOT NULL,
--     capacity  INT NOT NULL,
--     status    ENUM('Available','Occupied','Maintenance') DEFAULT 'Available',
--     FOREIGN KEY (floor_id) REFERENCES floors(floor_id)
-- );

-- -- =====================================================
-- -- ROOM ALLOCATIONS
-- -- =====================================================

-- CREATE TABLE room_allocations (
--     allocation_id   INT AUTO_INCREMENT PRIMARY KEY,
--     room_id         INT NOT NULL,
--     student_id      INT NOT NULL,
--     bed_number      VARCHAR(10),
--     allocation_date DATE NOT NULL,
--     checkout_date   DATE,
--     status          ENUM('Active','Vacated','Transferred') DEFAULT 'Active',
--     FOREIGN KEY (room_id)    REFERENCES rooms(room_id),
--     FOREIGN KEY (student_id) REFERENCES students(student_id)
-- );

-- -- =====================================================
-- -- FEE PAYMENTS (part of hostel module per ERD)
-- -- =====================================================

-- CREATE TABLE fee_payments (
--     payment_id     INT AUTO_INCREMENT PRIMARY KEY,
--     allocation_id  INT NOT NULL,
--     amount         DECIMAL(10,2) NOT NULL,
--     payment_date   DATE NOT NULL,
--     payment_mode   VARCHAR(50),
--     receipt_no     VARCHAR(50),
--     payment_status ENUM('Pending','Paid','Failed') DEFAULT 'Pending',
--     FOREIGN KEY (allocation_id) REFERENCES room_allocations(allocation_id)
-- );

-- -- =====================================================
-- -- VISITORS
-- -- =====================================================

-- CREATE TABLE visitors (
--     visitor_id   INT AUTO_INCREMENT PRIMARY KEY,
--     student_id   INT NOT NULL,
--     visitor_name VARCHAR(100) NOT NULL,
--     relationship VARCHAR(50),
--     mobile       VARCHAR(15),
--     checkin      DATETIME NOT NULL,
--     checkout     DATETIME,
--     FOREIGN KEY (student_id) REFERENCES students(student_id)
-- );

-- -- =====================================================
-- -- COMPLAINTS
-- -- =====================================================

-- CREATE TABLE complaints (
--     complaint_id   INT AUTO_INCREMENT PRIMARY KEY,
--     student_id     INT NOT NULL,
--     room_id        INT NOT NULL,
--     complaint_type VARCHAR(50),
--     description    TEXT,
--     complaint_date DATETIME DEFAULT CURRENT_TIMESTAMP,
--     status         ENUM('Pending','In Progress','Resolved') DEFAULT 'Pending',
--     FOREIGN KEY (student_id) REFERENCES students(student_id),
--     FOREIGN KEY (room_id)    REFERENCES rooms(room_id)
-- );

-- -- =====================================================
-- -- MAINTENANCE REQUESTS
-- -- =====================================================

-- CREATE TABLE maintenance_requests (
--     request_id   INT AUTO_INCREMENT PRIMARY KEY,
--     room_id      INT NOT NULL,
--     requested_by INT NOT NULL,
--     request_date DATETIME DEFAULT CURRENT_TIMESTAMP,
--     description  TEXT,
--     status       ENUM('Open','Assigned','In Progress','Completed') DEFAULT 'Open',
--     resolved_on  DATETIME NULL,
--     FOREIGN KEY (room_id)      REFERENCES rooms(room_id),
--     FOREIGN KEY (requested_by) REFERENCES users(user_id)
-- );

-- -- =====================================================
-- -- ROOM TRANSFERS (from module list in PDF page 3)
-- -- =====================================================

-- CREATE TABLE room_transfers (
--     transfer_id   INT AUTO_INCREMENT PRIMARY KEY,
--     student_id    INT NOT NULL,
--     old_room_id   INT NOT NULL,
--     new_room_id   INT NOT NULL,
--     transfer_date DATE NOT NULL,
--     reason        TEXT,
--     FOREIGN KEY (student_id)  REFERENCES students(student_id),
--     FOREIGN KEY (old_room_id) REFERENCES rooms(room_id),
--     FOREIGN KEY (new_room_id) REFERENCES rooms(room_id)
-- );

-- -- =====================================================
-- -- DUMMY DATA
-- -- =====================================================

-- INSERT INTO students (admission_no, first_name, last_name, gender, dob, mobile, email, academic_year, status)
-- VALUES
-- ('CE24001', 'Rahul',  'Bansode',  'Male',   '2005-03-12', '9876543210', 'rahul@college.edu',  'Second Year', 'Active'),
-- ('CE24002', 'Priya',  'Patil',    'Female', '2005-07-20', '9876543211', 'priya@college.edu',  'Second Year', 'Active'),
-- ('ME24001', 'Arjun',  'Sharma',   'Male',   '2006-01-15', '9876543212', 'arjun@college.edu',  'First Year',  'Active'),
-- ('IT24001', 'Neha',   'Kulkarni', 'Female', '2005-11-08', '9876543213', 'neha@college.edu',   'Second Year', 'Active');

-- INSERT INTO users (username, email, password_hash, first_name, last_name, mobile, status)
-- VALUES
-- ('warden01', 'warden@college.edu', 'hashed_password', 'Suresh', 'Warden', '9000000001', 'Active');

-- INSERT INTO hostels (hostel_code, hostel_name, address, status)
-- VALUES
-- ('BH01', 'Boys Hostel',  'Main Campus', 'Active'),
-- ('GH01', 'Girls Hostel', 'East Campus', 'Active');

-- INSERT INTO blocks (hostel_id, block_name)
-- VALUES
-- (1, 'Block A'),
-- (1, 'Block B'),
-- (2, 'Block G');

-- INSERT INTO floors (block_id, floor_no)
-- VALUES
-- (1, 1),
-- (1, 2),
-- (2, 1),
-- (3, 1);

-- INSERT INTO rooms (floor_id, room_no, room_type, capacity, status)
-- VALUES
-- (1, 'A101', 'Double', 2, 'Occupied'),
-- (1, 'A102', 'Double', 2, 'Available'),
-- (2, 'A201', 'Triple', 3, 'Occupied'),
-- (4, 'G101', 'Double', 2, 'Available'),
-- (4, 'G102', 'Single', 1, 'Maintenance');

-- INSERT INTO room_allocations (room_id, student_id, bed_number, allocation_date, checkout_date, status)
-- VALUES
-- (1, 1, 'B1', '2026-06-01', NULL, 'Active'),
-- (1, 2, 'B2', '2026-06-01', NULL, 'Active'),
-- (3, 3, 'B1', '2026-06-01', NULL, 'Active'),
-- (4, 4, 'B1', '2026-06-01', NULL, 'Active');

-- INSERT INTO fee_payments (allocation_id, amount, payment_date, payment_mode, receipt_no, payment_status)
-- VALUES
-- (1, 15000.00, '2026-06-01', 'Online',  'RCPT001', 'Paid'),
-- (2, 15000.00, '2026-06-01', 'Online',  'RCPT002', 'Paid'),
-- (3, 12000.00, '2026-06-01', 'Cash',    'RCPT003', 'Paid'),
-- (4, 15000.00, '2026-06-02', 'Cheque',  'RCPT004', 'Pending');

-- INSERT INTO room_transfers (student_id, old_room_id, new_room_id, transfer_date, reason)
-- VALUES
-- (3, 3, 2, '2026-06-10', 'Requested room change');

-- INSERT INTO visitors (student_id, visitor_name, relationship, mobile, checkin, checkout)
-- VALUES
-- (1, 'Ramesh Bansode', 'Father', '9999999999', '2026-06-05 10:00:00', '2026-06-05 12:00:00'),
-- (2, 'Sunita Patil',   'Mother', '9999999998', '2026-06-06 11:00:00', '2026-06-06 13:00:00');

-- INSERT INTO complaints (student_id, room_id, complaint_type, description, status)
-- VALUES
-- (1, 1, 'Bathroom',   'Wash basin leakage',         'Pending'),
-- (2, 1, 'Electrical', 'Tubelight not working',       'In Progress'),
-- (3, 3, 'Cleaning',   'Room requires deep cleaning', 'Resolved');

-- INSERT INTO maintenance_requests (room_id, requested_by, description, status, resolved_on)
-- VALUES
-- (1, 1, 'Fix wash basin leakage',  'Assigned',    NULL),
-- (1, 1, 'Replace tubelight',       'In Progress', NULL),
-- (3, 1, 'Deep cleaning completed', 'Completed',   '2026-06-08 14:00:00');

-- -- =====================================================
-- -- VERIFICATION
-- -- =====================================================

-- SHOW TABLES;
-- SELECT * FROM hostels;
-- SELECT * FROM blocks;
-- SELECT * FROM floors;
-- SELECT * FROM rooms;
-- SELECT * FROM students;
-- SELECT * FROM room_allocations;
-- SELECT * FROM fee_payments;
-- SELECT * FROM room_transfers;
-- SELECT * FROM visitors;
-- SELECT * FROM complaints;
-- SELECT * FROM maintenance_requests;
USE host_management;

-- =====================================================
-- NEW TABLE: GATE PASSES (Module 2)
-- =====================================================

CREATE TABLE gate_passes (
    pass_id           INT AUTO_INCREMENT PRIMARY KEY,
    student_id        INT NOT NULL,
    room_no           VARCHAR(20),
    destination       VARCHAR(200),
    purpose           TEXT,
    out_date          DATE NOT NULL,
    out_time          TIME NOT NULL,
    return_date       DATE NOT NULL,
    return_time       TIME NOT NULL,
    emergency_contact VARCHAR(15),
    status            ENUM('Pending','Approved','Rejected','Returned') DEFAULT 'Pending',
    approved_by       INT,
    approved_at       DATETIME,
    pdf_path          VARCHAR(255),
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id)  REFERENCES students(student_id),
    FOREIGN KEY (approved_by) REFERENCES users(user_id)
);

-- =====================================================
-- ALTER EXISTING TABLE: VISITORS (Module 3)
-- Adding missing columns for visitor pass workflow
-- =====================================================

ALTER TABLE visitors
ADD COLUMN purpose     VARCHAR(200),
ADD COLUMN status      ENUM('Pending','Approved','Rejected') DEFAULT 'Pending',
ADD COLUMN approved_by INT,
ADD COLUMN approved_at DATETIME,
ADD COLUMN pdf_path    VARCHAR(255);

-- =====================================================
-- VERIFICATION
-- =====================================================

DESCRIBE gate_passes;
DESCRIBE visitors;