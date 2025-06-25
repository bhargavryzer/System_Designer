import logging
import json

logger = logging.getLogger(__name__)

class OutputFormattingAgent:
    """
    Agent responsible for formatting the generated system design components
    and related analysis/review reports into a human-readable format (e.g., Markdown).
    """
    def __init__(self):
        pass

    def _format_individual_design(self, design_data: dict, title: str) -> list[str]:
        """Helper to format a single system design structure."""
        md_section = [f"## {title}\n"]
        if not design_data or "error" in design_data:
            error_info = design_data.get('error', 'Unknown error')
            details = design_data.get('details', 'No details provided.')
            raw_response = design_data.get('raw_response', '')
            md_section.append(f"**Error in this design stage:** {error_info}")
            md_section.append(f"_Details:_ {details}")
            if raw_response:
                md_section.append(f"_Raw AI Response (snippet):_ ```\n{str(raw_response)[:200]}...\n```")
            md_section.append("\n")
            return md_section

        # Suggested Services / Modules
        if "suggested_services" in design_data and design_data["suggested_services"]:
            md_section.append("### Services/Modules\n")
            for service in design_data["suggested_services"]:
                md_section.append(f"- **{service.get('name', 'N/A')}**: {service.get('description', 'No description')}")
            md_section.append("\n")

        # API Endpoints
        if "api_endpoints" in design_data and design_data["api_endpoints"]:
            md_section.append("### API Endpoints\n")
            md_section.append("| Method | Path                      | Description                         |")
            md_section.append("|--------|---------------------------|-------------------------------------|")
            for endpoint in design_data["api_endpoints"]:
                md_section.append(f"| {endpoint.get('method', 'N/A').upper()}  | `{endpoint.get('path', 'N/A')}` | {endpoint.get('description', 'No description')} |")
            md_section.append("\n")

        # Database Tables
        if "database_tables" in design_data and design_data["database_tables"]:
            md_section.append("### Database Tables\n")
            for table in design_data["database_tables"]:
                md_section.append(f"- **Table: {table.get('name', 'N/A')}**")
                md_section.append("  - **Columns**: " + ", ".join(f"`{col}`" for col in table.get("columns", [])))
                if table.get("relations"):
                    md_section.append("  - **Relations**: " + ", ".join(table.get("relations", [])))
                md_section.append("") # Adds a newline for spacing
            md_section.append("\n")

        # Technology Suggestions
        if "technology_suggestions" in design_data and design_data["technology_suggestions"]:
            md_section.append("### Technology Suggestions\n")
            for tech in design_data["technology_suggestions"]:
                md_section.append(f"- {tech}")
            md_section.append("\n")

        # Security Notes
        if "security_notes" in design_data and design_data["security_notes"]:
            md_section.append("### Security Notes\n")
            for note in design_data["security_notes"]:
                md_section.append(f"- {note}")
            md_section.append("\n")

        # Design Rationale Changes (for redesigned system)
        if "design_rationale_changes" in design_data and design_data["design_rationale_changes"]:
            md_section.append("### Key Design Changes and Rationale\n")
            for change_note in design_data["design_rationale_changes"]:
                md_section.append(f"- {change_note}")
            md_section.append("\n")

        if len(md_section) == 1: # Only title was added
             md_section.append("_No specific components detailed for this design stage._\n")
        return md_section

    def format_design(self, full_report_data: dict) -> str:
        """
        Formats the comprehensive report data, including all stages of design
        and analysis, into a single Markdown string.
        """
        if not full_report_data:
            logger.warning("No data provided to format.")
            return "# System Design Report\n\nNo data available to generate a report."

        logger.info(f"Formatting comprehensive report (top-level keys: {list(full_report_data.keys())})...")

        # Handle top-level error from Orchestrator
        if "error" in full_report_data and "initial_system_design" not in full_report_data : # Check if it's an early pipeline error
            return (f"# System Design Generation Error\n\n"
                    f"**Error:** {full_report_data['error']}\n"
                    f"**Details:** {full_report_data.get('details', 'N/A')}\n")

        md_output = ["# Comprehensive AI-Driven System Design Report\n"]

        # 0. User Flow Input (Optional, if included)
        if "cleaned_user_flow" in full_report_data:
            md_output.append("## 0. User Flow Input (Cleaned)\n")
            md_output.append("```text")
            md_output.append(full_report_data["cleaned_user_flow"])
            md_output.append("```\n")

        # 1. User Flow Analysis
        if "user_flow_analysis" in full_report_data:
            md_output.append("## 1. User Flow Analysis (Rule-Based)\n")
            analysis = full_report_data["user_flow_analysis"]
            md_output.append(f"- **Actors**: {', '.join(analysis.get('actors', ['N/A']))}")
            md_output.append(f"- **Key Actions/Features (Sample)**: {', '.join(analysis.get('actions', ['N/A'])[:5])}... ") # Show a sample
            md_output.append(f"- **Screens/Pages**: {', '.join(analysis.get('screens_pages', ['N/A']))}")
            md_output.append("\n")

        # 2. Initial System Design
        if "initial_system_design" in full_report_data:
            md_output.extend(self._format_individual_design(full_report_data["initial_system_design"], "2. Initial System Design (AI Generated)"))

        # 3. AI Design Analysis Report
        if "design_analysis_report" in full_report_data:
            report = full_report_data["design_analysis_report"]
            md_output.append("## 3. AI Design Analysis Report (Conceptual)\n")
            md_output.append(f"**Overall Assessment Score (Mocked):** {report.get('overall_assessment_score', 'N/A')}\n")
            md_output.append(f"**Summary:** {report.get('summary', 'N/A')}\n")
            for key, value in report.items():
                if key not in ["overall_assessment_score", "summary"] and isinstance(value, list) and value:
                    md_output.append(f"### {key.replace('_', ' ').capitalize()}\n")
                    for item in value:
                        md_output.append(f"- {item}")
                    md_output.append("") # newline
            md_output.append("\n")

        # 4. AI Design Review Summary
        if "design_review_summary" in full_report_data:
            review = full_report_data["design_review_summary"]
            md_output.append("## 4. AI Design Review Summary (Conceptual)\n")
            md_output.append(f"**Review Summary:** {review.get('review_summary', 'N/A')}\n")
            if review.get("prioritized_issues"):
                md_output.append("### Prioritized Issues & Redesign Recommendations:\n")
                for issue in review["prioritized_issues"]:
                    md_output.append(f"- **Issue ({issue.get('category', 'N/A')} - {issue.get('issue_id', 'N/A')}):** {issue.get('description', 'N/A')}")
                    md_output.append(f"  - **Recommendation for Redesign:** {issue.get('recommendation_for_redesign', 'N/A')}")
                md_output.append("") # newline
            md_output.append("\n")

        # 5. AI Simulation & Test Report
        if "simulation_report" in full_report_data:
            sim_report = full_report_data["simulation_report"]
            md_output.append("## 5. AI Simulation & Test Report (Conceptual)\n")
            md_output.append(f"**Overall Simulation Notes:** {sim_report.get('overall_simulation_notes', 'N/A')}\n")
            if sim_report.get("conceptual_test_cases"):
                md_output.append("### Conceptual Test Cases (Sample):\n")
                for tc in sim_report["conceptual_test_cases"][:3]: # Show a sample
                    md_output.append(f"- **ID {tc.get('test_id', 'N/A')} ({tc.get('type', 'N/A')}):** {tc.get('description', 'N/A')}")
                    md_output.append(f"  - *Expected Outcome:* {tc.get('expected_outcome', 'N/A')}")
                if len(sim_report["conceptual_test_cases"]) > 3:
                    md_output.append("- ... and more.")
                md_output.append("") # newline
            if sim_report.get("simulation_summary"):
                 md_output.append("### Simulation Highlights (Sample):\n")
                 for ss in sim_report["simulation_summary"][:2]: # Show a sample
                    md_output.append(f"- **For Test ID Ref {ss.get('test_id_ref', 'N/A')}:**")
                    md_output.append(f"  - *Interactions:* {ss.get('simulated_interactions', 'N/A')}")
                    md_output.append(f"  - *Potential Issues:* {ss.get('potential_issues_found', 'N/A')}")
                 if len(sim_report["simulation_summary"]) > 2:
                    md_output.append("- ... and more.")
                 md_output.append("") # newline
            md_output.append("\n")

        # 6. Final Redesigned System
        # Check for an error specifically at the redesign stage
        if "final_system_design_error" in full_report_data:
             md_output.extend(self._format_individual_design(full_report_data["final_system_design_error"], "6. Final Redesigned System (Error during Redesign)"))
        elif "final_system_design" in full_report_data:
            md_output.extend(self._format_individual_design(full_report_data["final_system_design"], "6. Final Redesigned System (AI Generated)"))
        else:
            md_output.append("## 6. Final Redesigned System\n_Redesign step was not completed or data is missing._\n")


        formatted_text = "\n".join(md_output)
        logger.info("Comprehensive report formatting complete.")
        return formatted_text

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    formatting_agent = OutputFormattingAgent()

    # Build a mock full_report_data similar to what Orchestrator would create
    mock_full_report = {
        "cleaned_user_flow": "User registers. User logs in. User views dashboard.",
        "user_flow_analysis": {
            "actors": ["User", "System"], "actions": ["User registers", "User logs in"], "screens_pages": ["Registration Page", "Login Page", "Dashboard"]
        },
        "initial_system_design": {
            "suggested_services": [{"name": "UserService", "description": "Manages users."}],
            "api_endpoints": [{"method": "POST", "path": "/register", "description": "Registers user."}]
        },
        "design_analysis_report": {
            "overall_assessment_score": 7, "summary": "Good start, needs password reset.",
            "completeness_notes": ["Password reset missing."]
        },
        "design_review_summary": {
            "review_summary": "Needs password reset and better error handling.",
            "prioritized_issues": [{"issue_id": "P1", "category": "Completeness", "description": "Password reset", "recommendation_for_redesign": "Add it."}]
        },
        "simulation_report": {
            "overall_simulation_notes": "Simulation okay, consider edge cases for login.",
            "conceptual_test_cases": [{"test_id": "TC1", "description": "Valid login", "expected_outcome": "Success"}]
        },
        "final_system_design": {
            "suggested_services": [{"name": "UserService", "description": "Manages users, including password reset."}, {"name": "NotificationService", "description": "Sends emails."}],
            "api_endpoints": [
                {"method": "POST", "path": "/register", "description": "Registers user."},
                {"method": "POST", "path": "/login", "description": "Logs in user."},
                {"method": "POST", "path": "/request-password-reset", "description": "Requests password reset."}
            ],
            "database_tables": [{"name": "users", "columns": ["id", "email", "password_hash", "updated_at"], "relations": []}],
            "design_rationale_changes": ["Added password reset flow.", "Added updated_at to users table."]
        }
    }

    logger.info("Testing comprehensive report formatting...")
    formatted_report = formatting_agent.format_design(mock_full_report)
    logger.info(f"Formatted Comprehensive Report:\n{formatted_report}")

    logger.info("Testing formatting with an early pipeline error...")
    error_report = formatting_agent.format_design({"error": "Critical Failure in Ingestion", "details": "Input file not found."})
    logger.info(f"Formatted Error Report:\n{error_report}")

    logger.info("Testing formatting with a late pipeline error (at redesign stage)...")
    late_error_data = mock_full_report.copy()
    late_error_data["final_system_design_error"] = {"error": "Redesign AI failed", "details": "Model timed out."}
    del late_error_data["final_system_design"] # Remove the successful one
    formatted_late_error = formatting_agent.format_design(late_error_data)
    logger.info(f"Formatted Late Error Report:\n{formatted_late_error}")
