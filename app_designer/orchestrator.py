import os
import logging
from . import config  # Import the config module
from .agents.ingestion_agent import UserFlowIngestionAgent
from .agents.analysis_agent import UserFlowAnalysisAgent
from .agents.generation_agent import SystemDesignGenerationAgent
from .agents.formatting_agent import OutputFormattingAgent

logger = logging.getLogger(__name__)

class Orchestrator:
    """
    Orchestrates the workflow between different agents to generate
    a system design from a user flow text.
    """
    def __init__(self, gemini_api_key: str | None = None, gemini_model_name: str | None = None):
        logger.info("Orchestrator: Initializing agents...")

        # Use provided model name, else fallback to config, else to a hardcoded default
        effective_model_name = gemini_model_name or config.DEFAULT_GEMINI_MODEL

        if gemini_api_key is None:
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if not gemini_api_key:
                logger.warning("GEMINI_API_KEY environment variable not found. "
                               "SystemDesignGenerationAgent will run in simulation mode.")
                # Provide a dummy key for simulation if none is found at all
                # The GenerationAgent itself will also log a warning.
                gemini_api_key = "DUMMY_API_KEY_FOR_SIMULATION"
            else:
                logger.info("GEMINI_API_KEY loaded from environment variable.")

        self.ingestion_agent = UserFlowIngestionAgent()
        self.analysis_agent = UserFlowAnalysisAgent()
        # Pass the potentially loaded API key and effective model name to the generation agent
        self.generation_agent = SystemDesignGenerationAgent(
            api_key=gemini_api_key,
            model_name=effective_model_name  # Use the resolved model name
        )
        self.formatting_agent = OutputFormattingAgent()
        logger.info(f"Orchestrator: Agents initialized. Using Gemini model: {effective_model_name}")

    def generate_system_design(self, user_flow_text: str) -> str:
        """
        Processes the user flow text through the pipeline of agents
        and returns the formatted system design.
        """
        logger.info(f"Starting system design generation for flow: '{user_flow_text[:100]}...'")

        try:
            # 1. Ingestion
            logger.debug("--- Orchestrator: Step 1: Ingestion ---")
            cleaned_text = self.ingestion_agent.ingest_user_flow(user_flow_text)
            if not cleaned_text:
                logger.error("Ingestion failed, no text to process.")
                return "Error: Ingestion failed, no text to process."

            # 2. Analysis
            logger.debug("--- Orchestrator: Step 2: Analysis ---")
            analysis_output = self.analysis_agent.analyze_flow(cleaned_text)
            if not analysis_output:
                logger.error("Analysis failed, no output from analysis agent.")
                return "Error: Analysis failed, no output from analysis agent."

            # 3. Generation
            logger.debug("--- Orchestrator: Step 3: Generation (Gemini/Simulated) ---")
            design_components = self.generation_agent.generate_design_components(analysis_output)
            if not design_components: # Should not happen if generation_agent returns error dict
                logger.error("Design generation failed, no components produced by agent.")
                return "Error: Design generation failed, no components produced."
            if "error" in design_components: # Check for specific error structure from agent
                logger.error(f"Error from Generation Agent: {design_components.get('details', design_components['error'])}")
                # Format the error nicely for the user
                # Potentially use formatting_agent to make error reports consistent
                error_report = f"# System Design Generation Error\n\n" \
                               f"**Error:** {design_components['error']}\n"
                if 'details' in design_components:
                    error_report += f"**Details:** {design_components['details']}\n"
                if 'raw_response' in design_components: # Be careful about logging raw responses if sensitive
                    error_report += f"\n**Raw AI Response (snippet for debugging):**\n" \
                                    f"```\n{str(design_components['raw_response'])[:200]}...\n```\n"
                return error_report


            # 4. Formatting
            logger.debug("--- Orchestrator: Step 4: Formatting ---")
            formatted_design = self.formatting_agent.format_design(design_components)

            logger.info("System design generation process complete.")
            return formatted_design

        except ValueError as ve:
            logger.error(f"A validation error occurred in orchestrator: {ve}", exc_info=True)
            return f"Error in processing: {ve}"
        except Exception as e:
            logger.error(f"An unexpected error occurred in orchestrator: {e}", exc_info=True)
            return f"An unexpected error occurred during system design generation: {e}"

if __name__ == '__main__':
    # Basic logging setup for standalone execution
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Orchestrator will try to load GEMINI_API_KEY from environment by default
    orchestrator = Orchestrator()

    sample_user_flow = """
    User Story: Online Book Purchase

    1.  The user searches for a book by title or author on the main page.
    2.  The system displays a list of matching books.
    3.  The user clicks on a book to view its detailed product page.
    4.  User clicks "Add to Cart".
    5.  System adds the book to the shopping cart.
    6.  User navigates to the shopping cart page.
    7.  User clicks "Proceed to Checkout".
    8.  System directs user to the checkout page. User enters shipping and payment information.
    9.  System validates and processes the payment via a Payment Gateway.
    10. If payment is successful, system confirms order and sends confirmation email.
    """

    logger.info("=== Running Orchestrator example with Online Book Purchase Flow ===")
    final_design_output = orchestrator.generate_system_design(sample_user_flow)

    print("\n" + "="*50)
    print("Final Generated System Design (Formatted by Orchestrator run):")
    print("="*50)
    print(final_design_output)
    print("="*50 + "\n")

    # Example of a flow that might trigger different simulation rules
    login_flow_example = "Basic User Login: User enters username and password. System authenticates. On success, redirect to dashboard. On failure, show error."
    logger.info("=== Running Orchestrator example with Login Flow ===")
    login_design_output = orchestrator.generate_system_design(login_flow_example)

    print("\n" + "="*50)
    print("Final Generated System Design (Login Flow - Formatted by Orchestrator run):")
    print("="*50)
    print(login_design_output)
    print("="*50 + "\n")

    logger.info("Orchestrator standalone test finished.")
