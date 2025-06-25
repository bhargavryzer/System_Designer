import unittest
from unittest.mock import patch, MagicMock
from app_designer.orchestrator import Orchestrator

class TestOrchestrator(unittest.TestCase):

    def setUp(self):
        # Orchestrator will try to load API key from env by default.
        # For most tests, we want to ensure it runs in simulation or with mocks.
        self.sample_flow_text = "User does something. System responds."

    @patch('app_designer.orchestrator.UserFlowIngestionAgent')
    @patch('app_designer.orchestrator.UserFlowAnalysisAgent')
    @patch('app_designer.orchestrator.SystemDesignGenerationAgent')
    @patch('app_designer.orchestrator.OutputFormattingAgent')
    def test_generate_system_design_happy_path(
        self,
        MockOutputFormattingAgent,
        MockSystemDesignGenerationAgent,
        MockUserFlowAnalysisAgent,
        MockUserFlowIngestionAgent
    ):
        # Setup mock instances and their return values
        mock_ingestion_agent = MockUserFlowIngestionAgent.return_value
        mock_ingestion_agent.ingest_user_flow.return_value = "cleaned text"

        mock_analysis_agent = MockUserFlowAnalysisAgent.return_value
        mock_analysis_agent.analyze_flow.return_value = {"analysis_key": "analysis_value"}

        mock_generation_agent = MockSystemDesignGenerationAgent.return_value
        mock_generation_agent.generate_design_components.return_value = {"design_key": "design_value"}

        mock_formatting_agent = MockOutputFormattingAgent.return_value
        mock_formatting_agent.format_design.return_value = "formatted design"

        # Instantiate orchestrator (it will use the mocked agents)
        # Pass a dummy key to ensure it doesn't complain if env var is not set during test
        orchestrator = Orchestrator(gemini_api_key="TEST_DUMMY_KEY")

        result = orchestrator.generate_system_design(self.sample_flow_text)

        # Assertions for happy path (extensive checks on what's passed to formatting_agent)
        mock_ingestion_agent.ingest_user_flow.assert_called_once_with(self.sample_flow_text)
        mock_analysis_agent.analyze_flow.assert_called_once_with("cleaned text")
        mock_generation_agent.generate_design_components.assert_called_once_with({"analysis_key": "analysis_value"})

        # Check calls to new conceptual agents
        MockSystemDesignGenerationAgent.return_value.generate_design_components.assert_called_once() # initial design
        MockDesignAnalysisAgent.return_value.analyze_design.assert_called_once()
        MockDesignReviewAgent.return_value.review_design.assert_called_once()
        MockSimulationAndTestGenerationAgent.return_value.simulate_and_test.assert_called_once()
        MockRedesignAgent.return_value.redesign_system.assert_called_once()

        # Check that the final call to formatting_agent receives a comprehensive dict
        call_args_to_formatter = MockOutputFormattingAgent.return_value.format_design.call_args[0][0]
        self.assertIsInstance(call_args_to_formatter, dict)
        self.assertIn("cleaned_user_flow", call_args_to_formatter)
        self.assertIn("user_flow_analysis", call_args_to_formatter)
        self.assertIn("initial_system_design", call_args_to_formatter)
        self.assertIn("design_analysis_report", call_args_to_formatter)
        self.assertIn("design_review_summary", call_args_to_formatter)
        self.assertIn("simulation_report", call_args_to_formatter)
        self.assertIn("final_system_design", call_args_to_formatter)
        self.assertIn("architect_review_summary", call_args_to_formatter) # Check for placeholder

        self.assertEqual(result, "formatted design")

    @patch.dict(os.environ, {"GEMINI_API_KEY": ""}) # Ensure no real key is picked up
    def test_orchestrator_ingestion_failure(self):
        orchestrator = Orchestrator(gemini_api_key="TEST_DUMMY_KEY_SIM") # Force simulation
        with patch.object(orchestrator.ingestion_agent, 'ingest_user_flow', side_effect=ValueError("Ingestion crash")) as mock_ingest_crash:
            result = orchestrator.generate_system_design("some flow")
            self.assertIn("Error in processing: Ingestion crash", result)
            mock_ingest_crash.assert_called_once()

    @patch.dict(os.environ, {"GEMINI_API_KEY": ""})
    def test_orchestrator_user_flow_analysis_returns_empty(self):
        """Test when user flow analysis returns an empty dict (treated as failure by orchestrator)."""
        orchestrator = Orchestrator(gemini_api_key="TEST_DUMMY_KEY_SIM")
        # Mock .ingestion_agent directly on the instance
        orchestrator.ingestion_agent = MagicMock()
        orchestrator.ingestion_agent.ingest_user_flow.return_value = "cleaned text"

        # Mock .user_flow_analysis_agent directly on the instance
        orchestrator.user_flow_analysis_agent = MagicMock()
        orchestrator.user_flow_analysis_agent.analyze_flow.return_value = {} # Empty dict

        # Mock formatting_agent to inspect what it receives or to simplify test
        orchestrator.formatting_agent = MagicMock()
        orchestrator.formatting_agent.format_design.return_value = "formatted error from analysis failure"

        result = orchestrator.generate_system_design("some flow")

        orchestrator.user_flow_analysis_agent.analyze_flow.assert_called_once_with("cleaned text")
        # The orchestrator's current logic returns a generic "Error: User Flow Analysis failed"
        # which is then formatted by the formatting_agent.
        # We check if format_design was called with an error structure.
        args_to_formatter = orchestrator.formatting_agent.format_design.call_args[0][0]
        self.assertIn("error", args_to_formatter)
        self.assertEqual(args_to_formatter["error"], "User Flow Analysis failed")
        self.assertEqual(result, "formatted error from analysis failure")


    @patch.dict(os.environ, {"GEMINI_API_KEY": ""})
    def test_orchestrator_initial_generation_returns_error_dict(self):
        orchestrator = Orchestrator(gemini_api_key="TEST_DUMMY_KEY_SIM")
        error_response = {"error": "Initial Generation Failed", "details": "AI model for initial design exploded"}

        # Mock previous agents
        orchestrator.ingestion_agent = MagicMock()
        orchestrator.ingestion_agent.ingest_user_flow.return_value = "cleaned text"
        orchestrator.user_flow_analysis_agent = MagicMock()
        orchestrator.user_flow_analysis_agent.analyze_flow.return_value = {"key": "val"}

        # Mock the failing agent
        orchestrator.initial_design_generation_agent = MagicMock()
        orchestrator.initial_design_generation_agent.generate_design_components.return_value = error_response

        # Mock formatting agent
        orchestrator.formatting_agent = MagicMock()
        orchestrator.formatting_agent.format_design.return_value = "formatted initial generation error"

        result = orchestrator.generate_system_design("some flow")

        orchestrator.initial_design_generation_agent.generate_design_components.assert_called_once()
        # Orchestrator should pass this error dict to the formatter
        args_to_formatter = orchestrator.formatting_agent.format_design.call_args[0][0]
        self.assertEqual(args_to_formatter, error_response)
        self.assertEqual(result, "formatted initial generation error")

    @patch.dict(os.environ, {"GEMINI_API_KEY": ""})
    def test_orchestrator_conceptual_design_analysis_agent_returns_error(self):
        """Test when a conceptual agent (DesignAnalysisAgent) returns an error."""
        orchestrator = Orchestrator(gemini_api_key="TEST_DUMMY_KEY_SIM")

        # Mock successful prior steps
        orchestrator.ingestion_agent = MagicMock()
        orchestrator.ingestion_agent.ingest_user_flow.return_value = "cleaned_text"
        orchestrator.user_flow_analysis_agent = MagicMock()
        orchestrator.user_flow_analysis_agent.analyze_flow.return_value = {"user_flow_analysis_data": True}
        orchestrator.initial_design_generation_agent = MagicMock()
        initial_design_mock = {"initial_system_design_data": True, "diagram_hints":[]} # ensure diagram_hints for architect review placeholder
        orchestrator.initial_design_generation_agent.generate_design_components.return_value = initial_design_mock

        # Mock DesignAnalysisAgent to return an error
        orchestrator.design_analysis_agent = MagicMock()
        design_analysis_error = {"error": "AI Design Analysis Failed", "details": "Conceptual analysis AI hiccuped."}
        orchestrator.design_analysis_agent.analyze_design.return_value = design_analysis_error

        # Mock subsequent conceptual agents (they might not be called if logic stops early, but good practice)
        orchestrator.design_review_agent = MagicMock()
        orchestrator.simulation_agent = MagicMock()
        orchestrator.redesign_agent = MagicMock()
        # Mock the RedesignAgent to return something that's not an error for the architect_review_summary placeholder logic
        orchestrator.redesign_agent.redesign_system.return_value = {"final_system_design_data": True, "diagram_hints":[]}


        # Mock formatting agent to inspect what it receives
        orchestrator.formatting_agent = MagicMock()
        orchestrator.formatting_agent.format_design.return_value = "formatted report with design analysis error"

        result = orchestrator.generate_system_design("some flow")

        orchestrator.design_analysis_agent.analyze_design.assert_called_once_with(initial_design_mock, {"user_flow_analysis_data": True})

        # The orchestrator should continue and include this error in full_report_data
        args_to_formatter = orchestrator.formatting_agent.format_design.call_args[0][0]
        self.assertIn("design_analysis_report", args_to_formatter)
        self.assertEqual(args_to_formatter["design_analysis_report"], design_analysis_error)
        # Ensure subsequent conceptual stages still have their mock data (or would be called)
        self.assertTrue(orchestrator.design_review_agent.review_design.called)
        self.assertTrue(orchestrator.simulation_agent.simulate_and_test.called)
        self.assertTrue(orchestrator.redesign_agent.redesign_system.called)

        self.assertEqual(result, "formatted report with design analysis error")


    # Need to import os for @patch.dict(os.environ, ...)
    # Also, ensure all mocked agents are imported if not using string paths in patch
    @classmethod
    def setUpClass(cls): # Changed from setUpModule to setUpClass for unittest structure
        global os
        import os
        # This is to ensure genai.types.BlockedPromptException can be referenced if genai is None
        # However, this setup is more for the generation_agent tests.
        # For orchestrator, direct mocking of agent methods is more common.
        try:
            import google.generativeai as genai
            if not hasattr(genai, 'types'): # Polyfill if types is not a direct attribute
                class MockTypes:
                    class BlockedPromptException(Exception): pass
                    class HarmBlockThreshold: BLOCK_REASON_SAFETY = "SAFETY" # Dummy value
                genai.types = MockTypes()
            elif not hasattr(genai.types, 'BlockedPromptException'):
                 class BlockedPromptException(Exception): pass
                 genai.types.BlockedPromptException = BlockedPromptException
                 if not hasattr(genai.types, 'HarmBlockThreshold'):
                    class HarmBlockThreshold: BLOCK_REASON_SAFETY = "SAFETY"
                    genai.types.HarmBlockThreshold = HarmBlockThreshold

        except ImportError:
            # Mock genai and its specific types if not installed
            mock_genai = MagicMock()
            class MockTypes:
                class BlockedPromptException(Exception): pass
                class HarmBlockThreshold: BLOCK_REASON_SAFETY = "SAFETY"
            mock_genai.types = MockTypes()
            mock_genai.GenerativeModel = MagicMock()
            mock_genai.configure = MagicMock()
            # This is a common pattern to inject a mock if a module is missing for tests
            # sys.modules['google.generativeai'] = mock_genai
            # For this test file, it's less critical as we mock agent methods directly.
            pass


if __name__ == '__main__':
    unittest.main()


if __name__ == '__main__':
    unittest.main()
