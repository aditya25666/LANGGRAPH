# ==========================================================
#                       IMPORTS
# ==========================================================

from typing import TypedDict, Annotated
from operator import add
from langgraph.graph import StateGraph, START, END


# ==========================================================
#                         STATE
# ==========================================================

class ATMState(TypedDict):

    entered_pin: int
    correct_pin: int

    account_number: str

    balance: int
    withdraw_amount: int
    remaining_balance: int

    status: str

    receipt: str

    history: Annotated[list[str], add]

# ==========================================================
#                   VERIFY PIN NODE
# ==========================================================

def verify_pin(state: ATMState):

    print("\n========== VERIFY PIN ==========")
    print(f"Entered PIN : {state['entered_pin']}")

    return {
    "history": ["PIN verification started"]
}


# ==========================================================
#                   REJECT PIN NODE
# ==========================================================

def reject_pin(state: ATMState):

    print("\n❌ Incorrect PIN")

    return {
    "status": "PIN_VERIFICATION_FAILED",
    "history": ["PIN verification failed"]
}


# ==========================================================
#                 CHECK BALANCE NODE
# ==========================================================

def check_balance(state: ATMState):

    print("\n========== CHECK BALANCE ==========")

    print(f"Available Balance : ₹{state['balance']}")
    print(f"Requested Amount  : ₹{state['withdraw_amount']}")

    return {
    "history": ["Balance checked"]
}


# ==========================================================
#             DECLINE TRANSACTION NODE
# ==========================================================

def decline_transaction(state: ATMState):

    print("\n❌ Insufficient Balance")

    return {
    "status": "INSUFFICIENT_BALANCE",
    "history": ["Transaction declined"]
}


# ==========================================================
#               DISPENSE CASH NODE
# ==========================================================

def dispense_cash(state: ATMState):

    print(f"\n💵 Dispensing ₹{state['withdraw_amount']}")

    return {
    "status": "CASH_DISPENSED",
    "history": ["Cash dispensed"]
}


# ==========================================================
#             UPDATE BALANCE NODE
# ==========================================================

def update_balance(state: ATMState):

    remaining = state["balance"] - state["withdraw_amount"]

    print(f"\n✅ Remaining Balance : ₹{remaining}")

    return {

    "remaining_balance": remaining,

    "status": "TRANSACTION_SUCCESS",

    "history": ["Balance updated"]

}

# ==========================================================
#                 PRINT RECEIPT NODE
# ==========================================================

def print_receipt(state: ATMState):

    receipt = f"""
============== ATM RECEIPT ==============

Account Number : XXXX{state["account_number"][-4:]}

Withdrawn      : ₹{state["withdraw_amount"]}

Remaining      : ₹{state["remaining_balance"]}

Status         : {state["status"]}

=========================================
"""

    print(receipt)

    return {
    "receipt": receipt,
    "history": ["Receipt printed"]
}


# ==========================================================
#                 PIN ROUTER
# ==========================================================

def pin_router(state: ATMState):

    if state["entered_pin"] == state["correct_pin"]:

        return "check_balance"

    return "reject_pin"


# ==========================================================
#               BALANCE ROUTER
# ==========================================================

def balance_router(state: ATMState):

    if state["balance"] >= state["withdraw_amount"]:

        return "dispense_cash"

    return "decline_transaction"


# ==========================================================
#                 BUILD GRAPH
# ==========================================================

builder = StateGraph(ATMState)


# ---------------- Add Nodes ----------------

builder.add_node("verify_pin", verify_pin)

builder.add_node("reject_pin", reject_pin)

builder.add_node("check_balance", check_balance)

builder.add_node("decline_transaction", decline_transaction)

builder.add_node("dispense_cash", dispense_cash)

builder.add_node("update_balance", update_balance)

builder.add_node(
    "print_receipt",
    print_receipt
)


# ---------------- Add Edges ----------------

builder.add_edge(START, "verify_pin")


builder.add_conditional_edges(

    "verify_pin",

    pin_router,

    {

        "check_balance": "check_balance",

        "reject_pin": "reject_pin"

    }

)


builder.add_conditional_edges(

    "check_balance",

    balance_router,

    {

        "dispense_cash": "dispense_cash",

        "decline_transaction": "decline_transaction"

    }

)


builder.add_edge(
    "dispense_cash",
    "update_balance"
)

builder.add_edge(
    "update_balance",
    "print_receipt"
)

builder.add_edge(
    "print_receipt",
    END
)

builder.add_edge(

    "update_balance",

    END

)

builder.add_edge(

    "decline_transaction",

    END

)

builder.add_edge(

    "reject_pin",

    END

)


# ==========================================================
#               COMPILE GRAPH
# ==========================================================

graph = builder.compile()


# ==========================================================
#             PRINT MERMAID GRAPH
# ==========================================================

print(graph.get_graph().draw_mermaid())


# ==========================================================
#                RUN GRAPH
# ==========================================================

result = graph.invoke({

    "entered_pin": 1234,

    "correct_pin": 1234,

    "account_number": "9876543210",

    "balance": 5000,

    "withdraw_amount": 1500,

    "history": []

})

print("\n========== FINAL STATE ==========")

print(result)

print("\n========== TRANSACTION HISTORY ==========")

for step in result["history"]:
    print(step)