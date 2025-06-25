import json
import os
import logging

# Attempt to import Google Generative AI; proceed if not found for simulation
try:
    import google.generativeai as genai
except ImportError:
    genai = None
    logging.warning("SystemDesignGenerationAgent: 'google.generativeai' not found. Gemini calls will be fully simulated.")


logger = logging.getLogger(__name__)

class SystemDesignGenerationAgent:
    """
    Agent responsible for generating system design components based on the
    analyzed user flow, using Google Gemini API.
    """
    def __init__(self, api_key: str, model_name: str = "gemini-pro"):
        self.api_key = api_key
        self.model_name = model_name
        self.gemini_model = None

        if not genai:
            logger.warning("Google Generative AI SDK (google.generativeai) is not installed. "
                           "This agent will operate in simulation mode.")
        elif not self.api_key or self.api_key == "DUMMY_API_KEY":
            logger.warning("GEMINI_API_KEY is not provided or is a dummy key. "
                           "This agent will operate in simulation mode.")
        else:
            try:
                genai.configure(api_key=self.api_key)
                self.gemini_model = genai.GenerativeModel(self.model_name)
                logger.info(f"SystemDesignGenerationAgent initialized with Gemini model '{self.model_name}'.")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini model: {e}. Operating in simulation mode.", exc_info=True)
                self.gemini_model = None # Ensure fallback to simulation

    def _make_gemini_api_call(self, prompt: str) -> str:
        """
        Makes an actual call to the Gemini API.
        """
        if not self.gemini_model:
            logger.warning("Gemini model not available. Falling back to simulation for API call.")
            # Construct a context for simulation based on the prompt structure
            # This is a rough approximation
            sim_context = "Context derived from prompt for simulation: "
            if "User Flow Summary:" in prompt:
                sim_context += "user flow processing. "
            if "registration" in prompt.lower():
                sim_context += "registration. "
            if "order" in prompt.lower():
                sim_context += "order processing. "
            return self._simulate_gemini_response(prompt, sim_context)

        try:
            logger.info(f"Making API call to Gemini model '{self.model_name}'...")
            # Example generation config (can be expanded)
            # generation_config = genai.types.GenerationConfig(
            #     candidate_count=1,
            #     temperature=0.7, # Adjust for creativity vs. determinism
            #     # response_mime_type="application/json" # If supported and desired
            # )
            # response = self.gemini_model.generate_content(prompt, generation_config=generation_config)

            # For now, assuming the model is configured for text response.
            # If Gemini Pro Vision is used, parts would be different.
            # Ensure the prompt asks for JSON output if that's what you want to parse.
            response = self.gemini_model.generate_content(prompt)

            # Ensure `response.text` is accessed correctly after checking for parts and errors
            if response.parts:
                # Assuming text is the primary content type we expect
                # You might need to iterate through parts if multiple types are returned
                # or if the model is multi-modal.
                # For simple text models, response.text should be sufficient.
                # However, the new API might structure it in response.parts[0].text
                # Checking response.text first as it's simpler if available directly.
                if hasattr(response, 'text') and response.text:
                    logger.info("Successfully received response from Gemini API.")
                    return response.text
                elif response.parts[0].text:
                     logger.info("Successfully received response from Gemini API (from parts).")
                     return response.parts[0].text
                else:
                    logger.error("Gemini API response received, but no text content found.")
                    raise ValueError("No text content in Gemini response")
            else: # Handle cases where the response might be blocked or have no content
                logger.error(f"Gemini API call failed or returned no parts. Response: {response}")
                # You might want to inspect response.prompt_feedback for blocking reasons
                if response.prompt_feedback:
                     logger.error(f"Prompt Feedback: {response.prompt_feedback}")
                raise genai.types.BlockedPromptException(f"Prompt was blocked or API returned no content. Feedback: {response.prompt_feedback}")


        except Exception as e:
            logger.error(f"Error during Gemini API call: {e}", exc_info=True)
            # Fallback to simulation or raise the error
            # For production, you might want more sophisticated retry logic here.
            # For now, let's re-raise to make it clear an error occurred.
            raise  # Re-raise the exception to be handled by the orchestrator

    def _simulate_gemini_response(self, prompt_text: str, context_for_simulation: str) -> str:
        """
        Simulates a call to Gemini AI for when the API is not available or not configured.
        This is the original simulation logic, adapted slightly.
        """
        logger.info(f"--- Simulating Gemini Call (API not available/configured) ---")
        logger.info(f"Simulated Context: {context_for_simulation}")
        logger.info(f"Simulated Prompt (first 100 chars): {prompt_text[:100]}...")

        mock_response_data = {
            "suggested_services": [],
            "api_endpoints": [],
            "database_tables": [],
            "technology_suggestions": [],
        "security_notes": ["Ensure input validation on all API endpoints.", "Use parameterized queries for database interactions."],
        "diagram_hints": [] # Placeholder for future diagram-related data
        }

        # FUTURE ENHANCEMENT for Language Agnosticism & Diagrams:
        # To be truly language-agnostic, this agent would first generate a more abstract
        # internal representation of the system (e.g., using a formal modeling language or a rich,
        # language-neutral schema). Subsequent agents would then translate this abstract model
        # into language-specific recommendations.
        #
        # For diagrams, this agent could also identify:
        # - Key entities and their relationships for ERDs.
        # - Services/components and their dependencies for component/C4 diagrams.
        # - Sequence of API calls for sequence diagrams.
        # This data would be passed to a dedicated DiagramGenerationAgent.
        # Example: diagram_hints: [{"type": "component", "nodes": ["UserService", "DB"], "edges": [("UserService", "DB", "reads/writes")]}]

        if "registration" in context_for_simulation.lower() or "signup" in context_for_simulation.lower():
            mock_response_data["suggested_services"].extend([
                {"name": "UserService", "description": "Manages user lifecycle: registration, authentication, profile."},
                {"name": "NotificationService", "description": "Handles sending emails (e.g., confirmation, password reset)."}
            ])
            mock_response_data["api_endpoints"].extend([
                {"method": "POST", "path": "/api/v1/users/register", "description": "Registers a new user."},
                {"method": "POST", "path": "/api/v1/auth/login", "description": "Authenticates an existing user and returns a token."},
                {"method": "GET", "path": "/api/v1/users/confirm-email", "description": "Confirms user's email address using a token."}
            ])
            mock_response_data["database_tables"].extend([
                {"name": "users", "columns": ["id (UUID, PK)", "username (VARCHAR, UNIQUE)", "email (VARCHAR, UNIQUE)", "password_hash (VARCHAR)", "status (VARCHAR, e.g., pending, active)", "created_at (TIMESTAMP)", "updated_at (TIMESTAMP)"], "relations": []},
                {"name": "email_confirmation_tokens", "columns": ["id (UUID, PK)", "user_id (UUID, FK to users.id)", "token (VARCHAR, UNIQUE)", "expires_at (TIMESTAMP)", "created_at (TIMESTAMP)"], "relations": ["users.id"]}
            ])
            mock_response_data["technology_suggestions"] = ["Backend: Python (FastAPI/Django) or Node.js (Express)", "Database: PostgreSQL or MySQL", "Caching: Redis (for tokens, sessions)"]
            mock_response_data["security_notes"].extend(["Store passwords using strong hashing (e.g., Argon2, bcrypt).", "Implement email confirmation.", "Protect against brute-force login attempts."])
        elif "order" in context_for_simulation.lower() or "product" in context_for_simulation.lower():
            # ... (add more simulation rules as needed) ...
            mock_response_data["suggested_services"].append({"name": "OrderService", "description": "Manages product orders and checkout process."})
        else:
            mock_response_data["suggested_services"].append({"name": "GenericAppService", "description": "Handles core application logic based on the provided flow."})
            mock_response_data["api_endpoints"].append({"method": "GET", "path": "/api/v1/items", "description": "Retrieves a list of generic items."})
            mock_response_data["database_tables"].append({"name": "generic_items", "columns": ["id (UUID, PK)", "name (VARCHAR)", "description (TEXT)", "created_at (TIMESTAMP)"], "relations": []})

        return json.dumps(mock_response_data, indent=2)

    def generate_design_components(self, analysis_output: dict) -> dict:
        if not analysis_output or "original_flow" not in analysis_output:
            logger.error("Analysis output is missing or invalid for design generation.")
            raise ValueError("Analysis output is missing or invalid.")

        logger.info(f"Generating design components based on analysis: {str(analysis_output)[:150]}...")

        user_flow_summary = analysis_output.get("original_flow", "")
        actors = analysis_output.get("actors", [])
        actions = analysis_output.get("actions", [])
        screens = analysis_output.get("screens_pages", [])

        # --- Enhanced Prompt for Gemini ---
        # This prompt asks for JSON output directly.
        # Ensure your Gemini model and configuration support this or adapt parsing accordingly.
        prompt = f"""
        Analyze the following user flow and generate a high-level system design.
        The output MUST be a single, valid JSON object. Do not include any text before or after the JSON object.
        The JSON object should have the following top-level keys:
        "suggested_services": An array of objects, each with "name" (string) and "description" (string).
        "api_endpoints": An array of objects, each with "method" (string, e.g., "GET", "POST"), "path" (string, e.g., "/api/v1/users"), and "description" (string).
        "database_tables": An array of objects, each with "name" (string, e.g., "users"), "columns" (array of strings describing columns, e.g., "id (UUID, PK)"), and "relations" (array of strings describing foreign key relationships, e.g., "orders.user_id to users.id").
        "technology_suggestions": An array of strings suggesting technologies (e.g., "Backend: Python (FastAPI)").
        "security_notes": An array of strings highlighting key security considerations.
        "diagram_hints": An array of objects, where each object suggests elements for a diagram (e.g., {{"type": "component_diagram_node", "id": "UserService", "label": "User Service"}, {"type": "component_diagram_edge", "from": "UserService", "to": "Database", "label": "CRUD Users"}}). This is highly conceptual.

        User Flow Context:
        --------------------
        User Flow Summary:
        {user_flow_summary}

        Identified Actors: {', '.join(actors) if actors else 'None'}
        Identified Key Actions/Features: {', '.join(actions) if actions else 'None'}
        Identified Screens/Pages: {', '.join(screens) if screens else 'None'}
        --------------------

        Based on this context, provide the system design as a JSON object.
        # Example of a service object: {{"name": "UserService", "description": "Handles user authentication and profile management.", "lld_details": {{"key_methods": [{{"name": "registerUser", "params": ["userData"], "returns": "UserObject or Error"}}], "core_classes": ["UserValidator", "UserDBAccessor"]}}}}
        # Example of an API endpoint object: {{"method": "POST", "path": "/api/v1/auth/login", "description": "Authenticates a user.", "lld_details": {{"request_body_schema": {{"email": "string", "password": "string"}}, "response_body_example_success": {{"token": "jwt_token_here"}}}}}}
        # Example of a database table object: {{"name": "users", "columns": ["id (UUID, PK)", "email (VARCHAR(255), UNIQUE, NOT NULL)", "password_hash (VARCHAR(255), NOT NULL)"], "relations": [], "lld_details": {{"indexes": ["idx_email_unique ON users (email)"]}}}}
        #
        # For LLD details:
        # - For "suggested_services", add an "lld_details" object with "key_methods" (array of objects with "name", "params" array of strings, "returns" string description) and "core_classes" (array of strings).
        # - For "api_endpoints", add an "lld_details" object with "request_body_schema" (JSON schema or example object), "response_body_example_success" (JSON example), and "response_body_example_error" (JSON example).
        # - For "database_tables", add an "lld_details" object with "column_details" (array of objects, each with "name", "type", "constraints", "description") and "indexes" (array of strings describing indexes).
        # Focus LLD on the most critical 1-2 services and 2-3 API endpoints if the design is large. Prioritize core functionality.
        """

        try:
            if self.gemini_model: # Prioritize real API call if model is available
                logger.info("Attempting to use configured Gemini API.")
                gemini_response_str = self._make_gemini_api_call(prompt)
            else: # Fallback to simulation if no real API or model
                logger.info("No Gemini API model configured or available, using simulation.")
                # Pass a context string to the simulation that helps it pick a relevant mock
                sim_context = f"User flow: {user_flow_summary.lower()}"
                gemini_response_str = self._simulate_gemini_response(prompt, sim_context)

            generated_design = json.loads(gemini_response_str)
            logger.info("Successfully parsed design components from Gemini response/simulation.")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response from Gemini/simulation: {e}. Response string: '{gemini_response_str}'", exc_info=True)
            return {"error": "Failed to parse design from AI response", "details": str(e), "raw_response": gemini_response_str}
        except Exception as e: # Catch other errors from API call or simulation
            logger.error(f"An unexpected error occurred in generate_design_components: {e}", exc_info=True)
            return {"error": "An unexpected error occurred during design generation", "details": str(e)}

        return generated_design

