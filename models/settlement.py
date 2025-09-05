"""Settlement data model for Split & Budget Tracker"""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4
from pydantic import BaseModel


class Settlement(BaseModel):
    """Settlement record when debt is paid"""
    id: str
    from_user_id: str
    to_user_id: str
    amount: Decimal
    timestamp: datetime

    @classmethod
    def create(cls, from_user_id: str, to_user_id: str, amount: Decimal):
        """Create a new settlement"""
        return cls(
            id=str(uuid4()),
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            amount=amount,
            timestamp=datetime.now()
        )