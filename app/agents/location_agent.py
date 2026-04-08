from typing import Dict, Any
import urllib.parse
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from ..config import GEMINI_MODEL

llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL)

def _build_system_prompt(bank_name: str) -> str:
    return f"""You are the **Location Agent** for **{bank_name}**.
Your job is to help users find physical branches and ATMs with **high precision**.

## LOGIC:
1. **Analyze Input**: Look for specific details: **Street Name, Building Name, House No, Landmark, Area, City**.
2. **If Location Found**:
   - Provide 2-3 direct Google Maps Search Links for different types:
     - Branch: `https://www.google.com/maps/search/{bank_name}+branch+near+{{location}}`
     - ATM: `https://www.google.com/maps/search/{bank_name}+ATM+near+{{location}}`
     - Nearest Area: `https://www.google.com/maps/search/{bank_name}+near+{{location}}`
   - After giving the links, say: "Click the link to see live results on Google Maps."
3. **If Location VAGUE (only City)**:
   - Always ask: "Which area, street, or landmark in [City] are you looking in for a more precise result?"
4. **If Location MISSING**:
   - Ask: "Which city, area, or street are you in?"

## OUTPUT FORMAT:
- Found: "Here are the {bank_name} options near **[Location]**:\n- [Find Branch](LINK1)\n- [Find ATM](LINK2)\n- [General Search](LINK3)\n\nClick the link to see live results on Google Maps."
- Vague: "I found results in **[City]**, but for a closer match, which **area, street, or landmark** are you near?"

## GENERAL RULES:
- Never use phrases like "Certainly!", "Of course!", "Great question!" — go straight to the answer.
- **Strict Rule: Do not use emojis in your responses under any circumstances.**
- Max response length: 200 words unless a detailed explanation is explicitly asked.
- If asked something outside banking, say: "I'm specialized in banking topics only. Try asking about loans, accounts, transfers, or nearby branches."
"""

def Assistant_location(state: Dict[str, Any]) -> Dict[str, Any]:
    """Location Agent node."""
    bank_name = state.get("bank_name", "Your Bank")
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
        ("system", _build_system_prompt(bank_name) + lang_instruction),
        ("human", "{input}"),
    ])
    
    # Dynamic History Truncation for Rate Limits
    limit = 4
    if language != "English":
        limit = 3
    
    recent_messages = state["messages"][-limit:] if len(state["messages"]) > limit else state["messages"]

    chain = prompt | llm
    response = chain.invoke({"input": recent_messages})
    
    return {"messages": [response]}
