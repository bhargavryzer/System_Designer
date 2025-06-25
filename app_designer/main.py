import os
import argparse
import logging
from orchestrator import Orchestrator
from . import config # Import the config module

# It's good practice to set up logging as early as possible.
# For a CLI app, basicConfig is often sufficient for initial setup.
# More complex apps might use a logging config file.
logging.basicConfig(
    level=logging.INFO,  # Default level, can be overridden by args
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__) # Get a logger for this module

# --- Best Practices for API Key Management ---
# 1. Environment Variables (as shown): Good for development and many deployment scenarios.
#    Set `GEMINI_API_KEY` in your shell or .env file (use python-dotenv to load .env).
# 2. Secrets Management Services: For production, use services like AWS Secrets Manager,
#    Google Secret Manager, Azure Key Vault, or HashiCorp Vault.
#    Your application would then fetch the key from these services at runtime.
# 3. Configuration Files (with caution): If used, ensure the config file containing the key
#    is NOT checked into version control (add to .gitignore). Permissions should be restricted.
#    This is generally less secure than environment variables or dedicated secrets managers.
#
# NEVER hardcode API keys directly in your source code in a production application.

def run_design_generation_app():
    """
    Main function to run the application.
    Parses command-line arguments, initializes the Orchestrator,
    and generates a system design based on user input.
    """
    parser = argparse.ArgumentParser(
        description="System Design Generator from User Flow using Gemini AI.",
        formatter_class=argparse.RawTextHelpFormatter # For better help text formatting
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "-t", "--text",
        type=str,
        help="Direct text string of the user flow."
    )
    input_group.add_argument(
        "-f", "--file",
        type=argparse.FileType('r', encoding='utf-8'),
        help="Path to a text file containing the user flow."
    )
    parser.add_argument(
        "-o", "--output",
        type=argparse.FileType('w', encoding='utf-8'),
        help="Optional: Path to a file where the generated Markdown design will be saved."
    )
    parser.add_argument(
        "--api_key",
        type=str,
        default=os.getenv("GEMINI_API_KEY"), # Default to environment variable
        help="Gemini API Key. If not provided, defaults to GEMINI_API_KEY environment variable. "
             "If neither is set, runs in simulation mode."
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default=config.DEFAULT_GEMINI_MODEL, # Default from config.py
        help=f"The Gemini model name to use (e.g., 'gemini-pro', 'gemini-1.5-pro-latest'). Default: {config.DEFAULT_GEMINI_MODEL}"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
        help="Enable verbose (DEBUG level) logging."
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_const",
        dest="loglevel",
        const=logging.WARNING,
        help="Enable quiet (WARNINGS only) logging."
    )

    args = parser.parse_args()

    # Update logging level based on arguments
    logging.getLogger().setLevel(args.loglevel) # Set root logger level
    # You might want to set levels for specific loggers if you have more complex needs
    # For example: logging.getLogger('app_designer.agents.generation_agent').setLevel(logging.DEBUG)

    logger.info("Application: System Design Generator - Starting")
    logger.debug(f"Arguments received: {args}")


    user_flow_text = ""
    if args.text:
        user_flow_text = args.text
        logger.info("User flow provided via direct text input.")
    elif args.file:
        try:
            user_flow_text = args.file.read()
            logger.info(f"User flow read successfully from file: {args.file.name}")
        except Exception as e:
            logger.error(f"Error reading from file {args.file.name}: {e}", exc_info=True)
            print(f"Error: Could not read from file {args.file.name}. See logs for details.")
            return 1 # Exit with error code
        finally:
            args.file.close()

    if not user_flow_text.strip():
        logger.error("User flow text is empty. Cannot proceed.")
        print("Error: User flow input is empty.")
        return 1


    # Initialize the orchestrator with the API key and model name from args or environment
    # The Orchestrator itself will handle the case where api_key is None or a dummy value.
    orchestrator = Orchestrator(
        gemini_api_key=args.api_key,
        gemini_model_name=args.model_name
    )

    logger.info("Requesting system design generation from Orchestrator...")
    formatted_system_design = orchestrator.generate_system_design(user_flow_text)

    if args.output:
        try:
            args.output.write(formatted_system_design)
            logger.info(f"Generated system design saved to: {args.output.name}")
            print(f"\nGenerated system design saved to: {args.output.name}")
        except Exception as e:
            logger.error(f"Error writing to output file {args.output.name}: {e}", exc_info=True)
            print(f"Error: Could not write to output file {args.output.name}. Displaying to console instead:")
            print("\n" + "="*50)
            print("Final Generated System Design:")
            print("="*50)
            print(formatted_system_design)
            print("="*50)
        finally:
            args.output.close()
    else:
        # Print to console if no output file specified
        print("\n" + "="*50)
        print("Final Generated System Design:")
        print("="*50)
        print(formatted_system_design)
        print("="*50)

    logger.info("Application: System Design Generator - Finished")
    return 0 # Exit with success code

if __name__ == "__main__":
    # Example of how to run from command line (these would be actual CLI commands):
    # python app_designer/main.py --file path/to/your/user_flow.txt
    # python app_designer/main.py --text "User logs in. System verifies. User sees dashboard." -o output.md
    # GEMINI_API_KEY="your_real_api_key" python app_designer/main.py --file flow.txt

    # To make this script executable and callable directly, you would typically
    # use a setup.py with entry_points, or just run `python -m app_designer.main ...`
    # For now, it's designed to be run as `python app_designer/main.py ...`

    # If running this file directly for testing (e.g. in an IDE without args):
    # import sys
    # if len(sys.argv) == 1: # No CLI args provided
    #     print("Running with default test flow (no CLI args detected)...")
    #     # This is a simple way to test; ideally, use pytest or similar for formal tests.
    #     # For direct execution in IDE without args, you might hardcode a test flow:
    #     test_flow = """
    #     Test Flow for direct execution:
    #     1. User visits the homepage.
    #     2. User clicks the 'About Us' link.
    #     3. System displays the About Us page.
    #     """
    #     # To simulate command line args for testing:
    #     # sys.argv.extend(['--text', test_flow, '--verbose'])
    #     # Or, to ensure it runs if this is the entry point without external args:
    #     # This part is tricky because argparse expects CLI args.
    #     # Better to run with actual args or use a dedicated test suite.
    #     # For now, we'll just let it run with `run_design_generation_app()`
    #     # which will show help if no args are given.
    #     pass

    exit_code = run_design_generation_app()
    sys.exit(exit_code) # Ensure the application exits with the correct code
import sys # Ensure sys is imported if used in __main__ guard. It's good practice to have it at the top.
