from typing import TypedDict, List, Optional

import sqlite3

from typing_extensions import Annotated

from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver

from .agents.main_assistant import Assistant_main
from .agents.account_agent import Assistant_account
from .agents.funds_transfer_agent import (
    Assistant_money_transfer,
    money_transfer_assistant_tools,
)
from .agents.location_agent import Assistant_location


# ---------------------- State ----------------------

class State(TypedDict):
    """
    Conversation state:
    - `messages`: dialog history managed via `add_messages`.
    - `user_id`: authenticated user's internal id (0 = guest).
    - `bank_name`: selected Indian bank for contextual responses.
    """

    messages: Annotated[list[BaseMessage], add_messages]
    user_id: int
    bank_name: str
    language: str


def _last_human_text(state: State) -> str:
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            return str(msg.content).lower()
    return ""


def main_router(state: State) -> str:
    """
    Simple keyword-based router that decides which specialist agent to call
    based on the latest human message.
    """
    text = _last_human_text(state)

    if any(word in text for word in [
        "transfer", "send", "pay", "beneficiary",
        "neft", "rtgs", "imps", "upi",
    ]):
        return "to_money_transfer_assistant"

    if any(word in text for word in [
        "near", "nearby", "nearest", "location", "address", "where is", "closest",
        "find atm", "find branch", "locate",
    ]):
        return "to_location_assistant"

    if any(word in text for word in [
        "balance", "transaction", "mini statement", "statement",
        "interest", "account type", "emi", "loan", "fd", "rd",
        "fixed deposit", "recurring deposit", "maturity",
        "credit card", "debit card", "card", "cheque", "check bounce",
        "charges", "fee", "penalty", "minimum balance",
    ]):
        return "to_account_assistant"

    # No clear banking intent – keep the conversation with main assistant only.
    return "terminate"


# ---------------------- Graph construction ----------------------

builder = StateGraph(State)

builder.add_node("main_assistant", Assistant_main)
builder.add_node("account_assistant", Assistant_account)
builder.add_node("money_transfer_assistant", Assistant_money_transfer)
builder.add_node("location_assistant", Assistant_location)

builder.add_edge(START, "main_assistant")

builder.add_conditional_edges(
    "main_assistant",
    main_router,
    {
        "to_account_assistant": "account_assistant",
        "to_money_transfer_assistant": "money_transfer_assistant",
        "to_location_assistant": "location_assistant",
        "terminate": END,
    },
)

builder.add_edge("account_assistant", END)
builder.add_edge("money_transfer_assistant", END)
builder.add_edge("location_assistant", END)

# Persistent memory with SQLite checkpointer (per session/thread)
conn = sqlite3.connect("persistent_memory.sqlite", check_same_thread=False)
checkpointer = SqliteSaver(conn)

graph = builder.compile(checkpointer=checkpointer)


# ---------------------- Helper for Streamlit / FastAPI ----------------------

def run_graph(
    user_id: int,
    user_message: str,
    thread_id: Optional[str] = None,
    bank_name: str = "State Bank of India",
    language: str = "English",
):
    """
    Entry point used by the Streamlit app and FastAPI server.

    - Builds a State with accumulated messages (handled via checkpointer).
    - Uses `thread_id` for persistent memory across turns.
    - Passes `bank_name` so agents can contextualise responses.
    - Returns the last assistant message as a plain string.
    """
    config = {"configurable": {"thread_id": thread_id or str(user_id)}}

    state = {
        "messages": [HumanMessage(content=user_message)],
        "user_id": user_id,
        "bank_name": bank_name,
        "language": language,
    }
    new_state = graph.invoke(state, config)

    reply_msg = new_state["messages"][-1]
    if isinstance(reply_msg, (AIMessage, HumanMessage)):
        reply_text = reply_msg.content
    else:
        reply_text = getattr(reply_msg, "content", str(reply_msg))

    return {"reply": reply_text, "thread_id": config["configurable"]["thread_id"]}
