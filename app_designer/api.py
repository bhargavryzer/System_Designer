import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS # For handling Cross-Origin Resource Sharing if UI is on different port/domain

from .orchestrator import Orchestrator
from . import config # To potentially get default model, etc.

# Configure basic logging for the API
# In a production Flask app, you'd likely use a more robust logging setup
# (e.g., Gunicorn's logging, or configure Flask's app.logger more extensively)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app) # Enable CORS for all routes, allowing requests from React dev server

# Initialize the Orchestrator once when the application starts.
# The Orchestrator will load the GEMINI_API_KEY from the environment.
# Ensure GEMINI_API_KEY is set in the environment where this Flask app runs.
# Default model can come from config.py or be overridden by request.
try:
    # Pass None for api_key and model_name so Orchestrator uses its defaults
    # (env var for key, config for model)
    orchestrator_instance = Orchestrator()
    logger.info("Orchestrator initialized successfully for Flask API.")
except Exception as e:
    logger.error(f"FATAL: Failed to initialize Orchestrator: {e}", exc_info=True)
    # If Orchestrator fails to init, the app is likely non-functional.
    # Depending on policy, you might exit or let Flask start and endpoints fail.
    orchestrator_instance = None


@app.route('/api/v1/generate-design', methods=['POST'])
def generate_design_endpoint():
    if orchestrator_instance is None:
        logger.error("Orchestrator not available. Cannot process request.")
        return jsonify({"error": "Server configuration error: Orchestrator not initialized."}), 500

    try:
        data = request.get_json()
        if not data:
            logger.warning("API /generate-design: Received empty request data.")
            return jsonify({"error": "Bad Request: No JSON data received."}), 400

        user_flow_text = data.get('user_flow_text')
        if not user_flow_text or not isinstance(user_flow_text, str) or not user_flow_text.strip():
            logger.warning("API /generate-design: 'user_flow_text' is missing or invalid.")
            return jsonify({"error": "Bad Request: 'user_flow_text' is required and must be a non-empty string."}), 400

        # Optional parameters from UI (e.g., if user can select a model)
        options = data.get('options', {})
        ui_selected_model = options.get('model_name') # Orchestrator will use its default if this is None

        logger.info(f"API /generate-design: Received request for user flow (snippet): '{user_flow_text[:100]}...'")
        if ui_selected_model:
            logger.info(f"API /generate-design: UI requested model: {ui_selected_model}")
            # Re-initialize orchestrator if model changes per request, or modify orchestrator to accept model per call
            # For simplicity, let's assume Orchestrator can take model_name in its generate_system_design or is re-init.
            # Current Orchestrator sets model at init. For per-request model, Orchestrator would need change
            # or we'd need a pool of orchestrators.
            # For this conceptual API, we'll assume the orchestrator instance uses its configured model,
            # but log the request. A production system would need a more robust way to handle per-request models.
            # A simpler approach for now: if the model from UI is different from default,
            # we might create a new orchestrator instance for this call if performance allows.
            # This is a placeholder for more complex model management.
            temp_orchestrator = Orchestrator(gemini_model_name=ui_selected_model) # API key still from env
            report_markdown_and_structured_data = temp_orchestrator.generate_system_design(user_flow_text)
        else:
            report_markdown_and_structured_data = orchestrator_instance.generate_system_design(user_flow_text)


        # The orchestrator currently returns a single Markdown string.
        # For the API, it's better if it returns structured data alongside the markdown.
        # Let's assume the orchestrator's `generate_system_design` now returns a dictionary:
        # { "full_report_markdown": "...", "structured_data": { ... } }
        # For now, we'll adapt based on current Orchestrator output (just markdown string)
        # and wrap it. The OutputFormattingAgent's format_design method receives full_report_data.
        # The Orchestrator's generate_system_design method returns the output of format_design.
        # So, report_markdown_and_structured_data IS the markdown string.

        # To provide structured data, the Orchestrator would need to return `full_report_data`
        # *before* it's passed to the formatting agent, or the formatting agent returns both.
        # Let's assume for this API, we just pass the markdown.
        # A future enhancement would be to return the structured `full_report_data` too.

        if "error" in report_markdown_and_structured_data.lower() and report_markdown_and_structured_data.startswith("#"): # Simple check if it's an error markdown
            # This means an error occurred within the orchestrator pipeline and was formatted as such
            logger.warning(f"API /generate-design: Orchestrator returned an error report.")
            # We could parse the markdown error, or just return it.
            # For now, let's return a generic server error if the orchestrator itself signals a major issue.
            # Or, if it's a design-related error, it's already formatted.
            # This logic depends on how Orchestrator signals critical vs. partial errors.
            # Let's assume any string starting with "# System Design Generation Error" is an error to the client.
            if report_markdown_and_structured_data.strip().startswith("# System Design Generation Error") or \
               report_markdown_and_structured_data.strip().startswith("# Orchestrator Pipeline Error"):
                return jsonify({
                    "error": "Failed to generate design",
                    "report_markdown": report_markdown_and_structured_data # Send the formatted error
                }), 500 # Internal server error as the process didn't complete successfully

        logger.info(f"API /generate-design: Successfully generated design report.")
        return jsonify({
            "report_markdown": report_markdown_and_structured_data,
            # "structured_report": {} # Placeholder for future enhancement
        }), 200

    except Exception as e:
        logger.error(f"API /generate-design: Unhandled exception: {e}", exc_info=True)
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

def run_api_server(host='0.0.0.0', port=5001, debug=False):
    """Runs the Flask development server."""
    # In production, use a proper WSGI server like Gunicorn or uWSGI
    # Example: gunicorn -w 4 -b 0.0.0.0:5001 app_designer.api:app
    logger.info(f"Starting Flask API server on {host}:{port} (Debug: {debug})")
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    # This allows running the Flask app directly for development/testing
    # For production, use a WSGI server like Gunicorn.
    # Example:
    # Set GEMINI_API_KEY environment variable first.
    # export FLASK_APP=app_designer.api:app  (or python -m app_designer.api)
    # flask run -p 5001
    # Or:
    # python -m app_designer.api

    # For simplicity to run `python app_designer/api.py`:
    is_debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    api_host = os.environ.get("FLASK_RUN_HOST", "127.0.0.1")
    api_port = int(os.environ.get("FLASK_RUN_PORT", 5001))

    run_api_server(host=api_host, port=api_port, debug=is_debug)
