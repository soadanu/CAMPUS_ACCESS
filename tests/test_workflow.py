import unittest
from access_cards.storage import ALLOWED_STATUSES
from access_cards.workflow import approve_request, issue_card, return_card

class TestWorkflow(unittest.TestCase):

    def setUp(self):
        ALLOWED_STATUSES.clear()

    def test_workflow_happy_path(self):
        ALLOWED_STATUSES["A001"] = {
            "id": "A001",
            "fellow_id": "F001",
            "card_type": "visitor",
            "status": "requested",
            "approved_by": None
        }
        
        approve_request("A001", "M01")
        self.assertEqual(ALLOWED_STATUSES["A001"]["status"], "approved")
        self.assertEqual(ALLOWED_STATUSES["A001"]["approved_by"], "M01")
        
        issue_card("A001")
        self.assertEqual(ALLOWED_STATUSES["A001"]["status"], "issued")
        
        return_card("A001")
        self.assertEqual(ALLOWED_STATUSES["A001"]["status"], "returned")

    def test_issue_rejected_if_not_approved(self):
        ALLOWED_STATUSES["A001"] = {
            "id": "A001",
            "fellow_id": "F001",
            "card_type": "visitor",
            "status": "requested",
            "approved_by": None
        }
        
        with self.assertRaises(ValueError):
            issue_card("A001")
            
        self.assertEqual(ALLOWED_STATUSES["A001"]["status"], "requested")

    def test_approval_rejected_if_approver_blank(self):
        ALLOWED_STATUSES["A001"] = {
            "id": "A001",
            "fellow_id": "F001",
            "card_type": "visitor",
            "status": "requested",
            "approved_by": None
        }
        
        with self.assertRaises(ValueError):
            approve_request("A001", "   ")
            
        self.assertEqual(ALLOWED_STATUSES["A001"]["status"], "requested")
        self.assertIsNone(ALLOWED_STATUSES["A001"]["approved_by"])

    def test_return_rejected_if_already_returned(self):
        ALLOWED_STATUSES["A001"] = {
            "id": "A001",
            "fellow_id": "F001",
            "card_type": "visitor",
            "status": "returned",
            "approved_by": "M01"
        }
        
        with self.assertRaises(ValueError):
            return_card("A001")
            
        self.assertEqual(ALLOWED_STATUSES["A001"]["status"], "returned")

if __name__ == "__main__":
    unittest.main()
