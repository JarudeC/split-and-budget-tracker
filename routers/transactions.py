"""Transactions endpoints matching exact requirements"""

from typing import List
from fastapi import APIRouter, HTTPException
from models.api_models import TransactionRequest, TransactionResponse
from models.transaction import GroupExpense

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/", response_model=TransactionResponse)
def create_transaction(request: TransactionRequest):
    """Records a bill payment: who paid, total amount"""
    from main import store
    
    # Edge Case 5: Negative Transaction Amount - Prevent negative or zero transaction amounts
    if request.total_amount <= 0:
        raise HTTPException(
            status_code=400,
            detail=f"Transaction amount must be positive. Received: ${request.total_amount}"
        )
    
    # Edge Case 2: Invalid User ID - Ensure payer exists in the system
    try:
        payer = store.get_user(request.payer_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Payer not found")
    
    # Edge Case 1: Insufficient Transaction Funds - Ensure payer has enough money in wallet
    if payer.wallet_balance < request.total_amount:
        raise HTTPException(
            status_code=400, 
            detail=f"Insufficient funds. Available: ${payer.wallet_balance}, Required: ${request.total_amount}"
        )
    
    group_expense = GroupExpense.create(
        payer_id=request.payer_id,
        total_amount=request.total_amount,
        description=request.description
    )
    
    store.add_group_expense(group_expense)
    updated_payer = store.get_user(request.payer_id)
    other_user = store.get_other_user(request.payer_id)
    amount_owed = store.get_amount_owed(other_user.id, request.payer_id)
    
    return TransactionResponse(
        group_expense_id=group_expense.id,
        payer_id=group_expense.payer_id,
        total_amount=group_expense.total_amount,
        individual_share=group_expense.individual_share,
        description=group_expense.description,
        timestamp=group_expense.timestamp,
        payer_new_wallet_balance=updated_payer.wallet_balance,
        amount_owed_by_other=amount_owed,
        message=f"Bill payment recorded. Other user owes ${float(group_expense.individual_share):.2f}"
    )


@router.get("/", response_model=List[dict])
def get_transactions():
    """Lists all past transactions with who paid and splits"""
    from main import store
    
    group_expenses = store.get_all_group_expenses()
    users = store.get_all_users()
    user_names = {user.id: user.name for user in users}
    
    result = []
    for expense in group_expenses:
        result.append({
            "id": expense.id,
            "payer": user_names.get(expense.payer_id, "Unknown"),
            "total_amount": f"{float(expense.total_amount):.2f}",
            "individual_share": f"{float(expense.individual_share):.2f}",
            "description": expense.description,
            "timestamp": expense.timestamp.isoformat(),
            "is_settled": expense.is_settled
        })
    
    return result