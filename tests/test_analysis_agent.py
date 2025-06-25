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
        # The current action extraction is very greedy and might grab long phrases.
        self.assertTrue(any("navigates to the signup page" in action.lower() for action in analysis.get("actions", [])),
                        f"Actions found: {analysis.get('actions')}")
        self.assertTrue(any("system validates the input" in action.lower() for action in analysis.get("actions", [])),
                        f"Actions found: {analysis.get('actions')}")
        self.assertIn("Signup page", analysis.get("screens_pages", []))


    def test_analyze_empty_flow_raises_error(self):
        with self.assertRaisesRegex(ValueError, "Cleaned flow text cannot be empty for analysis."):
            self.agent.analyze_flow("")

    def test_analyze_vague_flow_produces_empty_results_gracefully(self):
        cleaned_flow = "Something happens. Then something else."
        # Expect default actor or empty lists, not errors.
        analysis = self.agent.analyze_flow(cleaned_flow)

        self.assertIn("actors", analysis)
        # Depending on current logic, "GenericActor" might be added if no specific keywords are found.
        # Or it might be empty if no "user" keyword is present and no other actors identified.
        # Let's check for the presence of the key and that it's a list.
        self.assertIsInstance(analysis["actors"], list)
        if not analysis["actors"]: # if list is empty
             pass # This is acceptable
        elif analysis["actors"] == ["Genericactor"]: # Current default when nothing else is found
            pass
        else: # If it finds unexpected actors
            self.fail(f"Expected empty or default actor, got {analysis['actors']}")


        self.assertIn("actions", analysis)
        self.assertEqual(analysis["actions"], [], f"Expected no actions, got {analysis['actions']}")

        self.assertIn("screens_pages", analysis)
        self.assertEqual(analysis["screens_pages"], [], f"Expected no screens, got {analysis['screens_pages']}")

    def test_analyze_more_complex_sentences(self):
        # This test will highlight the brittleness of the current regex approach.
        cleaned_flow = ("The primary User, upon successful authentication provided by the System, "
                        "is immediately redirected to their personalized dashboard page, where "
                        "a list of recent activities is displayed by the aforementioned System.")
        analysis = self.agent.analyze_flow(cleaned_flow)

        self.assertIn("User", analysis["actors"])
        self.assertIn("System", analysis["actors"])

        # Actions will be very dependent on the naive keyword matching.
        # e.g., "redirected to their personalized dashboard page"
        # e.g., "displayed by the aforementioned System"
        self.assertTrue(len(analysis["actions"]) > 0, "Expected some actions to be identified.")
        self.assertTrue(any("redirected to their personalized dashboard page" in action.lower() for action in analysis["actions"]))

        self.assertIn("Dashboard page", analysis["screens_pages"])


if __name__ == '__main__':
    unittest.main()
