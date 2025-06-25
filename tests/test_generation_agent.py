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
        # Default model for testing simulation, can be overridden in specific tests
        self.default_model_name = "gemini-pro"
        self.agent_simulated = SystemDesignGenerationAgent(
            api_key=self.dummy_api_key,
            model_name=self.default_model_name
        )

        self.sample_analysis_output_registration = {
            "actors": ["User", "System"],
            "actions": ["User registers", "System sends email confirmation"],
            "screens_pages": ["Registration Page"],
            "original_flow": "User attempts to register. System sends a confirmation email."
        }

    def test_generate_design_components_simulated_registration_flow(self):
        """Test simulated response for a registration flow."""
        result = self.agent_simulated.generate_design_components(self.sample_analysis_output_registration)

        self.assertIn("suggested_services", result)
        self.assertTrue(any("user" in s["name"].lower() for s in result["suggested_services"]),
                        "Expected UserService for registration flow in simulation.")
        self.assertTrue(any("notification" in s["name"].lower() for s in result["suggested_services"]),
                        "Expected NotificationService for email confirmation in simulation.")
        self.assertIn("api_endpoints", result)
        self.assertIn("database_tables", result)
        self.assertIsInstance(result["suggested_services"], list)
        # Check if simulation for "registration" or "email" was triggered
        # No specific check for "email" in service name, as "NotificationService" covers it.

    def test_simulate_gemini_response_order_flow(self):
        """Test _simulate_gemini_response directly for an order flow context."""
        # The generate_design_components method internally calls _simulate_gemini_response
        # when no real API is available. This test focuses on the simulation logic.
        # We need to craft an analysis output that would lead to an "order" context.
        order_analysis_output = {
            "actors": ["Customer", "System"],
            "actions": ["Customer places order", "System processes payment"],
            "screens_pages": ["Checkout Page", "Order Confirmation Page"],
            "original_flow": "Customer places an order for a product. System processes payment and confirms the order."
        }
        # The agent's `generate_design_components` will internally use the original_flow for context.
        result = self.agent_simulated.generate_design_components(order_analysis_output)

        self.assertIn("suggested_services", result)
        self.assertTrue(any("order" in s["name"].lower() for s in result["suggested_services"]),
                        "Expected OrderService for order flow in simulation.")
        self.assertTrue(any("payment" in s["name"].lower() for s in result.get("suggested_services", [])),  # Payment might be separate or part of OrderService
                        "Expected Payment processing hints for order flow in simulation (optional).")

    def test_simulate_gemini_response_generic_flow(self):
        """Test _simulate_gemini_response for a generic flow context."""
        generic_analysis_output = {
            "actors": ["User"],
            "actions": ["User performs a generic task"],
            "screens_pages": ["Generic Page"],
            "original_flow": "A user performs a generic task on a generic page."
        }
        result = self.agent_simulated.generate_design_components(generic_analysis_output)
        self.assertIn("suggested_services", result)
        self.assertTrue(any("generic" in s["name"].lower() for s in result["suggested_services"]),
                        "Expected GenericAppService for a generic flow in simulation.")


    def test_generate_design_components_invalid_input(self):
        with self.assertRaisesRegex(ValueError, "Analysis output is missing or invalid."):
            self.agent_simulated.generate_design_components({}) # Empty analysis
        with self.assertRaisesRegex(ValueError, "Analysis output is missing or invalid."):
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
        agent_with_mocked_api = SystemDesignGenerationAgent(
            api_key="REAL_KEY_FOR_MOCK_TEST",
            model_name=self.default_model_name
        )

        result = agent_with_mocked_api.generate_design_components(self.sample_analysis_output_registration)

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

        agent_with_mocked_api = SystemDesignGenerationAgent(
            api_key="REAL_KEY_FOR_MOCK_TEST",
            model_name=self.default_model_name
            )
        result = agent_with_mocked_api.generate_design_components(self.sample_analysis_output_registration)

        self.assertIn("error", result)
        self.assertIn("Failed to parse design from AI response", result["error"])
        self.assertEqual(result["raw_response"], "This is not JSON")

    @patch.dict(os.environ, {"GEMINI_API_KEY": "REAL_KEY_FOR_MOCK_TEST"})
    @patch('app_designer.agents.generation_agent.genai')
    def test_gemini_api_call_blocked_prompt(self, mock_genai_module):
        if not genai:
            self.skipTest("google.generativeai SDK not available.")

        mock_model_instance = MagicMock()

        # Simulate a BlockedPromptException or similar error
        # The actual exception is genai.types.BlockedPromptException
        # We need to mock the response object to reflect how the SDK signals this
        mock_response_object = MagicMock()
        mock_response_object.parts = [] # No parts typically for blocked prompt
        mock_response_object.text = None
        # Mock prompt_feedback if your code checks it
        mock_prompt_feedback = MagicMock()
        mock_prompt_feedback.block_reason = genai.types.HarmBlockThreshold.BLOCK_REASON_SAFETY # Or other reason
        mock_prompt_feedback.safety_ratings = [] # Example
        mock_response_object.prompt_feedback = mock_prompt_feedback

        # If generate_content itself raises the exception (depends on SDK version nuances)
        # mock_model_instance.generate_content.side_effect = genai.types.BlockedPromptException("Blocked due to safety")
        # For this test, let's assume it returns a response object that indicates blocking via lack of parts/text and prompt_feedback
        mock_model_instance.generate_content.return_value = mock_response_object

        mock_genai_module.GenerativeModel.return_value = mock_model_instance
        mock_genai_module.configure = MagicMock()

        agent_with_mocked_api = SystemDesignGenerationAgent(
            api_key="REAL_KEY_FOR_MOCK_TEST",
            model_name=self.default_model_name
            )
        # We expect the agent's _make_gemini_api_call to catch this and raise,
        # then generate_design_components to return an error dict.
        # If BlockedPromptException is raised and not caught by _make_gemini_api_call to return a string,
        # then generate_design_components's own try-except for Exception e should catch it.

        # Let's refine _make_gemini_api_call in the agent to explicitly handle BlockedPromptException
        # For now, assume it propagates and is caught by the general Exception in generate_design_components

        result = agent_with_mocked_api.generate_design_components(self.sample_analysis_output_registration)

        self.assertIn("error", result)
        self.assertTrue("An unexpected error occurred during design generation" in result["error"] or \
                        "Prompt was blocked" in result.get("details", ""), # if BlockedPromptException is caught and stringified
                        f"Unexpected error message: {result}")


if __name__ == '__main__':
    unittest.main()
