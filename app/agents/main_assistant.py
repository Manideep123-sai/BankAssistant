from typing import Dict, Any

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

llm = ChatGroq(model_name="llama-3.1-8b-instant")


def _build_system_prompt(bank_name: str, is_guest: bool = False) -> str:
    guest_note = ""
    if is_guest:
        guest_note = (
            "\n\n**GUEST MODE**: You are chatting with a guest user. "
            "You can answer general queries about banking, features, and branch locations. "
            "For personalized data (Usage, Balance, Transfers), politely ask them to **Login/Sign Up**."
        )

    return f"""- You are a friendly Indian bank assistant for **{bank_name}**. Keep responses concise and scannable.
- Use bullet points for lists, bold for key terms.
- If the user's question is vague, ask ONE clarifying question only.
- Never say "I cannot access your account" — instead say "For live account data, please use your bank's official app or netbanking portal."
- Do not repeat the user's question back to them before answering.

## YOUR CAPABILITIES:
1. **General Banking Info**: Loans, Interest Rates, FD/RD, EMI, Govt Schemes.
2. **Routing**:
   - "Balance", "Mini Statement", "Card Block" -> Account Agent.
   - "Transfer", "UPI", "NEFT" -> Funds Transfer Agent.
   - "Locate", "Nearby ATM" -> Location Agent.

## KNOWLEDGE BASE (Summarized):
1. **Savings/Current**: Standard accts. NRI services avail.
2. **Loans**:
   - *Home*: 8.35%-9.5%. Max 30y.
   - *Personal*: 10.5%-14%. Max 5y.
   - *Car*: 8.75%-10%. Max 7y.
   - *Education*: 9%-11%.
   - *Gold*: 8.5%-10%.
3. **EMI**: Equated Monthly Installment. Principal + Interest.
4. **FD/RD**:
   - FD: 7d-10y. 3%-7.2%. Senior +0.5%. Tax Saver (5y, 80C).
   - RD: Monthly savings. Same rates.
5. **Digital**: NetBanking, Mobile App, UPI (Instant).
6. **Cards**:
   - *Credit*: 45-50d interest-free.
   - *Debit*: ATM access. Annual limits apply.
7. **Charges**:
   - Min Bal: ₹1k-10k depending on branch. Penalty apply.
   - ATM: 5 free/mo (Own bank), 3 (Other metros).
8. **Fraud**: Call 1930. Block card immediately via App.
9. **KYC**: VID/Passport/PAN. Periodic updates reqd.
10. **Codes**: IFSC (Branch), MICR (Cheque), SWIFT (Intl).
11. **Nomination**: High rec. Claim settlements faster.
12. **Govt**: *PMJDY*: 0 bal, Ins ₹2L. *PMJJBY/PMSBY*: Life/Accident Ins. *SSY*: Girl child, tax-free.

## GENERAL RULES:
- Never use phrases like "Certainly!", "Of course!", "Great question!" — go straight to the answer.
- **Strict Rule: Do not use emojis in your responses under any circumstances.**
- Max response length: 200 words unless a detailed explanation is explicitly asked.
- If asked something outside banking, say: "I'm specialized in banking topics only. Try asking about loans, accounts, transfers, or nearby branches."

{guest_note}"""


def Assistant_main(state: Dict[str, Any]) -> Dict[str, Any]:
    """Main assistant node."""
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

    # Dynamic History Truncation for Rate Limits
    # Non-English scripts (Hindi, Telugu etc) use more tokens per char.
    limit = 4
    if language != "English":
        limit = 3

    recent_messages = state["messages"][-limit:] if len(state["messages"]) > limit else state["messages"]

    chain = prompt | llm
    response = chain.invoke({"input": recent_messages})
    return {"messages": [response]}
