"""Storage for Split & Budget Tracker matching exact requirements"""

from decimal import Decimal
from typing import Dict, List
from uuid import uuid4
from models.user import User
from models.transaction import Transaction, GroupExpense
from models.settlement import Settlement


class SimpleStore:
    """Storage that exactly matches the requirements example"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.group_expenses: List[GroupExpense] = []  # Track group payments for debt
        self.transactions: List[Transaction] = []  # Individual spending records for budgeting
        self.settlements: List[Settlement] = []
        
        user_a = User.create("User A")
        user_b = User.create("User B") 
        self.users[user_a.id] = user_a
        self.users[user_b.id] = user_b
    
    def get_all_users(self) -> List[User]:
        """Get both users"""
        return list(self.users.values())
    
    def get_user(self, user_id: str) -> User:
        """Get user by ID"""
        if user_id not in self.users:
            raise KeyError(f"User not found: {user_id}")
        return self.users[user_id]
    
    def get_other_user(self, user_id: str) -> User:
        """Get the other user (since there are only 2)"""
        for uid, user in self.users.items():
            if uid != user_id:
                return user
        raise KeyError(f"Other user not found for: {user_id}")
    
    def add_group_expense(self, group_expense: GroupExpense) -> None:
        """Add group expense"""
        self.group_expenses.append(group_expense)
        
        payer = self.get_user(group_expense.payer_id)
        payer.wallet_balance -= group_expense.total_amount
        
        #Track the payer's share of spending (not the full amount)
        payer_spending = Transaction.create_spending_record(
            user_id=group_expense.payer_id,
            amount=group_expense.individual_share,
            description=group_expense.description
        )
        self.transactions.append(payer_spending)
    
    def add_settlement(self, settlement: Settlement) -> None:
        """Add settlement - transfer money and create spending records for settled expenses"""
        self.settlements.append(settlement)
        
        from_user = self.get_user(settlement.from_user_id)
        to_user = self.get_user(settlement.to_user_id)
        
        # Transfer money between wallets
        from_user.wallet_balance -= settlement.amount
        to_user.wallet_balance += settlement.amount
        
        # Create spending record for settling user (their share of the expenses being settled)
        remaining_settlement = settlement.amount
        for expense in self.group_expenses:
            if (expense.payer_id == settlement.to_user_id and 
                not expense.is_settled and 
                remaining_settlement >= expense.individual_share):
                
                # Record the settling user's spending for their share of the original expense
                settler_spending = Transaction.create_spending_record(
                    user_id=settlement.from_user_id,
                    amount=expense.individual_share,
                    description=expense.description
                )
                self.transactions.append(settler_spending)
                
                # Mark expense as settled to prevent duplicate settlements
                expense.is_settled = True
                remaining_settlement -= expense.individual_share
                if remaining_settlement == 0:
                    break
    
    def get_amount_owed(self, from_user_id: str, to_user_id: str) -> Decimal:
        """Calculate net debt between users"""
        from_owes_to = Decimal("0.00")
        to_owes_from = Decimal("0.00")
        
        for expense in self.group_expenses:
            if expense.payer_id == to_user_id and not expense.is_settled:
                from_owes_to += expense.individual_share
            elif expense.payer_id == from_user_id and not expense.is_settled:
                to_owes_from += expense.individual_share
        
        net_debt = from_owes_to - to_owes_from
        
        settled_amount = Decimal("0.00")
        for settlement in self.settlements:
            if settlement.from_user_id == from_user_id and settlement.to_user_id == to_user_id:
                settled_amount += settlement.amount
            elif settlement.from_user_id == to_user_id and settlement.to_user_id == from_user_id:
                settled_amount -= settlement.amount
        
        return max(net_debt - settled_amount, Decimal("0.00"))
    
    def get_user_transactions(self, user_id: str) -> List[Transaction]:
        """Get individual spending records for a user"""
        return [tx for tx in self.transactions if tx.user_id == user_id]
    
    def get_user_spending_total(self, user_id: str) -> Decimal:
        """Get total spending for budgeting purposes"""
        return sum(tx.amount for tx in self.get_user_transactions(user_id))
    
    def get_all_group_expenses(self) -> List[GroupExpense]:
        """Get all group expenses"""
        return self.group_expenses
    
    def get_all_transactions(self) -> List[Transaction]:
        """Get all individual spending records"""
        return self.transactions
    
    def get_all_settlements(self) -> List[Settlement]:
        """Get all settlements"""
        return self.settlements
    
    def reset_users(self, user_a_amount: Decimal = Decimal("500.00"), user_b_amount: Decimal = Decimal("500.00")) -> None:
        """Reset users with individual wallet amounts (for testing purposes)"""
        self.group_expenses.clear()
        self.transactions.clear() 
        self.settlements.clear()
        
        user_a = User(
            id=str(uuid4()),
            name="User A",
            wallet_balance=user_a_amount
        )
        user_b = User(
            id=str(uuid4()),
            name="User B", 
            wallet_balance=user_b_amount
        )
        
        self.users = {user_a.id: user_a, user_b.id: user_b}