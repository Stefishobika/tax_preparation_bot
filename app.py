import streamlit as st
import re
from tax_engine import calculate_tax

st.set_page_config(
    page_title="Tax Preparation Assistant",
    page_icon="🧾",
    layout="centered"
)

st.title("🧾 Tax Preparation Assistant")
st.caption("Rule-based chatbot for Indian tax calculation")

def parse_income(user_input: str) -> int | None:
    raw = user_input.lower().replace(",", "").strip()

    match = re.search(r"(\d+(\.\d+)?)", raw)
    if not match:
        return None

    value = float(match.group())

    if "crore" in raw or "cr" in raw:
        return int(value * 10_000_000)     
    elif "lpa" in raw:
        return int(value * 100_000)      
    elif "lakh" in raw or "lak" in raw:  
        return int(value * 100_000)        
    else:
        return int(value)                  
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.stage = "income"
    st.session_state.income = None
    st.session_state.ded_80c = 0
    st.session_state.ded_80d = 0

if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            "Hi! I can help you calculate your tax.\n\n"
            "Please enter your **annual income** "
        )
    })

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Enter your response...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    reply = ""

    if st.session_state.stage == "income":
        income = parse_income(user_input)

        if income is None:
            reply = "❌ Please enter a valid income (e.g. `30 LPA`, `2 crore`)."
        else:
            st.session_state.income = income
            st.session_state.stage = "deductions"

            reply = (
                f"Annual income recorded: **₹{income:,}**\n\n"
                "Do you invest in PF / PPF / ELSS / Life Insurance?\n"
                "(Section 80C)\nReply **yes** or **no**."
            )

    elif st.session_state.stage == "deductions":
        if "yes" in user_input.lower():
            st.session_state.ded_80c = 150000

        st.session_state.stage = "health"
        reply = (
            "Do you have **health insurance**?\n"
            "(Section 80D)\nReply **yes** or **no**."
        )

    elif st.session_state.stage == "health":
        if "yes" in user_input.lower():
            st.session_state.ded_80d = 25000

        st.session_state.stage = "done"

        total_deductions = (
            st.session_state.ded_80c + st.session_state.ded_80d
        )

        taxable, tax = calculate_tax(
            st.session_state.income,
            st.session_state.ded_80c,
            st.session_state.ded_80d
        )

        reply = f"""
### Tax Summary (Old Regime)

- **Annual Income:** ₹{st.session_state.income:,}
- **Total Deductions:** ₹{total_deductions:,}
- **Taxable Income:** ₹{taxable:,}
- **Estimated Tax Payable (incl. 4% cess):** ₹{int(tax):,}
"""

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
