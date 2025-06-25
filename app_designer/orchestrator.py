from .agents.ingestion_agent import UserFlowIngestionAgent
from .agents.analysis_agent import UserFlowAnalysisAgent
from .agents.generation_agent import SystemDesignGenerationAgent
from .agents.formatting_agent import OutputFormattingAgent

class Orchestrator:
    """
    Orchestrates the workflow between different agents to generate
    a system design from a user flow text.
    """
    def __init__(self, gemini_api_key: str = "DUMMY_API_KEY"):
        print("Orchestrator: Initializing agents...")
        self.ingestion_agent = UserFlowIngestionAgent()
        self.analysis_agent = UserFlowAnalysisAgent()
        self.generation_agent = SystemDesignGenerationAgent(gemini_api_key=gemini_api_key)
        self.formatting_agent = OutputFormattingAgent()
        print("Orchestrator: Agents initialized.")

    def generate_system_design(self, user_flow_text: str) -> str:
        """
        Processes the user flow text through the pipeline of agents
        and returns the formatted system design.
        """
        print(f"\nOrchestrator: Starting system design generation for flow: '{user_flow_text[:100]}...'")

        try:
            # 1. Ingestion
            print("\nOrchestrator: --- Step 1: Ingestion ---")
            cleaned_text = self.ingestion_agent.ingest_user_flow(user_flow_text)
            if not cleaned_text:
                return "Error: Ingestion failed, no text to process."

            # 2. Analysis
            print("\nOrchestrator: --- Step 2: Analysis ---")
            analysis_output = self.analysis_agent.analyze_flow(cleaned_text)
            if not analysis_output:
                return "Error: Analysis failed, no output from analysis agent."

            # 3. Generation
            print("\nOrchestrator: --- Step 3: Generation (Simulated Gemini) ---")
            design_components = self.generation_agent.generate_design_components(analysis_output)
            if not design_components:
                return "Error: Design generation failed, no components produced."

            # 4. Formatting
            print("\nOrchestrator: --- Step 4: Formatting ---")
            formatted_design = self.formatting_agent.format_design(design_components)

            print("\nOrchestrator: System design generation complete.")
            return formatted_design

        except ValueError as ve:
            print(f"Orchestrator: A validation error occurred: {ve}")
            return f"Error in processing: {ve}"
        except Exception as e:
            print(f"Orchestrator: An unexpected error occurred: {e}")
            # In a real app, you might want to log the full traceback here
            return f"An unexpected error occurred during system design generation: {e}"

if __name__ == '__main__':
    # Example Usage
    orchestrator = Orchestrator() # Uses DUMMY_API_KEY for GenerationAgent

    sample_user_flow = """
    User Story: Online Book Purchase

    1.  The user searches for a book by title or author on the main page.
    2.  The system displays a list of matching books, including cover image, title, author, and price.
    3.  The user clicks on a book to view its detailed product page.
    4.  On the product page, the user can see more details, reviews, and an "Add to Cart" button.
    5.  User clicks "Add to Cart".
    6.  The system adds the book to the user's shopping cart and updates the cart icon/count.
    7.  User navigates to the shopping cart page.
    8.  The shopping cart page displays all items, quantities, and total price. User can update quantities or remove items.
    9.  User clicks "Proceed to Checkout".
    10. System directs user to the checkout page. User enters shipping address and payment information.
    11. System validates the information and processes the payment via a Payment Gateway.
    12. If payment is successful, the system confirms the order, displays an order confirmation page, and sends a confirmation email to the user.
    13. The user's order is recorded in their order history.
    """

    print("Orchestrator: === Running example with Online Book Purchase Flow ===")
    final_design_output = orchestrator.generate_system_design(sample_user_flow)
    print("\n" + "="*50)
    print("Final Generated System Design (Formatted):")
    print("="*50)
    print(final_design_output)
    print("="*50 + "\n")

    another_flow = "Basic User Login: User enters username and password into the login form. System authenticates credentials. If successful, user is redirected to their dashboard. If not, an error message is shown."
    print("Orchestrator: === Running example with Basic User Login Flow ===")
    final_design_output_login = orchestrator.generate_system_design(another_flow)
    print("\n" + "="*50)
    print("Final Generated System Design (Login Flow - Formatted):")
    print("="*50)
    print(final_design_output_login)
    print("="*50)
