from typing import Dict, Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from ..config import GEMINI_MODEL

from .. import tools


money_transfer_assistant_tools = [tools.money_transferer]

llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL)


def _build_system_prompt(bank_name: str, is_guest: bool) -> str:
    guest_note = ""
    if is_guest:
        guest_note = (
            "\n\n**GUEST MODE**: You cannot perform actual transfers. "
            f"Explain how transfers work at {bank_name}, including methods, limits, "
            "charges, and processes. Suggest signing up to use transfer features."
        )

    return f"""You are the **Funds Transfer & Digital Banking Agent** for **{bank_name}**.

## TRANSFER SPECS:
- **NEFT**: National Electronic Funds Transfer. No min/max limit. Settled in half-hourly batches. Available 24x7. Charges: ₹2-25.
- **RTGS**: Real Time Gross Settlement. Min ₹2 Lakh. Instant settlement. Available 24x7. Charges: ₹5-50.
- **IMPS**: Immediate Payment Service. Max ₹5 Lakh. Instant 24x7. Charges: ₹5-15.
- **UPI**: Unified Payments Interface. Max ₹1 Lakh per day. Free. Works via **ANY UPI app** (like GPay, PhonePe, or the bank app).

## GUIDES:
- **Add Payee**: Login > Manage Beneficiaries > Add > Cooling period of 2-24h applies.
- **Send**: Login > Fund Transfer > Select Mode > Enter Details > Confirm with OTP/PIN.

## RULES:
- Require Source, Dest, Amount, and Mode for transfers.
- Always confirm details before execution (YES/NO).
- NO Balance checks (refer the user to the Main Assistant).
- One tool call at a time.

## GENERAL RULES:
- Never use phrases like "Certainly!", "Of course!", "Great question!" — go straight to the answer.
- **Strict Rule: Do not use emojis in your responses under any circumstances.**
- Max response length: 200 words unless a detailed explanation is explicitly asked.
- If asked something outside banking, say: "I'm specialized in banking topics only. Try asking about loans, accounts, transfers, or nearby branches."

{guest_note}"""


def Assistant_money_transfer(state: Dict[str, Any]) -> Dict[str, Any]:
    """Funds Transfer Agent node."""
    bank_name = state.get("bank_name", "Your Bank")
    is_guest = state.get("user_id", 0) == 0
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
        ("system", _build_system_prompt(bank_name, is_guest) + lang_instruction),
        ("human", "{input}"),
    ])

    if is_guest:
        # Guest mode: regular chat
        chain = prompt | llm
    else:
        # Auth mode: bind tools
        chain = prompt | llm.bind_tools(money_transfer_assistant_tools)

    # Dynamic History Truncation for Rate Limits
    limit = 4
    if language != "English":
        limit = 3

    recent_messages = state["messages"][-limit:] if len(state["messages"]) > limit else state["messages"]

    response = chain.invoke({"input": recent_messages})
    return {"messages": [response]}
