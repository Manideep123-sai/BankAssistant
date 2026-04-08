from langchain.tools import tool

from . import repositories


@tool
def authenticator(email: str, password: str) -> str:
    """
    Authenticate a banking user by email and password.
    Returns 'ok:<user_id>' or 'error'.
    """
    user = repositories.verify_user(email, password)
    if not user:
        return "error"
    return f"ok:{user['user_id']}"


@tool
def money_transferer(from_account: str, to_account: str, amount: float) -> str:
    """
    Transfer money between two accounts.
    Returns 'success', 'invalid_accounts', or 'insufficient_balance'.
    """
    src = repositories.get_account_by_number(from_account)
    dest = repositories.get_account_by_number(to_account)
    if not src or not dest:
        return "invalid_accounts"
    if float(src["balance"]) < amount:
        return "insufficient_balance"

    repositories.create_transfer_transaction(
        from_account_id=src["account_id"],
        to_account_id=dest["account_id"],
        amount=amount,
    )
    return "success"





