"""User data model for Split & Budget Tracker"""

from decimal import Decimal
from uuid import uuid4
from pydantic import BaseModel


class User(BaseModel):
    """User with wallet balance for cash flow and budget tracking"""
    id: str
    name: str
    wallet_balance: Decimal = Decimal("500.00")
    
    @classmethod
    def create(cls, name: str):
        """Create a new user with default balance"""
        return cls(
            id=str(uuid4()),
            name=name,
            wallet_balance=Decimal("500.00")
        )