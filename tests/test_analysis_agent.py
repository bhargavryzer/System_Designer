import unittest
from app_designer.agents.analysis_agent import UserFlowAnalysisAgent

class TestUserFlowAnalysisAgent(unittest.TestCase):

    def setUp(self):
        self.agent = UserFlowAnalysisAgent()

    def test_analyze_simple_flow(self):
        cleaned_flow = "User navigates to home page. System displays welcome message."
        # This test is highly dependent on the current naive regex implementation.
        # It would need significant changes if a Gemini-based analysis were implemented.
        analysis = self.agent.analyze_flow(cleaned_flow)

        self.assertIn("User", analysis["actors"])
        self.assertIn("System", analysis["actors"])
        # Check for some action (capitalization and exact phrasing might vary)
        self.assertTrue(any("navigates to home page" in action.lower() for action in analysis["actions"]))
        self.assertTrue(any("displays welcome message" in action.lower() for action in analysis["actions"]))
        self.assertIn("Home page", analysis["screens_pages"]) # Assuming "page" keyword triggers this

    def test_analyze_empty_flow_raises_error(self):
        with self.assertRaises(ValueError):
            self.agent.analyze_flow("")

if __name__ == '__main__':
    unittest.main()
