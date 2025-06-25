import json

class SystemDesignGenerationAgent:
    """
    Agent responsible for generating system design components based on the
    analyzed user flow, simulating calls to a Generative AI like Gemini.
    """
    def __init__(self, gemini_api_key: str = "DUMMY_API_KEY"):
        # In a real scenario, this would initialize the Gemini client
        self.gemini_api_key = gemini_api_key
        if self.gemini_api_key == "DUMMY_API_KEY":
            print("SystemDesignGenerationAgent: Initialized with a DUMMY_API_KEY. Gemini calls will be simulated.")
        # self.gemini_model = GenerativeModel("gemini-pro") # Or similar initialization

    def _simulate_gemini_call(self, prompt: str, context: str) -> str:
        """
        Simulates a call to Gemini AI.
        In a real implementation, this would make an actual API call.
        """
        print(f"\nSystemDesignGenerationAgent: --- Simulating Gemini Call ---")
        print(f"Context: {context}")
        print(f"Prompt: {prompt}")
        print(f"-----------------------------------\n")

        # Mock responses based on keywords in the prompt or context
        # This is highly simplified for demonstration.
        mock_response = {
            "suggested_services": [],
            "api_endpoints": [],
            "database_tables": [],
            "technology_suggestions": [],
            "security_notes": []
        }

        if "registration" in context.lower() or "signup" in context.lower():
            mock_response["suggested_services"].append({"name": "UserService", "description": "Manages user accounts, registration, login."})
            mock_response["suggested_services"].append({"name": "NotificationService", "description": "Handles sending emails (e.g., confirmation)."})
            mock_response["api_endpoints"].append({"method": "POST", "path": "/users/register", "description": "Registers a new user."})
            mock_response["api_endpoints"].append({"method": "POST", "path": "/auth/login", "description": "Logs in an existing user."})
            mock_response["database_tables"].append({"name": "Users", "columns": ["UserID (PK)", "Email", "PasswordHash", "Username", "CreatedAt"], "relations": []})
            mock_response["database_tables"].append({"name": "EmailConfirmations", "columns": ["ConfirmationID (PK)", "UserID (FK)", "Token", "ExpiresAt"], "relations": ["Users.UserID"]})
            mock_response["technology_suggestions"] = ["Python (Flask/FastAPI) for backend", "PostgreSQL for database", "React/Vue for frontend"]
            mock_response["security_notes"] = ["Password hashing (bcrypt)", "Email verification", "Input validation for all fields"]
        elif "order" in context.lower() or "product" in context.lower():
            mock_response["suggested_services"].append({"name": "OrderService", "description": "Manages product orders."})
            mock_response["suggested_services"].append({"name": "ProductService", "description": "Manages product catalog."})
            mock_response["api_endpoints"].append({"method": "POST", "path": "/orders", "description": "Creates a new order."})
            mock_response["api_endpoints"].append({"method": "GET", "path": "/products/{product_id}", "description": "Retrieves product details."})
            mock_response["database_tables"].append({"name": "Orders", "columns": ["OrderID (PK)", "UserID (FK)", "OrderDate", "TotalAmount"], "relations": ["Users.UserID"]})
            mock_response["database_tables"].append({"name": "OrderItems", "columns": ["OrderItemID (PK)", "OrderID (FK)", "ProductID (FK)", "Quantity", "Price"], "relations": ["Orders.OrderID", "Products.ProductID"]})
            mock_response["database_tables"].append({"name": "Products", "columns": ["ProductID (PK)", "Name", "Description", "Price"], "relations": []})
        else:
            mock_response["suggested_services"].append({"name": "GenericService", "description": "Handles core application logic based on the flow."})
            mock_response["api_endpoints"].append({"method": "GET", "path": "/generic/items", "description": "Retrieves generic items."})
            mock_response["database_tables"].append({"name": "GenericTable", "columns": ["ID (PK)", "Data"], "relations": []})


        return json.dumps(mock_response, indent=2)

    def generate_design_components(self, analysis_output: dict) -> dict:
        """
        Takes the analyzed flow and generates system design components
        by formulating prompts and (simulating) calling Gemini.
        """
        if not analysis_output or "original_flow" not in analysis_output:
            raise ValueError("Analysis output is missing or invalid.")

        print(f"SystemDesignGenerationAgent: Generating design based on analysis: {str(analysis_output)[:100]}...")

        user_flow_summary = analysis_output.get("original_flow", "")
        actors = analysis_output.get("actors", [])
        actions = analysis_output.get("actions", [])
        screens = analysis_output.get("screens_pages", [])

        # --- Prompt Engineering (Example) ---
        # In a real scenario, this would be much more sophisticated.
        # We might have multiple prompts for different aspects of the design.

        context_for_gemini = f"""
        User Flow Summary:
        {user_flow_summary}

        Identified Actors: {', '.join(actors) if actors else 'None'}
        Identified Actions/Features: {', '.join(actions) if actions else 'None'}
        Identified Screens/Pages: {', '.join(screens) if screens else 'None'}
        """

        main_prompt = f"""
        Based on the provided user flow summary and extracted components, please generate a high-level system design.
        Suggest the following:
        1.  Key microservices or backend modules with a brief description of their responsibilities.
        2.  Potential API endpoints (HTTP method, path, and a brief description).
        3.  Core database tables with essential columns and potential relationships (e.g., UserID (PK), Email, PasswordHash).
        4.  Optionally, suggest a suitable technology stack (e.g., backend language/framework, database type).
        5.  Briefly mention any critical security considerations for this flow.

        Return the output as a JSON object with keys: "suggested_services", "api_endpoints", "database_tables", "technology_suggestions", "security_notes".
        Each service should be an object with "name" and "description".
        Each API endpoint should be an object with "method", "path", and "description".
        Each database table should be an object with "name", "columns" (list of strings), and "relations" (list of strings indicating foreign keys like "OtherTable.OtherColumn").
        """

        # Simulate the Gemini call
        simulated_gemini_response_str = self._simulate_gemini_call(prompt=main_prompt, context=context_for_gemini)

        try:
            generated_design = json.loads(simulated_gemini_response_str)
        except json.JSONDecodeError as e:
            print(f"Error decoding simulated Gemini response: {e}")
            generated_design = {"error": "Failed to parse design from Gemini simulation", "details": str(e)}

        print("SystemDesignGenerationAgent: Design components generated.")
        return generated_design

if __name__ == '__main__':
    # Example Usage
    generation_agent = SystemDesignGenerationAgent() # Uses DUMMY_API_KEY

    # Sample analysis output (normally from UserFlowAnalysisAgent)
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

    design_components = generation_agent.generate_design_components(sample_analysis)
    print("\nGenerated Design Components:")
    print(json.dumps(design_components, indent=2))

    sample_analysis_order = {
        "actors": ["Customer", "System"],
        "actions": ["Customer logs in", "System verifies credentials", "Customer views order history", "Customer clicks on an order"],
        "screens_pages": ["Order history page"],
        "original_flow": "Customer logs in with username and password. System verifies credentials. Customer views the order history page. Customer clicks on an order to see details."
    }
    design_components_order = generation_agent.generate_design_components(sample_analysis_order)
    print("\nGenerated Design Components (Order Flow):")
    print(json.dumps(design_components_order, indent=2))
