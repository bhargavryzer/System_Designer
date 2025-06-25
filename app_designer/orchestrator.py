import os
import logging
import json # For logging complex dicts
from . import config
from .agents import (
    UserFlowIngestionAgent,
    UserFlowAnalysisAgent,         # For user flow text analysis
    SystemDesignGenerationAgent,   # For initial design generation
    DesignAnalysisAgent,           # For AI analysis of the generated design
    DesignReviewAgent,
    SimulationAndTestGenerationAgent,
    RedesignAgent,
    OutputFormattingAgent
)

logger = logging.getLogger(__name__)

class Orchestrator:
    """
    Orchestrates the workflow between different agents to generate,
    analyze, review, simulate (conceptually), and redesign a system design
    from a user flow text.
    """
    def __init__(self, gemini_api_key: str | None = None, gemini_model_name: str | None = None):
        logger.info("Orchestrator: Initializing all agents for advanced workflow...")

        resolved_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not resolved_api_key:
            logger.warning("GEMINI_API_KEY environment variable not found or not provided. "
                           "AI-driven agents will run in simulation/mock mode.")
            resolved_api_key = "DUMMY_API_KEY_FOR_SIMULATION"
        else:
            logger.info("GEMINI_API_KEY loaded for AI agents.")

        effective_model_name = gemini_model_name or config.DEFAULT_GEMINI_MODEL
        logger.info(f"Using Gemini Model: {effective_model_name} (or simulation if API key is dummy/missing)")

        # Core initial agents
        self.ingestion_agent = UserFlowIngestionAgent()
        self.user_flow_analysis_agent = UserFlowAnalysisAgent() # Renamed for clarity
        self.initial_design_generation_agent = SystemDesignGenerationAgent(
            api_key=resolved_api_key,
            model_name=effective_model_name
        )

        # New agents for advanced workflow (conceptual, using mocks)
        self.design_analysis_agent = DesignAnalysisAgent(api_key=resolved_api_key, model_name=effective_model_name)
        self.design_review_agent = DesignReviewAgent(api_key=resolved_api_key, model_name=effective_model_name)
        self.simulation_agent = SimulationAndTestGenerationAgent(api_key=resolved_api_key, model_name=effective_model_name)
        self.redesign_agent = RedesignAgent(api_key=resolved_api_key, model_name=effective_model_name)

        self.formatting_agent = OutputFormattingAgent()
        logger.info("Orchestrator: All agents initialized.")

    def _log_step_data(self, step_name: str, data: dict, detail_level: int = logging.DEBUG):
        """Helper to log data from steps, showing keys or full data based on level."""
        if logger.isEnabledFor(detail_level):
            try:
                # Attempt to pretty-print JSON for readability if it's a dict/list
                log_message = json.dumps(data, indent=2, ensure_ascii=False)
            except TypeError:
                log_message = str(data) # Fallback for non-serializable data
            logger.log(detail_level, f"--- Orchestrator: Data from {step_name} ---\n{log_message[:1000]}...\n--- End {step_name} Data ---")
        else:
            logger.info(f"--- Orchestrator: Completed {step_name} (keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}) ---")


    def generate_system_design(self, user_flow_text: str) -> str:
        """
        Processes the user flow text through the full pipeline of agents
        including generation, analysis, review, simulation, and redesign.
        Returns the comprehensive formatted system design report.
        """
        logger.info(f"Starting ADVANCED system design generation for flow: '{user_flow_text[:100]}...'")

        full_report_data = {"user_flow_text": user_flow_text}

        try:
            # 1. Ingestion
            logger.info("--- Orchestrator: Step 1: User Flow Ingestion ---")
            cleaned_text = self.ingestion_agent.ingest_user_flow(user_flow_text)
            if not cleaned_text:
                logger.error("Ingestion failed.")
                return self.formatting_agent.format_design({"error": "Ingestion failed", "details": "No text to process."})
            full_report_data["cleaned_user_flow"] = cleaned_text
            self._log_step_data("User Flow Ingestion", {"cleaned_text_snippet": cleaned_text[:100]})

            # 2. User Flow Analysis (Rule-based or conceptual AI)
            logger.info("--- Orchestrator: Step 2: User Flow Analysis ---")
            user_flow_analysis_output = self.user_flow_analysis_agent.analyze_flow(cleaned_text)
            if not user_flow_analysis_output:
                logger.error("User Flow Analysis failed.")
                return self.formatting_agent.format_design({"error": "User Flow Analysis failed"})
            full_report_data["user_flow_analysis"] = user_flow_analysis_output
            self._log_step_data("User Flow Analysis", user_flow_analysis_output)

            # 3. Initial Design Generation (Gemini or Simulated)
            logger.info("--- Orchestrator: Step 3: Initial Design Generation ---")
            initial_system_design = self.initial_design_generation_agent.generate_design_components(user_flow_analysis_output)
            if "error" in initial_system_design:
                logger.error(f"Initial Design Generation failed: {initial_system_design.get('details', initial_system_design['error'])}")
                return self.formatting_agent.format_design(initial_system_design) # Format the error
            full_report_data["initial_system_design"] = initial_system_design
            self._log_step_data("Initial Design Generation", initial_system_design)

            # --- Start of New Advanced Workflow Steps (Conceptual Mocks) ---

            # 4. AI Design Analysis
            logger.info("--- Orchestrator: Step 4: AI Design Analysis (Conceptual) ---")
            design_analysis_report = self.design_analysis_agent.analyze_design(initial_system_design, user_flow_analysis_output)
            full_report_data["design_analysis_report"] = design_analysis_report
            self._log_step_data("AI Design Analysis", design_analysis_report)

            # 5. AI Design Review
            logger.info("--- Orchestrator: Step 5: AI Design Review (Conceptual) ---")
            design_review_summary = self.design_review_agent.review_design(initial_system_design, design_analysis_report)
            full_report_data["design_review_summary"] = design_review_summary
            self._log_step_data("AI Design Review", design_review_summary)

            # 6. AI Simulation & Test Generation
            logger.info("--- Orchestrator: Step 6: AI Simulation & Test Generation (Conceptual) ---")
            simulation_report = self.simulation_agent.simulate_and_test(initial_system_design, user_flow_analysis_output)
            full_report_data["simulation_report"] = simulation_report
            self._log_step_data("AI Simulation & Test Generation", simulation_report)

            # 7. AI Redesign
            logger.info("--- Orchestrator: Step 7: AI System Redesign (Conceptual) ---")
            final_redesigned_system = self.redesign_agent.redesign_system(
                original_user_flow_analysis=user_flow_analysis_output,
                initial_system_design=initial_system_design,
                design_analysis_report=design_analysis_report,
                design_review_summary=design_review_summary,
                simulation_report=simulation_report
            )
            if "error" in final_redesigned_system: # Check if redesign itself reported an error
                 logger.error(f"AI System Redesign failed: {final_redesigned_system.get('details', final_redesigned_system['error'])}")
                 # We might want to format the report up to this point, or just the error
                 full_report_data["final_system_design_error"] = final_redesigned_system
            else:
                full_report_data["final_system_design"] = final_redesigned_system
            self._log_step_data("AI System Redesign", final_redesigned_system)

            # --- End of New Advanced Workflow Steps ---

            # 8. Formatting the Comprehensive Report
            logger.info("--- Orchestrator: Step 8: Formatting Comprehensive Report ---")
            # The formatting agent will now receive the `full_report_data` dictionary
            formatted_final_report = self.formatting_agent.format_design(full_report_data)

            logger.info("ADVANCED system design generation process complete.")
            return formatted_final_report

        except Exception as e:
            logger.error(f"An unexpected error occurred in the orchestrator's advanced workflow: {e}", exc_info=True)
            # Format a general error if something outside the agents failed
            return self.formatting_agent.format_design({
                "error": "Orchestrator Pipeline Error",
                "details": f"An unexpected error occurred: {str(e)}",
                "partial_report_data_keys": list(full_report_data.keys()) # Show what we had so far
            })

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # To see more detailed logs from the orchestrator and agents during standalone run:
    # logging.getLogger('app_designer').setLevel(logging.DEBUG)
    # or specifically: logging.getLogger('app_designer.orchestrator').setLevel(logging.DEBUG)


    orchestrator = Orchestrator() # Will use env var for API key or dummy

    sample_user_flow = """
    User Authentication Flow:
    1. User navigates to the signup page.
    2. User enters email, password. System validates. If valid, creates account.
    3. System sends confirmation email.
    4. User clicks confirmation link. System activates account.
    5. User navigates to login page, enters credentials. System validates.
    6. On success, user is redirected to dashboard.
    7. User should be able to request a password reset if they forget their password.
    """

    logger.info("=== Running Orchestrator (Advanced Workflow) with Sample User Flow ===")
    final_report = orchestrator.generate_system_design(sample_user_flow)

    print("\n" + "="*70)
    print("Comprehensive System Design Report (Formatted):")
    print("="*70)
    print(final_report)
    print("="*70 + "\n")

    logger.info("Orchestrator (Advanced Workflow) standalone test finished.")
