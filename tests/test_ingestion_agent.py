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
        with self.assertRaisesRegex(ValueError, "User flow text cannot be empty."):
            self.agent.ingest_user_flow("")

    def test_ingest_whitespace_only_flow_raises_error(self):
        # This input, after strip(), becomes empty.
        with self.assertRaisesRegex(ValueError, "User flow text cannot be empty."):
            self.agent.ingest_user_flow("   \n\t   ")

    def test_ingest_multiline_flow(self):
        raw_text = """
        First line of flow.
        Second line, with   extra spaces.
        Third line.
        """
        # Current behavior: \s+ collapses all whitespace including newlines into single spaces.
        expected_text = "First line of flow. Second line, with extra spaces. Third line."
        processed_text = self.agent.ingest_user_flow(raw_text)
        self.assertEqual(processed_text, expected_text)

    def test_ingest_leading_trailing_newlines_and_tabs(self):
        raw_text = "\n\t  Start of text. \t Middle. \n End of text.  \t\n"
        expected_text = "Start of text. Middle. End of text."
        processed_text = self.agent.ingest_user_flow(raw_text)
        self.assertEqual(processed_text, expected_text)

    def test_ingest_flow_with_internal_multiple_spaces(self):
        raw_text = "Word1    Word2  Word3"
        expected_text = "Word1 Word2 Word3"
        processed_text = self.agent.ingest_user_flow(raw_text)
        self.assertEqual(processed_text, expected_text)

if __name__ == '__main__':
    unittest.main()
