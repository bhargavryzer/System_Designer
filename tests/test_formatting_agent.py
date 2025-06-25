import unittest
from app_designer.agents.formatting_agent import OutputFormattingAgent

class TestOutputFormattingAgent(unittest.TestCase):

    def setUp(self):
        self.agent = OutputFormattingAgent()
        self.sample_design_components = {
            "suggested_services": [{"name": "UserService", "description": "Manages users."}],
            "api_endpoints": [{"method": "GET", "path": "/users", "description": "Lists users."}],
            "database_tables": [{"name": "users", "columns": ["id", "name"], "relations": []}],
            "technology_suggestions": ["Python"],
            "security_notes": ["Validate input."]
        }

    def test_format_full_design(self):
        formatted_text = self.agent.format_design(self.sample_design_components)

        self.assertIn("# Generated System Design", formatted_text)
        self.assertIn("## 1. Suggested Services/Modules", formatted_text)
        self.assertIn("- **UserService**: Manages users.", formatted_text)
        self.assertIn("## 2. API Endpoints", formatted_text)
        self.assertIn("| GET    | `/users` | Lists users. |", formatted_text) # Check table format
        self.assertIn("## 3. Database Tables", formatted_text)
        self.assertIn("### Table: users", formatted_text)
        self.assertIn("- **Columns**: `id`, `name`", formatted_text)
        self.assertIn("## 4. Technology Suggestions", formatted_text)
        self.assertIn("- Python", formatted_text)
        self.assertIn("## 5. Security Notes", formatted_text)
        self.assertIn("- Validate input.", formatted_text)
        self.assertIn("Diagram Hints", formatted_text) # Check if diagram hints section is rendered

    def test_format_individual_design_with_mixed_lld(self):
        """Test _format_individual_design with some LLD details present and some absent."""
        mixed_lld_data = {
            "suggested_services": [
                {"name": "UserService", "description": "Manages users.", "lld_details": {"key_methods": [{"name": "register", "params": ["data"], "returns": "user"}]}},
                {"name": "OrderService", "description": "Manages orders."} # No LLD here
            ],
            "api_endpoints": [
                {"method": "POST", "path": "/users", "description": "Create user.", "lld_details": {"request_body_schema": {"type": "object"}}},
                {"method": "GET", "path": "/orders", "description": "List orders."} # No LLD here
            ],
             "database_tables": [
                {"name": "users", "lld_details": {"column_details": [{"name": "id", "type": "uuid"}]}},
                {"name": "orders" } # No LLD here, no 'columns' key either
            ]
        }
        # We call _format_individual_design directly for this test, though it's a protected member.
        # This is for focused testing of its rendering logic.
        formatted_parts = self.agent._format_individual_design(mixed_lld_data, "Test Mixed LLD Design")
        formatted_text = "\n".join(formatted_parts)

        self.assertIn("UserService", formatted_text)
        self.assertIn("Key Methods (Conceptual):", formatted_text) # LLD for UserService
        self.assertIn("OrderService", formatted_text)
        self.assertNotIn("Key Methods (Conceptual):", formatted_text.split("OrderService")[1]) # No LLD for OrderService

        self.assertIn("POST /users", formatted_text)
        self.assertIn("Request Body Schema (Example):", formatted_text) # LLD for /users
        self.assertIn("GET /orders", formatted_text)
        # Check that "Request Body Schema" does not appear after "/orders"
        self.assertNotIn("Request Body Schema (Example):", formatted_text.split("GET /orders")[1].split("Table:")[0])


        self.assertIn("Table: `users`", formatted_text)
        self.assertIn("Columns (Detailed):", formatted_text) # LLD for users table
        self.assertIn("Table: `orders`", formatted_text)
        # For orders table, it should fallback or show minimal info, not "Columns (Detailed):"
        self.assertNotIn("Columns (Detailed):", formatted_text.split("Table: `orders`")[1])
        self.assertIn("_No specific components detailed for this design stage._", formatted_text.split("Table: `orders`")[1])


    def test_format_design_report_with_missing_conceptual_sections(self):
        """Test main format_design with some advanced conceptual reports missing."""
        partial_report_data = {
            "cleaned_user_flow": "User does X.",
            "user_flow_analysis": {"actors": ["User"]},
            "initial_system_design": {"suggested_services": [{"name": "XService"}]},
            # design_analysis_report is missing
            "design_review_summary": {"review_summary": "Review based on initial design only."},
            # simulation_report is missing
            "final_system_design": {"suggested_services": [{"name": "XServiceRefined"}]},
            "architect_review_summary": "Final thoughts on XServiceRefined."
        }
        formatted_text = self.agent.format_design(partial_report_data)

        self.assertIn("XService", formatted_text)
        self.assertIn("Review based on initial design only.", formatted_text)
        self.assertIn("XServiceRefined", formatted_text)
        self.assertIn("Final thoughts on XServiceRefined.", formatted_text)

        # Check that sections for missing reports are handled gracefully (e.g., show a placeholder or are omitted)
        # The current OutputFormattingAgent omits sections if their top-level key is missing in full_report_data
        self.assertNotIn("AI Design Analysis Report (Conceptual)", formatted_text) # Section title for design_analysis_report
        self.assertNotIn("AI Simulation & Test Report (Conceptual)", formatted_text) # Section title for simulation_report


    def test_format_empty_design_data_for_main_method(self): # Renamed for clarity
        formatted_text = self.agent.format_design({}) # Main method call
        self.assertIn("No data available to generate a report.", formatted_text)

    def test_format_error_report_for_main_method(self): # Renamed for clarity
        error_components = {
            "error": "Test Error",
            "details": "Something went wrong.",
            "raw_response": "Raw AI output causing error."
        }
        formatted_text = self.agent.format_design(error_components)
        self.assertIn("# System Design Generation Error", formatted_text)
        self.assertIn("**Error:** Test Error", formatted_text)
        self.assertIn("**Details:** Something went wrong.", formatted_text)
        self.assertIn("Raw AI output causing error.", formatted_text)

if __name__ == '__main__':
    unittest.main()
