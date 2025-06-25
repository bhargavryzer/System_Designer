import unittest
from app_designer.agents.ingestion_agent import UserFlowIngestionAgent

class TestUserFlowIngestionAgent(unittest.TestCase):

    def setUp(self):
        self.agent = UserFlowIngestionAgent()

    def test_ingest_simple_flow(self):
        raw_text = "  User clicks button.  System responds.  "
        expected_text = "User clicks button. System responds."
        processed_text = self.agent.ingest_user_flow(raw_text)
        self.assertEqual(processed_text, expected_text)

    def test_ingest_empty_flow_raises_error(self):
        with self.assertRaises(ValueError):
            self.agent.ingest_user_flow("")

    def test_ingest_whitespace_flow_raises_error(self):
        # Current behavior is to strip and then check if empty.
        # If the requirement was to error on pure whitespace before strip, this test would change.
        with self.assertRaises(ValueError):
            self.agent.ingest_user_flow("   \n\t   ")

if __name__ == '__main__':
    unittest.main()
