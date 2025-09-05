"""
FastAPI app for Split & Budget Tracker.
Simple bill splitting for exactly 2 friends.
"""

from fastapi import FastAPI
from routers import users, transactions, settlements, analytics
from storage.in_memory_store import SimpleStore

# Global store instance
store = SimpleStore()

# Create FastAPI application
app = FastAPI(
    title="Split & Budget Tracker",
    description="Simple bill splitting for 2 friends",
    version="1.0.0"
)

@app.post("/reset")
def reset_for_testing(user_a_amount: float = 500.0, user_b_amount: float = 500.0):
    """Reset users with individual wallet amounts for testing"""
    from decimal import Decimal
    store.reset_users(Decimal(str(user_a_amount)), Decimal(str(user_b_amount)))
    return {
        "message": f"Users reset: User A=${user_a_amount}, User B=${user_b_amount}",
        "users": len(store.get_all_users())
    }


# Include routers
app.include_router(users.router)
app.include_router(transactions.router)
app.include_router(settlements.router)
app.include_router(analytics.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)