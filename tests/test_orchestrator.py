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

        # Assertions
        mock_ingestion_agent.ingest_user_flow.assert_called_once_with(self.sample_flow_text)
        mock_analysis_agent.analyze_flow.assert_called_once_with("cleaned text")
        mock_generation_agent.generate_design_components.assert_called_once_with({"analysis_key": "analysis_value"})
        mock_formatting_agent.format_design.assert_called_once_with({"design_key": "design_value"})
        self.assertEqual(result, "formatted design")

    @patch.dict(os.environ, {"GEMINI_API_KEY": ""}) # Ensure no real key is picked up
    def test_orchestrator_ingestion_failure(self):
        orchestrator = Orchestrator(gemini_api_key="TEST_DUMMY_KEY") # Force simulation
        # Mock the ingestion agent to simulate failure
        with patch.object(orchestrator.ingestion_agent, 'ingest_user_flow', return_value="") as mock_ingest:
            result = orchestrator.generate_system_design("some flow")
            self.assertIn("Error: Ingestion failed", result)
            mock_ingest.assert_called_once()

    @patch.dict(os.environ, {"GEMINI_API_KEY": ""})
    def test_orchestrator_analysis_failure(self):
        orchestrator = Orchestrator(gemini_api_key="TEST_DUMMY_KEY")
        with patch.object(orchestrator.ingestion_agent, 'ingest_user_flow', return_value="cleaned text"), \
             patch.object(orchestrator.analysis_agent, 'analyze_flow', return_value={}) as mock_analyze: # Empty dict
            result = orchestrator.generate_system_design("some flow")
            self.assertIn("Error: Analysis failed", result) # Check if analysis_output is empty
            mock_analyze.assert_called_once()

    @patch.dict(os.environ, {"GEMINI_API_KEY": ""})
    def test_orchestrator_generation_failure_error_dict(self):
        orchestrator = Orchestrator(gemini_api_key="TEST_DUMMY_KEY")
        error_response = {"error": "Generation Failed", "details": "AI model exploded"}
        with patch.object(orchestrator.ingestion_agent, 'ingest_user_flow', return_value="cleaned text"), \
             patch.object(orchestrator.analysis_agent, 'analyze_flow', return_value={"key": "val"}), \
             patch.object(orchestrator.generation_agent, 'generate_design_components', return_value=error_response) as mock_generate:
            result = orchestrator.generate_system_design("some flow")
            self.assertIn("System Design Generation Error", result)
            self.assertIn("Error: Generation Failed", result)
            self.assertIn("Details: AI model exploded", result)
            mock_generate.assert_called_once()

    # Need to import os for @patch.dict(os.environ, ...)
    def setUpModule(): # Changed from staticmethod to setUpModule for clarity on when it runs
        global os
        import os


if __name__ == '__main__':
    unittest.main()
