from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from . import repositories
from .auth import authenticate_user, create_access_token, get_current_user
from .schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    ChatRequest,
    ChatResponse,
)
from .graph import run_graph


app = FastAPI(title="Bank Chatbot with LangGraph")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Auth endpoints ----------


@app.post("/auth/register", response_model=TokenResponse)
def register(req: RegisterRequest):
    # Simple uniqueness handling (real app: better error handling)
    user_id = repositories.create_user(
        full_name=req.full_name,
        email=req.email,
        phone=req.phone,
        password=req.password,
    )
    token = create_access_token(user_id=user_id, email=req.email)
    return TokenResponse(access_token=token)


@app.post("/auth/login", response_model=TokenResponse)
def login(req: LoginRequest):
    user = authenticate_user(req.email, req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    token = create_access_token(user_id=user["user_id"], email=user["email"])
    return TokenResponse(access_token=token)


# ---------- Chat endpoint (requires auth) ----------


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    result = run_graph(user_id=user_id, user_message=req.message, thread_id=req.thread_id)
    return ChatResponse(reply=result["reply"], thread_id=result["thread_id"])


@app.get("/health")
def health_check():
    return {"status": "ok"}

