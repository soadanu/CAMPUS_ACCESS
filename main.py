import sys
from campusflow.storage import create_request, save_requests, load_requests, get_request
from campusflow.workflow import approve_request, issue_card, return_card

DATA_FILE = "data.json"

def run_menu():
    try:
        load_requests(DATA_FILE)
    except FileNotFoundError:
        print("Starting a new campus access registry.")
    except Exception as e:
        print(f"Error loading system data: {e}")
        return

    while True:
        print("\n=== CAMPUS ACCESS CARD SYSTEM ===")
        print("1. Create Card Request")
        print("2. Approve Card Request")
        print("3. Issue Access Card")
        print("4. Return Access Card")
        print("5. Save Current Registry")
        print("6. Quit Safely")
        
        choice = input("Select an option (1-6): ").strip()
        
        try:
            if choice == "1":
                fellow_id = input("Enter Fellow ID: ")
                card_type = input("Enter Card Type (visitor/student/staff): ")
                record = create_request(fellow_id, card_type)
                print(f"Success: Created record {record['id']} as {record['status']}")
                
            elif choice == "2":
                req_id = input("Enter Request ID (e.g., A001): ").strip()
                approver = input("Enter Approver Staff ID: ")
                msg = approve_request(req_id, approver)
                print(msg)
                
            elif choice == "3":
                req_id = input("Enter Request ID (e.g., A001): ").strip()
                msg = issue_card(req_id)
                print(msg)
                
            elif choice == "4":
                req_id = input("Enter Request ID (e.g., A001): ").strip()
                msg = return_card(req_id)
                print(msg)
                
            elif choice == "5":
                save_requests(DATA_FILE)
                print("Registry saved successfully to disk.")
                
            elif choice == "6":
                print("Exiting campus access system. Goodbye.")
                sys.exit(0)
                
            else:
                print("Unrecognized option. Please try entering a number between 1 and 6.")
                
        except (ValueError, KeyError) as error:
            print(f"Operation Blocked: {error}")

if __name__ == "__main__":
    run_menu()
