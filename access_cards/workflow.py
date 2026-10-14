def approve_request(request_id, approved_by):
    try:
        req = ALLOWED_STATUSES[request_id]

        req_id = request_id
    except KeyError as e:
        print(f"missing key error: {e}")
        raise KeyError("Unknown request ID")

    current_status = req.get("status")
    approved = approved_by.strip()
    if not  approved:
        raise ValueError("Approved should not be empty")

    if current_status != "requested":
        raise ValueError(
            f"Illegal state transition! Cannot approve a request that is currently '{current_status}'."
        )

    req["status"] = "approved"
    
    return f"Request {req_id} approved by {approved}"


def issue_card(request_id):
    try:
        req = ALLOWED_STATUSES[request_id]
        req_id = request_id
    except KeyError as e:
        print(f"missing key error: {e}")
        raise KeyError("Unknown request ID")

    current_status = req.get("status")
    if current_status != "approved":
        raise ValueError("Not approved yet")
    if not req["approved_by"]:
        raise ValueError("approved_by must not be empty or None")   
    req["status"] = "issued"
    return f"Status updated"


def return_card(request_id):
    try:
        req = ALLOWED_STATUSES[request_id]
        req_id = request_id
    except KeyError as e:
        print(f"missing key error: {e}")
        raise KeyError("Unknown request ID")
    current_status = req.get("status")
    if current_status != "issued":
        raise ValueError("current status must be issued")
    req["status"] = "returned"
    return f"Status updated to return"
