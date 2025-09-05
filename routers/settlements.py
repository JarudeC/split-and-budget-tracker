"""Settlement endpoints - Allows users to settle outstanding balances"""

from fastapi import APIRouter, HTTPException
from models.api_models import SettlementRequest, SettlementResponse
from models.settlement import Settlement

router = APIRouter(prefix="/settle", tags=["settlements"])


@router.post("/", response_model=SettlementResponse)
def settle_debt(request: SettlementRequest):
    """Allows a user to settle their outstanding balance"""
    from main import store
    
    # Edge Case 7: Negative Settlement Amount - Prevent negative or zero settlement amounts
    if request.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail=f"Settlement amount must be positive. Received: ${request.amount}"
        )
    
    # Edge Case 2: Invalid User ID - Ensure both users exist in the system  
    try:
        from_user = store.get_user(request.from_user_id)
        store.get_user(request.to_user_id)  # Validate user exists
    except KeyError:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Edge Case 1: Insufficient Settlement Funds - Ensure settling user has enough money in wallet
    if from_user.wallet_balance < request.amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds. Available: ${from_user.wallet_balance}, Required: ${request.amount}"
        )
    
    amount_owed = store.get_amount_owed(request.from_user_id, request.to_user_id)
    # Edge Case 3: No Debt Settlement - Prevent settling when no money is actually owed
    if amount_owed == 0:
        raise HTTPException(status_code=400, detail="No outstanding debt to settle")
    
    # Edge Case 4: Excessive Settlement - Prevent settling more than what is actually owed  
    if request.amount > amount_owed:
        raise HTTPException(
            status_code=400, 
            detail=f"Settlement amount ${request.amount} exceeds debt of ${amount_owed}"
        )
    
    settlement = Settlement.create(
        from_user_id=request.from_user_id,
        to_user_id=request.to_user_id,
        amount=request.amount
    )
    
    store.add_settlement(settlement)
    updated_from_user = store.get_user(request.from_user_id)
    updated_to_user = store.get_user(request.to_user_id)
    
    return SettlementResponse(
        settlement_id=settlement.id,
        from_user_id=settlement.from_user_id,
        to_user_id=settlement.to_user_id,
        amount=settlement.amount,
        timestamp=settlement.timestamp,
        from_user_new_balance=updated_from_user.wallet_balance,
        to_user_new_balance=updated_to_user.wallet_balance,
        message=f"Settlement of ${float(settlement.amount):.2f} processed successfully"
    )


@router.get("/status", response_model=dict)
def get_settlement_status():
    """View current debt positions between users"""
    from main import store
    
    users = store.get_all_users()
    user_a, user_b = users[0], users[1]
    
    # Calculate debt between users
    a_owes_b = store.get_amount_owed(user_a.id, user_b.id)
    b_owes_a = store.get_amount_owed(user_b.id, user_a.id)
    
    return {
        "debt_summary": {
            f"{user_a.name} owes {user_b.name}": f"{float(a_owes_b):.2f}",
            f"{user_b.name} owes {user_a.name}": f"{float(b_owes_a):.2f}"
        },
        "total_outstanding_debt": f"{float(a_owes_b + b_owes_a):.2f}",
        "settlements": [
            {
                "id": settlement.id,
                "from_user": settlement.from_user_id,
                "to_user": settlement.to_user_id,
                "amount": f"{float(settlement.amount):.2f}",
                "timestamp": settlement.timestamp.isoformat()
            }
            for settlement in store.get_all_settlements()
        ]
    }