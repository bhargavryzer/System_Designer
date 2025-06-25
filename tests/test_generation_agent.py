import unittest
import os
from unittest.mock import patch, MagicMock
from app_designer.agents.generation_agent import SystemDesignGenerationAgent

# Import genai if available for type hinting and potential real checks, otherwise mock it.
try:
    import google.generativeai as genai
except ImportError:
    genai = None


class TestSystemDesignGenerationAgent(unittest.TestCase):

    def setUp(self):
        # Test with a dummy API key by default, relying on simulation
        self.dummy_api_key = "DUMMY_API_KEY_FOR_TESTING"
        self.agent_simulated = SystemDesignGenerationAgent(api_key=self.dummy_api_key)

        self.sample_analysis_output = {
            "actors": ["User", "System"],
            "actions": ["User registers", "System sends email"],
            "screens_pages": ["Registration Page"],
            "original_flow": "User attempts to register. System sends a confirmation email."
        }

    def test_generate_design_components_simulated(self):
        """Test that simulated response works and returns expected structure."""
        result = self.agent_simulated.generate_design_components(self.sample_analysis_output)

        self.assertIn("suggested_services", result)
        self.assertIn("api_endpoints", result)
        self.assertIn("database_tables", result)
        self.assertIsInstance(result["suggested_services"], list)
        # Check if simulation for "registration" or "email" was triggered
        self.assertTrue(any("user" in s["name"].lower() for s in result["suggested_services"]), "UserService or similar expected for registration flow.")
        self.assertTrue(any("notification" in s["name"].lower() or "email" in s["name"].lower() for s in result["suggested_services"]), "NotificationService or similar expected for email action.")


    def test_generate_design_components_invalid_input(self):
        with self.assertRaises(ValueError):
            self.agent_simulated.generate_design_components({}) # Empty analysis
        with self.assertRaises(ValueError):
            self.agent_simulated.generate_design_components({"actors": []}) # Missing original_flow

    @patch.dict(os.environ, {"GEMINI_API_KEY": "REAL_KEY_FOR_MOCK_TEST"})
    @patch('app_designer.agents.generation_agent.genai') # Mock the genai module
    def test_generate_design_components_with_mocked_api(self, mock_genai_module):
        """
        Test the agent assuming a real API key is provided and mocking the genai library.
        """
        if not genai: # If genai is not importable, this kind of test is harder to set up perfectly
            self.skipTest("google.generativeai SDK not available, skipping direct mock test of its usage.")

        # Configure the mock genai module and its classes/methods
        mock_model_instance = MagicMock()

        # Define the mock response structure Gemini API would return
        # This should be a string that can be parsed into JSON, as per the prompt
        mock_api_response_text = """
        {
            "suggested_services": [{"name": "MockedUserService", "description": "Handles user stuff via mock"}],
            "api_endpoints": [{"method": "POST", "path": "/mock/users", "description": "Mocked user creation"}],
            "database_tables": [{"name": "mock_users", "columns": ["id", "email"], "relations": []}],
            "technology_suggestions": ["MockTech"],
            "security_notes": ["Always mock securely."]
        }
        """
        # The generate_content method should return an object that has a 'text' attribute (or parts[0].text)
        mock_response_object = MagicMock()
        mock_response_object.text = mock_api_response_text
        # If your code uses response.parts[0].text:
        # mock_part = MagicMock()
        # mock_part.text = mock_api_response_text
        # mock_response_object.parts = [mock_part]
        # mock_response_object.prompt_feedback = None # To avoid issues with feedback checks

        mock_model_instance.generate_content.return_value = mock_response_object

        # Mock the GenerativeModel class to return our mock_model_instance
        mock_genai_module.GenerativeModel.return_value = mock_model_instance
        # Mock configure if it's called
        mock_genai_module.configure = MagicMock()

        # Create agent instance, it should now use the mocked genai
        agent_with_mocked_api = SystemDesignGenerationAgent(api_key="REAL_KEY_FOR_MOCK_TEST")

        result = agent_with_mocked_api.generate_design_components(self.sample_analysis_output)

        # Assert that the genai.GenerativeModel was called (i.e., API path was attempted)
        mock_genai_module.GenerativeModel.assert_called_once_with("gemini-pro") # or whatever default model
        mock_model_instance.generate_content.assert_called_once() # Check the actual call was made

        self.assertIn("suggested_services", result)
        self.assertEqual(result["suggested_services"][0]["name"], "MockedUserService")
        self.assertNotIn("error", result)


    @patch.dict(os.environ, {"GEMINI_API_KEY": "REAL_KEY_FOR_MOCK_TEST"})
    @patch('app_designer.agents.generation_agent.genai')
    def test_gemini_api_call_failure_json_parsing(self, mock_genai_module):
        if not genai:
            self.skipTest("google.generativeai SDK not available.")

        mock_model_instance = MagicMock()
        mock_response_object = MagicMock()
        mock_response_object.text = "This is not JSON" # Invalid JSON response
        # mock_part = MagicMock(); mock_part.text = "This is not JSON"; mock_response_object.parts = [mock_part]
        # mock_response_object.prompt_feedback = None
        mock_model_instance.generate_content.return_value = mock_response_object
        mock_genai_module.GenerativeModel.return_value = mock_model_instance
        mock_genai_module.configure = MagicMock()

        agent_with_mocked_api = SystemDesignGenerationAgent(api_key="REAL_KEY_FOR_MOCK_TEST")
        result = agent_with_mocked_api.generate_design_components(self.sample_analysis_output)

        self.assertIn("error", result)
        self.assertIn("Failed to parse design from AI response", result["error"])
        self.assertEqual(result["raw_response"], "This is not JSON")

if __name__ == '__main__':
    unittest.main()
