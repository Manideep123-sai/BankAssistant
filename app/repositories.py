from typing import List, Optional
import bcrypt

from .db import fetch_one, fetch_all, execute


# -------------------- Users --------------------

def create_user(full_name: str, email: str, phone: str, password: str) -> int:
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    query = """
        INSERT INTO users (full_name, email, phone, password_hash)
        VALUES (%s, %s, %s, %s)
    """
    return execute(query, (full_name, email, phone, password_hash))


def get_user_by_email(email: str) -> Optional[dict]:
    return fetch_one("SELECT * FROM users WHERE email = %s", (email,))


def verify_user(email: str, password: str) -> Optional[dict]:
    user = get_user_by_email(email)
    if not user:
        return None
    stored = user["password_hash"]
    # Try bcrypt first (for properly hashed passwords from signup)
    try:
        if stored.startswith("$2") and bcrypt.checkpw(password.encode(), stored.encode()):
            return user
    except (ValueError, TypeError):
        pass
    # Fallback: plaintext match (legacy sample data rows)
    if stored == password:
        return user
    return None


# -------------------- Accounts --------------------

def get_accounts_by_user(user_id: int) -> List[dict]:
    return fetch_all(
        """
        SELECT * FROM accounts
        WHERE user_id = %s AND status = 'ACTIVE'
        """,
        (user_id,),
    )


def get_account_by_number(account_number: str) -> Optional[dict]:
    return fetch_one(
        "SELECT * FROM accounts WHERE account_number = %s",
        (account_number,),
    )


def get_account_balance(account_number: str) -> Optional[float]:
    row = fetch_one(
        "SELECT balance FROM accounts WHERE account_number = %s",
        (account_number,),
    )
    return row["balance"] if row else None


# -------------------- Transactions --------------------

def get_recent_transactions(account_id: int, limit: int = 5) -> List[dict]:
    return fetch_all(
        """
        SELECT * FROM transactions
        WHERE from_account = %s OR to_account = %s
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (account_id, account_id, limit),
    )


def create_transfer_transaction(
    from_account_id: int,
    to_account_id: int,
    amount: float,
    status: str = "SUCCESS",
) -> int:
    # NOTE: This is a simple example without overdraft checks, etc.
    execute(
        "UPDATE accounts SET balance = balance - %s WHERE account_id = %s",
        (amount, from_account_id),
    )
    execute(
        "UPDATE accounts SET balance = balance + %s WHERE account_id = %s",
        (amount, to_account_id),
    )
    return execute(
        """
        INSERT INTO transactions (from_account, to_account, amount, transaction_type, status)
        VALUES (%s, %s, %s, 'TRANSFER', %s)
        """,
        (from_account_id, to_account_id, amount, status),
    )


# -------------------- Beneficiaries --------------------

def add_beneficiary(user_id: int, name: str, account: str, bank_name: str) -> int:
    return execute(
        """
        INSERT INTO beneficiaries (user_id, beneficiary_name, beneficiary_account, bank_name)
        VALUES (%s, %s, %s, %s)
        """,
        (user_id, name, account, bank_name),
    )


def get_beneficiaries(user_id: int) -> List[dict]:
    return fetch_all(
        "SELECT * FROM beneficiaries WHERE user_id = %s",
        (user_id,),
    )


def find_beneficiary_by_name(user_id: int, name: str) -> Optional[dict]:
    return fetch_one(
        """
        SELECT * FROM beneficiaries
        WHERE user_id = %s AND beneficiary_name LIKE %s
        """,
        (user_id, f"%{name}%"),
    )


# -------------------- Cards / Loans (for future agents) --------------------

def get_cards_by_user(user_id: int) -> List[dict]:
    return fetch_all("SELECT * FROM cards WHERE user_id = %s", (user_id,))


def get_loans_by_user(user_id: int) -> List[dict]:
    return fetch_all("SELECT * FROM loans WHERE user_id = %s", (user_id,))

