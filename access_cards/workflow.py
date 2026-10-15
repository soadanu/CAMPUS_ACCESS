from access_cards import storage
def _require_status(request_id, required, action):
    """Fetch the request and check it is in the status this action needs."""
    request = storage.get_request(request_id)
    if request["status"] != required:
        raise ValueError(
            f"cannot {action}: {request_id} is '{request['status']}', "
            f"must be '{required}'"
        )
    return request


def approve_request(request_id, approved_by):
    try:
        _require_status(request_id, "requested", "approve")
        storage.update_request(request_id, "approved", approved_by)
    except ValueError as error:
        return f"Error: {error}"
    return f"Success: {request_id} approved by {approved_by}"


def issue_card(request_id):
    try:
        _require_status(request_id, "approved", "issue")
        storage.update_request(request_id, "issued")
    except ValueError as error:
        return f"Error: {error}"
    return f"Success: card issued for {request_id}"


def return_card(request_id):
    try:
        _require_status(request_id, "issued", "return")
        storage.update_request(request_id, "returned")
    except ValueError as error:
        return f"Error: {error}"
    return f"Success: card returned for {request_id}"