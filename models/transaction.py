"""Transaction data model for Split & Budget Tracker"""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4
from pydantic import BaseModel


class Transaction(BaseModel):
    """Individual spending record for budget tracking"""
    id: str
    user_id: str
    amount: Decimal
    description: str
    timestamp: datetime

    @classmethod
    def create_spending_record(cls, user_id: str, amount: Decimal, description: str):
        """Create individual spending record for budgeting"""
        return cls(
            id=str(uuid4()),
            user_id=user_id,
            amount=amount,
            description=description,
            timestamp=datetime.now()
        )


class GroupExpense(BaseModel):
    """Group expense that creates debt between users"""
    id: str
    payer_id: str
    total_amount: Decimal
    individual_share: Decimal
    description: str
    timestamp: datetime
    is_settled: bool = False

    @classmethod
    def create(cls, payer_id: str, total_amount: Decimal, description: str):
        """Create a group expense split equally between two users with proper currency rounding"""
        individual_share = Decimal(str(round(float(total_amount / 2), 2)))
        
        return cls(
            id=str(uuid4()),
            payer_id=payer_id,
            total_amount=total_amount,
            individual_share=individual_share,
            description=description,
            timestamp=datetime.now()
        )