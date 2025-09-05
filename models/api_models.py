"""API request and response models for Split & Budget Tracker"""

from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Any
from pydantic import BaseModel


class TransactionRequest(BaseModel):
    """Request to record a bill payment"""
    payer_id: str
    total_amount: Decimal
    description: str


class SettlementRequest(BaseModel):
    """Request to settle outstanding balance"""
    from_user_id: str
    to_user_id: str
    amount: Decimal


class UserResponse(BaseModel):
    """User response - transactions and balances"""
    id: str
    name: str
    wallet_balance: Decimal
    total_spent: Decimal
    transactions: List[Dict[str, Any]]
    net_balance: Decimal


class UsersResponse(BaseModel):
    """Response for GET /users endpoint"""
    users: List[UserResponse]


class TransactionResponse(BaseModel):
    """Response for POST /transactions - bill payment recorded"""
    group_expense_id: str
    payer_id: str
    total_amount: Decimal
    individual_share: Decimal
    description: str
    timestamp: datetime
    payer_new_wallet_balance: Decimal
    amount_owed_by_other: Decimal
    message: str


class SettlementResponse(BaseModel):
    """Response for POST /settle"""
    settlement_id: str
    from_user_id: str
    to_user_id: str
    amount: Decimal
    timestamp: datetime
    from_user_new_balance: Decimal
    to_user_new_balance: Decimal
    message: str