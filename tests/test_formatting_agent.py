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

    def test_format_partial_design(self):
        partial_components = {
            "suggested_services": [{"name": "OrderService", "description": "Manages orders."}]
        }
        formatted_text = self.agent.format_design(partial_components)
        self.assertIn("OrderService", formatted_text)
        self.assertNotIn("API Endpoints", formatted_text) # Check that missing sections aren't rendered

    def test_format_empty_design(self):
        formatted_text = self.agent.format_design({})
        self.assertIn("No specific design components were generated.", formatted_text)
        self.assertNotIn("## 1.", formatted_text) # No numbered sections

    def test_format_error_design(self):
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
