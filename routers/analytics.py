"""Simple analytics endpoint for spending insights"""

from typing import Dict
from decimal import Decimal
from fastapi import APIRouter
from pydantic import BaseModel


class Analytics(BaseModel):
    """Simple analytics response"""
    total_transactions: int
    total_amount_spent: Decimal
    average_transaction: Decimal
    user_balances: Dict[str, Decimal]
    debt_status: str


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/spending-insights", response_model=Analytics)
def get_spending_insights():
    """Get simple spending analytics"""
    from main import store
    
    group_expenses = store.get_all_group_expenses()
    users = store.get_all_users()
    
    total_transactions = len(group_expenses)
    total_amount = sum(expense.total_amount for expense in group_expenses)
    avg_amount = round(total_amount / total_transactions, 2) if total_transactions > 0 else Decimal("0.00")
    
    user_balances = {user.name: user.wallet_balance for user in users}
    
    user_a, user_b = users[0], users[1]
    a_owes_b = store.get_amount_owed(user_a.id, user_b.id)
    b_owes_a = store.get_amount_owed(user_b.id, user_a.id)
    
    if a_owes_b > 0:
        debt_status = f"{user_a.name} owes {user_b.name}: ${a_owes_b}"
    elif b_owes_a > 0:
        debt_status = f"{user_b.name} owes {user_a.name}: ${b_owes_a}"
    else:
        debt_status = "No outstanding debts - all settled"
    
    return Analytics(
        total_transactions=total_transactions,
        total_amount_spent=total_amount,
        average_transaction=avg_amount,
        user_balances=user_balances,
        debt_status=debt_status
    )