import re
import logging

logger = logging.getLogger(__name__)

class UserFlowIngestionAgent:
    """
    Agent responsible for ingesting and performing initial processing of the user flow text.
    """
    def __init__(self):
        pass

    def ingest_user_flow(self, raw_text: str) -> str:
        """
        Takes raw user flow text, validates it, and performs basic cleaning.
        """
        if not raw_text or not raw_text.strip():
            raise ValueError("User flow text cannot be empty.")

        # Basic cleaning:
        # - Remove leading/trailing whitespace from the whole text
        # - Collapse multiple spaces into one
        # - Ensure consistent line breaks (optional, depending on expected input)
        processed_text = raw_text.strip()
        processed_text = re.sub(r'\s+', ' ', processed_text) # Collapse multiple spaces
        # For simplicity, we'll assume single spaces are fine and further line break
        # processing might be handled by the analysis agent if it expects specific structures.

        logger.info(f"Ingested and cleaned text (first 100 chars): '{processed_text[:100]}...'")
        return processed_text

if __name__ == '__main__':
    # Basic logging setup for standalone execution
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Example Usage
    ingestion_agent = UserFlowIngestionAgent()
    sample_flow_empty = ""
    sample_flow_valid = """
    User Registration Flow:
    1. User navigates to the signup page.
    2. User enters email, password, and username.
    3. System validates the input. If valid, creates a new user account.
    4. System sends a confirmation email.
    5. User is redirected to the login page or dashboard.
    """
    sample_flow_messy = "  User logs in   with   credentials.  System   checks. "

    try:
        logger.info("Testing with empty flow (should raise ValueError)...")
        ingestion_agent.ingest_user_flow(sample_flow_empty)
    except ValueError as e:
        logger.error(f"Caught expected error for empty flow: {e}", exc_info=True)

    logger.info("Testing with valid flow...")
    processed_valid = ingestion_agent.ingest_user_flow(sample_flow_valid)
    logger.info(f"Processed valid flow:\n{processed_valid}")

    logger.info("Testing with messy flow...")
    processed_messy = ingestion_agent.ingest_user_flow(sample_flow_messy)
    logger.info(f"Processed messy flow:\n{processed_messy}")
