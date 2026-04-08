CREATE DATABASE IF NOT EXISTS bank_chatbot;
USE bank_chatbot;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Accounts Table
CREATE TABLE IF NOT EXISTS accounts (
    account_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    account_type ENUM('SAVINGS','CURRENT') NOT NULL,
    balance DECIMAL(15,2) DEFAULT 0.00,
    status ENUM('ACTIVE','FROZEN','CLOSED') DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 3. Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    from_account INT,
    to_account INT,
    amount DECIMAL(15,2) NOT NULL,
    transaction_type ENUM('TRANSFER','DEPOSIT','WITHDRAWAL') NOT NULL,
    status ENUM('PENDING','SUCCESS','FAILED') DEFAULT 'SUCCESS',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_account) REFERENCES accounts(account_id),
    FOREIGN KEY (to_account) REFERENCES accounts(account_id)
);

-- 4. Beneficiaries Table
CREATE TABLE IF NOT EXISTS beneficiaries (
    beneficiary_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    beneficiary_name VARCHAR(100) NOT NULL,
    beneficiary_account VARCHAR(20) NOT NULL,
    bank_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 5. Cards Table
CREATE TABLE IF NOT EXISTS cards (
    card_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    account_id INT NOT NULL,
    card_number VARCHAR(20) UNIQUE NOT NULL,
    card_type ENUM('DEBIT','CREDIT') NOT NULL,
    status ENUM('ACTIVE','BLOCKED') DEFAULT 'ACTIVE',
    expiry_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
);

-- 6. Loans Table
CREATE TABLE IF NOT EXISTS loans (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    loan_type ENUM('HOME','PERSONAL','CAR') NOT NULL,
    principal_amount DECIMAL(15,2) NOT NULL,
    interest_rate DECIMAL(5,2) NOT NULL,
    tenure_months INT NOT NULL,
    emi_amount DECIMAL(15,2),
    remaining_balance DECIMAL(15,2),
    status ENUM('ACTIVE','CLOSED') DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ======================
-- INSERT SAMPLE DATA
-- ======================

-- Users
INSERT INTO users (full_name, email, phone, password_hash) VALUES
('Rahul Sharma', 'rahul@example.com', '9876543210', 'hashed_pw_1'),
('Anita Verma', 'anita@example.com', '9876543211', 'hashed_pw_2'),
('Vikram Rao', 'vikram@example.com', '9876543212', 'hashed_pw_3');

-- Accounts
INSERT INTO accounts (user_id, account_number, account_type, balance) VALUES
(1, 'ACC10001', 'SAVINGS', 75000.00),
(1, 'ACC10002', 'CURRENT', 150000.00),
(2, 'ACC20001', 'SAVINGS', 50000.00),
(3, 'ACC30001', 'SAVINGS', 120000.00);

-- Transactions
INSERT INTO transactions (from_account, to_account, amount, transaction_type, status) VALUES
(1, 3, 5000.00, 'TRANSFER', 'SUCCESS'),
(3, 2, 10000.00, 'TRANSFER', 'SUCCESS'),
(NULL, 1, 20000.00, 'DEPOSIT', 'SUCCESS'),
(2, NULL, 5000.00, 'WITHDRAWAL', 'SUCCESS');

-- Beneficiaries
INSERT INTO beneficiaries (user_id, beneficiary_name, beneficiary_account, bank_name) VALUES
(1, 'Anita Verma', 'ACC20001', 'HDFC Bank'),
(1, 'Vikram Rao', 'ACC30001', 'ICICI Bank'),
(2, 'Rahul Sharma', 'ACC10001', 'HDFC Bank');

-- Cards
INSERT INTO cards (user_id, account_id, card_number, card_type, status, expiry_date) VALUES
(1, 1, '4111111111111111', 'DEBIT', 'ACTIVE', '2028-12-31'),
(1, 2, '5500000000000004', 'CREDIT', 'ACTIVE', '2027-10-31'),
(2, 3, '4111111111111122', 'DEBIT', 'BLOCKED', '2026-08-31'),
(3, 4, '4111111111111133', 'DEBIT', 'ACTIVE', '2029-01-31');

-- Loans
INSERT INTO loans (user_id, loan_type, principal_amount, interest_rate, tenure_months, emi_amount, remaining_balance, status) VALUES
(1, 'HOME', 2500000.00, 8.50, 240, 21700.00, 2100000.00, 'ACTIVE'),
(2, 'PERSONAL', 500000.00, 11.00, 60, 10850.00, 320000.00, 'ACTIVE'),
(3, 'CAR', 800000.00, 9.25, 84, 12900.00, 600000.00, 'ACTIVE');
