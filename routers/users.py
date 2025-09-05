"""Users endpoint - Returns both users' transactions and balances"""

from fastapi import APIRouter
from models.api_models import UsersResponse, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=UsersResponse)
def get_users():
    """Returns both users' transactions and balances"""
    from main import store
    
    users = store.get_all_users()
    user_responses = []
    
    for user in users:
        user_transactions = []
        for transaction in store.get_user_transactions(user.id):
            user_transactions.append({
                "id": transaction.id,
                "amount": f"{float(transaction.amount):.2f}",
                "description": transaction.description,
                "timestamp": transaction.timestamp.isoformat()
            })
        
        other_user = store.get_other_user(user.id)
        amount_owed_to_me = store.get_amount_owed(other_user.id, user.id)
        amount_i_owe = store.get_amount_owed(user.id, other_user.id)
        net_balance = amount_owed_to_me - amount_i_owe
        
        total_spent = store.get_user_spending_total(user.id)
        
        user_response = UserResponse(
            id=user.id,
            name=user.name,
            wallet_balance=user.wallet_balance,
            total_spent=total_spent,
            transactions=user_transactions,
            net_balance=net_balance
        )
        user_responses.append(user_response)
    
    return UsersResponse(users=user_responses)