# Split & Budget Tracker

Simple bill splitting for 2 friends with equal expense shares and debt tracking.

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python main.py

# Test the system
python showcase_workflow.py
```

## Example API Workflow

**1. Initial state - both users have $500:**
```bash
GET /users
Response: {
  "users": [
    {"name": "User A", "wallet_balance": "500.00", "total_spent": "0.00", "net_balance": "0.00"},
    {"name": "User B", "wallet_balance": "500.00", "total_spent": "0.00", "net_balance": "0.00"}
  ]
}
```

**2. User A pays $120 for dinner (split equally):**
```bash
POST /transactions
{
  "payer_id": "user_a_id",
  "total_amount": 120.00,
  "description": "Dinner"
}

Response: {
  "individual_share": "60.00",
  "payer_new_wallet_balance": "380.00",
  "amount_owed_by_other": "60.00",
  "message": "Bill payment recorded. Other user owes $60.00"
}
```

**3. Check updated balances:**
```bash
GET /users
Response: {
  "users": [
    {"name": "User A", "wallet_balance": "380.00", "total_spent": "60.00", "net_balance": "60.00"},
    {"name": "User B", "wallet_balance": "500.00", "total_spent": "0.00", "net_balance": "-60.00"}
  ]
}
```

**4. User B settles by paying User A $60:**
```bash
POST /settle
{
  "from_user_id": "user_b_id",
  "to_user_id": "user_a_id",
  "amount": 60.00
}

Response: {
  "from_user_new_balance": "440.00",
  "to_user_new_balance": "440.00",
  "message": "Settlement of $60.00 processed successfully"
}
```

**5. Final state - both spent $60, debt settled:**
```bash
GET /users
Response: {
  "users": [
    {"name": "User A", "wallet_balance": "440.00", "total_spent": "60.00", "net_balance": "0.00"},
    {"name": "User B", "wallet_balance": "440.00", "total_spent": "60.00", "net_balance": "0.00"}
  ]
}
```

## Summary of Approach

### Analysis of Requirements

**Key Requirements Identified:**
- Exactly 2 users with fixed $500 wallets (no user management needed)
- Equal 50/50 bill splitting (automatic calculation, no manual percentages)
- Dual tracking: cash flow (wallet) vs spending (budget) 
- Debt management between friends with settlement capability

**Domain Model Design:**
- `GroupExpense`: Tracks who paid what (creates debt)
- `Transaction`: Individual spending records (budget tracking)
- `Settlement`: Debt payments between users
- Clean separation prevents mixing cash flow with spending data

### Edge Cases & Validation Handled

**Financial Edge Cases:**
- Insufficient wallet funds validation (`transactions.py:27-31`)
- Negative amounts blocked (`transactions.py:16-20`)
- Overpayment prevention (`settlements.py:37-41`) 
- Currency rounding precision (`transaction.py:42`)

**Business Logic Edge Cases:**
- Settling non-existent debt blocked (`settlements.py:34-35`)
- User not found handling (`transactions.py:24-25`)
- Net debt calculation handles cross-debts properly (`in_memory_store.py:83-103`)

**Data Integrity:**
- Pydantic models ensure type safety
- Decimal precision for currency calculations
- Atomic operations in storage layer

### Backend Design & API Structure

**Clean Architecture:**
```
API Layer (FastAPI routers) → Domain Models → Storage Layer
```

**RESTful API Design:**
- Resource-based endpoints (`/users`, `/transactions`, `/settle`)
- Clear request/response models with typed validation
- Proper HTTP status codes and error messages
- Comprehensive response data for UI needs

**Storage Pattern:**
- Repository pattern with `SimpleStore` class
- Encapsulated business logic (debt calculation, settlements)
- In-memory storage matching requirements (no persistence needed)

**Code Quality:**
- SOLID principles: Single responsibility per class/function
- DRY: Reusable models and utility functions
- KISS: Minimal complexity, focused on core requirements
- Type safety throughout with Pydantic and proper Python typing

### Testing & Validation Script

**Comprehensive Workflow Testing:**
- Interactive `showcase_workflow.py` demonstrating all features
- Edge case testing menu option
- Real API calls against running server
- Guided user experience with clear feedback

**Demonstrates:**
- Full transaction lifecycle (payment → debt → settlement)
- Error handling with meaningful messages
- Data consistency across operations
- Professional API documentation via FastAPI