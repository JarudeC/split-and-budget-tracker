"""
Enhanced Interactive Split & Budget Tracker Workflow
Comprehensive testing tool with user input and edge case validation
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def print_header(title: str):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def print_response(response):
    """Print formatted API response"""
    print(f"\nStatus: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2, default=str)}")
    else:
        print(f"Error: {response.text}")

def get_users() -> Dict[str, Any]:
    """Get users and return the response data"""
    response = requests.get(f"{BASE_URL}/users")
    print_response(response)
    if response.status_code == 200:
        return response.json()
    return {}

def show_menu():
    """Display available actions"""
    print(f"\n{'='*75}")
    print("1. GET  /users           - View balances and transactions")
    print("2. POST /transactions    - Create bill payment")
    print("3. GET  /transactions    - View transaction history") 
    print("4. POST /settle          - Settle debt payment")
    print("5. GET  /settle/status   - View debt status")
    print("6. GET  /analytics       - View spending insights")
    print("7. TEST Edge cases       - Test validation errors")
    print("8. POST /reset           - Reset users with individual wallet balances")
    print()
    print("Commands: 'menu' = full options, 'exit' = finish")
    print('='*75)

def handle_transaction():
    """Handle transaction creation with user input"""
    users_data = get_users()
    if not users_data or "users" not in users_data:
        print("Could not get users")
        return
    
    users = users_data["users"]
    print(f"\nAvailable users:")
    for user in users:
        print(f"  {user['name']} - Wallet: ${user['wallet_balance']}")
    
    try:
        payer_name = input(f"\nWho paid the bill? Type '{users[0]['name']}' or '{users[1]['name']}': ").strip()
        payer_choice = None
        
        if payer_name.lower() in [users[0]['name'].lower(), 'user a', 'a']:
            payer_choice = 0
        elif payer_name.lower() in [users[1]['name'].lower(), 'user b', 'b']:
            payer_choice = 1
        else:
            print(f"Invalid choice. Please type '{users[0]['name']}' or '{users[1]['name']}'")
            return
        
        amount = float(input("Enter total amount: $"))
        description = input("Enter description: ") or "Test transaction"
        
        payer_id = users[payer_choice]["id"]
        
        transaction_data = {
            "payer_id": payer_id,
            "total_amount": amount,
            "description": description
        }
        
        print(f"\nCreating transaction...")
        response = requests.post(f"{BASE_URL}/transactions", json=transaction_data)
        print_response(response)
        
    except (ValueError, KeyError) as e:
        print(f"Invalid input: {e}")

def handle_settlement():
    """Handle debt settlement with user input"""
    users_data = get_users()
    if not users_data or "users" not in users_data:
        print("Could not get users")
        return
    
    users = users_data["users"]
    print(f"\nDebt Status:")
    for user in users:
        net_balance = float(user.get('net_balance', 0))
        if net_balance > 0:
            print(f"  {user['name']}: Is owed ${net_balance}")
        elif net_balance < 0:
            print(f"  {user['name']}: Owes ${abs(net_balance)}")
        else:
            print(f"  {user['name']}: No debt (settled)")
    
    try:
        from_name = input(f"\nWho is settling their debt? Type '{users[0]['name']}' or '{users[1]['name']}': ").strip()
        to_name = input(f"Who are they paying back? Type '{users[0]['name']}' or '{users[1]['name']}': ").strip()
        
        from_choice = None
        to_choice = None
        
        if from_name.lower() in [users[0]['name'].lower(), 'user a', 'a']:
            from_choice = 0
        elif from_name.lower() in [users[1]['name'].lower(), 'user b', 'b']:
            from_choice = 1
        
        if to_name.lower() in [users[0]['name'].lower(), 'user a', 'a']:
            to_choice = 0
        elif to_name.lower() in [users[1]['name'].lower(), 'user b', 'b']:
            to_choice = 1
        
        if from_choice is None or to_choice is None or from_choice == to_choice:
            print(f"Invalid choice. Please type '{users[0]['name']}' or '{users[1]['name']}' for different users")
            return
        
        amount = float(input("Enter settlement amount: $"))
        
        settlement_data = {
            "from_user_id": users[from_choice]["id"],
            "to_user_id": users[to_choice]["id"],
            "amount": amount
        }
        
        print(f"\nProcessing settlement...")
        response = requests.post(f"{BASE_URL}/settle", json=settlement_data)
        print_response(response)
        
    except (ValueError, KeyError) as e:
        print(f"Invalid input: {e}")

def handle_reset():
    """Handle resetting users with individual wallet amounts"""
    try:
        user_a_amount = float(input("Enter wallet balance for User A: $"))
        user_b_amount = float(input("Enter wallet balance for User B: $"))
        
        print(f"\nResetting users: User A=${user_a_amount}, User B=${user_b_amount}...")
        response = requests.post(f"{BASE_URL}/reset", params={
            "user_a_amount": user_a_amount,
            "user_b_amount": user_b_amount
        })
        print_response(response)
        
    except ValueError:
        print("Invalid amount entered")

def test_edge_cases():
    """Test various edge cases"""
    print_header("EDGE CASE TESTING")
    print("Testing validation and error handling with intentionally bad inputs")
    
    users_data = get_users()
    if not users_data or "users" not in users_data:
        print("Could not get users")
        return
    
    users = users_data["users"]
    user_a_id = users[0]["id"]
    user_b_id = users[1]["id"]
    user_a_balance = float(users[0]["wallet_balance"])
    
    print(f"\nCurrent state: User A has ${user_a_balance} wallet balance")
    print(f"User A ID: {user_a_id}")
    print(f"User B ID: {user_b_id}")
    
    edge_cases = [
        {
            "name": "Insufficient Funds Transaction",
            "description": f"Trying to spend ${user_a_balance + 100} when User A only has ${user_a_balance}",
            "expected": "Should return 400 error - insufficient funds",
            "action": lambda: requests.post(f"{BASE_URL}/transactions", json={
                "payer_id": user_a_id,
                "total_amount": user_a_balance + 100,
                "description": "Over-budget test"
            })
        },
        {
            "name": "Invalid User Transaction", 
            "description": "Using a fake user ID that doesn't exist",
            "expected": "Should return 404 error - user not found",
            "action": lambda: requests.post(f"{BASE_URL}/transactions", json={
                "payer_id": "fake-user-id",
                "total_amount": 50,
                "description": "Fake user test"
            })
        },
        {
            "name": "No Debt Settlement",
            "description": "Trying to settle debt when no money is owed",
            "expected": "Should return 400 error - no outstanding debt",
            "action": lambda: requests.post(f"{BASE_URL}/settle", json={
                "from_user_id": user_a_id,
                "to_user_id": user_b_id,
                "amount": 10
            })
        },
        {
            "name": "Excessive Settlement",
            "description": "Trying to settle more than what's owed",
            "expected": "Should return 400 error - exceeds debt amount",
            "action": lambda: requests.post(f"{BASE_URL}/settle", json={
                "from_user_id": user_b_id,
                "to_user_id": user_a_id,
                "amount": 999999
            })
        },
        {
            "name": "Negative Transaction Amount",
            "description": "Trying to create transaction with negative amount",
            "expected": "Should return 400 error - amount must be positive",
            "action": lambda: requests.post(f"{BASE_URL}/transactions", json={
                "payer_id": user_a_id,
                "total_amount": -50.0,
                "description": "Negative amount test"
            })
        },
        {
            "name": "Zero Transaction Amount",
            "description": "Trying to create transaction with zero amount",
            "expected": "Should return 400 error - amount must be positive",
            "action": lambda: requests.post(f"{BASE_URL}/transactions", json={
                "payer_id": user_a_id,
                "total_amount": 0.0,
                "description": "Zero amount test"
            })
        },
        {
            "name": "Negative Settlement Amount",
            "description": "Trying to settle with negative amount",
            "expected": "Should return 400 error - amount must be positive",
            "action": lambda: requests.post(f"{BASE_URL}/settle", json={
                "from_user_id": user_a_id,
                "to_user_id": user_b_id,
                "amount": -25.0
            })
        }
    ]
    
    for i, test_case in enumerate(edge_cases, 1):
        print(f"\n{'='*60}")
        print(f"EDGE CASE {i}: {test_case['name']}")
        print(f"What we're doing: {test_case['description']}")
        print(f"Expected result: {test_case['expected']}")
        print('='*60)
        
        try:
            response = test_case["action"]()
            print_response(response)
            
            # Provide analysis
            if response.status_code >= 400:
                print("✅ PASS: Error correctly caught and returned appropriate status code")
            else:
                print("❌ UNEXPECTED: This should have failed but didn't")
                
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
        
        if i < len(edge_cases):
            input("\nPress Enter to continue to next test...")
    
    print(f"\n{'='*60}")
    print("EDGE CASE TESTING COMPLETE")
    print("All tests verify the API properly validates inputs and handles errors")
    print('='*60)

def main():
    """Main interactive loop"""
    print_header("ENHANCED SPLIT & BUDGET TRACKER TESTING")
    print("Interactive testing environment for comprehensive functionality validation")
    
    # Initial status
    print_header("INITIAL STATE")
    get_users()
    
    while True:
        try:
            # Show options before each prompt
            show_menu()
            command = input(f"Enter action (1-8) or command: ").strip().lower()
            
            if command == "exit":
                print_header("FINAL ANALYTICS & SUMMARY")
                # Show final analytics
                print("\nFinal Analytics:")
                response = requests.get(f"{BASE_URL}/analytics/spending-insights")
                print_response(response)
                
                print("\nTesting session complete!")
                break
                
            elif command == "menu":
                show_menu()
                
            elif command == "1":
                print_header("USERS STATUS")
                get_users()
                
            elif command == "2":
                print_header("CREATE TRANSACTION")
                handle_transaction()
                
            elif command == "3":
                print_header("TRANSACTION HISTORY")
                response = requests.get(f"{BASE_URL}/transactions")
                print_response(response)
                
            elif command == "4":
                print_header("SETTLE DEBT")
                handle_settlement()
                
            elif command == "5":
                print_header("SETTLEMENT STATUS")
                response = requests.get(f"{BASE_URL}/settle/status")
                print_response(response)
                
            elif command == "6":
                print_header("ANALYTICS")
                response = requests.get(f"{BASE_URL}/analytics/spending-insights")
                print_response(response)
                
            elif command == "7":
                test_edge_cases()
                
            elif command == "8":
                print_header("RESET USERS")
                handle_reset()
                
            else:
                print("Invalid command. Type 'menu' for options or 'exit' to finish.")
                
        except KeyboardInterrupt:
            print(f"\n\nSession interrupted. Type 'exit' to see final analytics.")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print("WARNING: Make sure the server is running: uvicorn main:app --reload")
    input("Press Enter when server is ready...")
    
    try:
        # Test connection
        response = requests.get(f"{BASE_URL}/users", timeout=5)
        if response.status_code != 200:
            print("Server not responding correctly")
            exit(1)
            
        main()
        
    except requests.exceptions.ConnectionError:
        print("Cannot connect to server. Please start with: uvicorn main:app --reload")
    except Exception as e:
        print(f"Unexpected error: {e}")