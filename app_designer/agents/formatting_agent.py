import logging

logger = logging.getLogger(__name__)

class OutputFormattingAgent:
    """
    Agent responsible for formatting the generated system design components
    into a human-readable format (e.g., Markdown).
    """
    def __init__(self):
        pass

    def format_design(self, design_components: dict) -> str:
        """
        Formats the structured design components into a Markdown string.
        """
        if not design_components:
            logger.warning("No design components provided to format.")
            return "No design components to format."

        logger.info(f"Formatting design components (keys: {list(design_components.keys())})...")
        logger.debug(f"Full design components for formatting: {str(design_components)[:200]}...") # Log snippet of input

        if "error" in design_components:
            logger.warning(f"Formatting an error report: {design_components['error']}")
            # Error report format is already handled by Orchestrator, but if called directly:
            error_details = design_components.get('details', '')
            raw_response_snippet = str(design_components.get('raw_response', ''))[:200]
            return (f"# System Design Generation Error\n\n"
                    f"**Error:** {design_components['error']}\n"
                    f"**Details:** {error_details}\n"
                    f"**Raw AI Response (snippet):**\n```\n{raw_response_snippet}...\n```\n")

        md_output = ["# Generated System Design\n"]

        # Suggested Services / Modules
        if "suggested_services" in design_components and design_components["suggested_services"]:
            md_output.append("## 1. Suggested Services/Modules\n")
            for service in design_components["suggested_services"]:
                md_output.append(f"- **{service.get('name', 'N/A')}**: {service.get('description', 'No description')}")
            md_output.append("\n")

        # API Endpoints
        if "api_endpoints" in design_components and design_components["api_endpoints"]:
            md_output.append("## 2. API Endpoints\n")
            md_output.append("| Method | Path                      | Description                         |")
            md_output.append("|--------|---------------------------|-------------------------------------|")
            for endpoint in design_components["api_endpoints"]:
                md_output.append(f"| {endpoint.get('method', 'N/A').upper()}  | `{endpoint.get('path', 'N/A')}` | {endpoint.get('description', 'No description')} |")
            md_output.append("\n")

        # Database Tables
        if "database_tables" in design_components and design_components["database_tables"]:
            md_output.append("## 3. Database Tables\n")
            for table in design_components["database_tables"]:
                md_output.append(f"### Table: {table.get('name', 'N/A')}\n")
                md_output.append("- **Columns**: " + ", ".join(f"`{col}`" for col in table.get("columns", [])))
                if table.get("relations"):
                    md_output.append("- **Relations**: " + ", ".join(table.get("relations", [])))
                md_output.append("") # Adds a newline for spacing
            md_output.append("\n")

        # Technology Suggestions
        if "technology_suggestions" in design_components and design_components["technology_suggestions"]:
            md_output.append("## 4. Technology Suggestions\n")
            for tech in design_components["technology_suggestions"]:
                md_output.append(f"- {tech}")
            md_output.append("\n")

        # Security Notes
        if "security_notes" in design_components and design_components["security_notes"]:
            md_output.append("## 5. Security Notes\n")
            for note in design_components["security_notes"]:
                md_output.append(f"- {note}")
            md_output.append("\n")

        if len(md_output) == 1: # Only title was added
            md_output.append("No specific design components were generated.")

        formatted_text = "\n".join(md_output)
        logger.info("Formatting complete.")
        return formatted_text

if __name__ == '__main__':
    # Basic logging setup for standalone execution
    import json # Added import for json.dumps
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Example Usage
    formatting_agent = OutputFormattingAgent()

    # Sample design components (normally from SystemDesignGenerationAgent)
    sample_design = {
        "suggested_services": [
            {"name": "UserService", "description": "Manages user accounts, registration, login."},
            {"name": "NotificationService", "description": "Handles sending emails (e.g., confirmation)."}
        ],
        "api_endpoints": [
            {"method": "POST", "path": "/users/register", "description": "Registers a new user."},
            {"method": "POST", "path": "/auth/login", "description": "Logs in an existing user."}
        ],
        "database_tables": [
            {"name": "Users", "columns": ["UserID (PK)", "Email", "PasswordHash", "Username", "CreatedAt"], "relations": []},
            {"name": "EmailConfirmations", "columns": ["ConfirmationID (PK)", "UserID (FK)", "Token", "ExpiresAt"], "relations": ["Users.UserID"]}
        ],
        "technology_suggestions": ["Python (Flask/FastAPI) for backend", "PostgreSQL for database"],
        "security_notes": ["Password hashing (bcrypt)", "Email verification", "Input validation"]
    }

    logger.info("Testing with sample design components...")
    formatted_output = formatting_agent.format_design(sample_design)
    logger.info(f"Formatted System Design (Markdown):\n{formatted_output}")

    empty_design = {}
    logger.info("Testing with empty design components...")
    formatted_empty = formatting_agent.format_design(empty_design)
    logger.info(f"Formatted Empty Design:\n{formatted_empty}")

    error_design = {
        "error": "Simulated Gemini API failure.",
        "details": "The model returned an unexpected status code.",
        "raw_response": "Some raw error string from AI"
    }
    logger.info("Testing with error design components...")
    formatted_error = formatting_agent.format_design(error_design)
    logger.info(f"Formatted Error Design:\n{formatted_error}")
