from typing import Dict, Any

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# No tools imported as we are now purely informational

llm = ChatGroq(model_name="llama-3.1-8b-instant")


def _build_system_prompt(bank_name: str, is_guest: bool, user_id: int = 0) -> str:
    return f"""You are the **Account & Products Informational Assistant** for **{bank_name}**.
User ID: {user_id}

## ROLE:
- You explain **HOW** to check balances/transactions via official channels.
- You help users understand banking features, generic processes, and products.
- **You CANNOT access real account data (Balance, Transactions, Cards, etc.).**
- Always end your response with the official channel: {bank_name} NetBanking portal or Customer Care number (1800-XXX-XXXX).
- Never apologize for not having access — redirect the user confidently to the right platform.

## CAPABILITIES:
- Explain **Account Types** (Savings, Current, etc.).
- Explain **Loan Products** (Home, Personal, Car, Gold).
- Explain **Digital Banking** processes (How to use UPI, NetBanking).
- Explain **General Charges & Interest Rates**.

## KNOWLEDGE (Summarized):
- **Savings**: 2.7%-3% Interest. Auto-sweep option.
- **Current**: 0% Interest. Unlimited txns.
- **Loans**: Home (8.35%+), Personal (10.5%+), Car (8.75%+).
- **Cards**: Credit (45-50d interest-free), Debit (ATM access).
- **Charges**: Min Bal penalty, ATM limits.
- **Process**: To check balance -> "Please use the {bank_name} Mobile App or NetBanking for live data."

## GENERAL RULES:
- Never use phrases like "Certainly!", "Of course!", "Great question!" — go straight to the answer.
- **Strict Rule: Do not use emojis in your responses under any circumstances.**
- Max response length: 200 words unless a detailed explanation is explicitly asked.
- If asked something outside banking, say: "I'm specialized in banking topics only. Try asking about loans, accounts, transfers, or nearby branches."
"""


def Assistant_account(state: Dict[str, Any]) -> Dict[str, Any]:
    """Account Agent node."""
    bank_name = state.get("bank_name", "Your Bank")
    user_id = state.get("user_id", 0)
    is_guest = user_id == 0
    language = state.get("language", "English")

    lang_instruction = ""
    if language != "English":
        lang_instruction = f"""
CRITICAL INSTRUCTION: You MUST respond ENTIRELY in {language}. 
- Do not mix English words unless it is a proper noun (bank name, scheme name).
- Do not translate technical terms that are universally used in English (UPI, NEFT, EMI, KYC).
- If you are unsure of a word in {language}, use the English term.
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", _build_system_prompt(bank_name, is_guest, user_id) + lang_instruction),
        ("human", "{input}"),
    ])

    # Pure LLM call, no tools
    chain = prompt | llm

    # Dynamic History Truncation for Rate Limits
    limit = 6
    if language != "English":
        limit = 3
    else:
        limit = 4 

    recent_messages = state["messages"][-limit:] if len(state["messages"]) > limit else state["messages"]

    response = chain.invoke({"input": recent_messages})
    return {"messages": [response]}