if __name__ == '__main__':
    # Basic logging setup for standalone execution
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Example Usage
    # To test with actual Gemini, set your GEMINI_API_KEY environment variable
    # and ensure 'google.generativeai' is installed.
    api_key_to_test = os.getenv("GEMINI_API_KEY", "DUMMY_API_KEY")

    generation_agent = SystemDesignGenerationAgent(api_key=api_key_to_test)

    sample_analysis = {
        "actors": ["User", "System"],
        "actions": [
            "User navigates to the signup page",
            "User enters email, password, and username",
            "System validates the input",
            "System creates a new user account",
            "System sends a confirmation email"
        ],
        "screens_pages": ["Signup page", "Login page", "Dashboard"],
        "original_flow": "User Registration Flow: 1. User navigates to the signup page. 2. User enters email, password, and username. 3. System validates the input. If valid, creates a new user account. 4. System sends a confirmation email. 5. User is redirected to the login page or dashboard."
    }

    logger.info("--- Testing with User Registration Flow ---")
    design_components = generation_agent.generate_design_components(sample_analysis)
    print("\nGenerated Design Components (Registration Flow):")
    print(json.dumps(design_components, indent=2))

    sample_analysis_order = {
        "actors": ["Customer", "System"],
        "actions": ["Customer logs in", "System verifies credentials", "Customer views order history", "Customer clicks on an order"],
        "screens_pages": ["Order history page"],
        "original_flow": "Customer logs in with username and password. System verifies credentials. Customer views the order history page. Customer clicks on an order to see details for an e-commerce site."
    }
    logger.info("\n--- Testing with Order Flow ---")
    design_components_order = generation_agent.generate_design_components(sample_analysis_order)
    print("\nGenerated Design Components (Order Flow):")
    print(json.dumps(design_components_order, indent=2))

    # Test case for when analysis is empty or invalid
    logger.info("\n--- Testing with Invalid Analysis Input ---")
    try:
        generation_agent.generate_design_components({})
    except ValueError as e:
        print(f"Caught expected error for invalid input: {e}")

    # Test case for JSON parsing error (if simulation was faulty or API returned non-JSON)
    # This requires modifying _simulate_gemini_response to return bad JSON, or if the API call fails that way
    # For now, we assume the simulation returns valid JSON.
    # If the real API returns non-JSON, the error handling should catch it.
    logger.info("\n--- End of Standalone Test ---")
