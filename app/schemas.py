from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


# ---------- Auth ----------


class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Chat ----------


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = Field(
        default=None,
        description="Conversation/thread id for persistent memory. Reuse to continue.",
    )


class ChatResponse(BaseModel):
    reply: str
    thread_id: str


# ---------- Account info ----------


class AccountSummary(BaseModel):
    account_number: str
    account_type: str
    balance: float


class TransactionRecord(BaseModel):
    transaction_id: int
    from_account: Optional[int]
    to_account: Optional[int]
    amount: float
    transaction_type: str
    status: str


# ---------- Transfers ----------


class TransferContext(BaseModel):
    from_account: Optional[str] = None
    to_account: Optional[str] = None
    beneficiary_name: Optional[str] = None
    amount: Optional[float] = None
    confirmed: bool = False

