# System Design Generator from User Flow (using Gemini AI)

This application takes a textual description of an application's user flow and leverages Google's Gemini AI to generate a high-level system design. The output includes suggestions for services/modules, API endpoints, database tables, technology stack, and security considerations, formatted in Markdown.

## Features

-   Parses user flow text provided directly or from a file.
-   Generates an initial system design using Gemini AI (or simulation).
-   **Conceptual Advanced AI Workflow (Currently Mocked):**
    -   **AI Design Analysis:** Analyzes the initial design for completeness, coherence, and best practices.
    -   **AI Design Review:** Synthesizes analysis into a review and provides redesign recommendations.
    -   **AI Simulation & Test Generation:** Conceptually generates test cases and simulates system behavior to find flaws.
    -   **AI Redesign:** Refines the initial design based on all feedback.
-   Outputs a comprehensive system design report in Markdown, including all stages of the conceptual AI refinement process.
-   Configurable Gemini model (for initial generation) and logging levels via CLI.
-   User flow analysis currently uses regex/keywords; a future enhancement is to use Gemini for this too.

## Prerequisites

-   Python 3.9+
-   Google Generative AI SDK: `pip install google-generativeai`
-   (Optional, for loading `.env` files if you choose to use one for API keys): `pip install python-dotenv`

## Setup

1.  **Clone the repository (if applicable) or ensure all project files are in a directory (e.g., `app_designer/`).**

2.  **Install dependencies:**
    ```bash
    pip install google-generativeai
    # pip install python-dotenv # If you plan to use a .env file for the API key
    ```

3.  **Set up your Gemini API Key:**
    You need a valid API key for Google's Gemini models. You can obtain one from [Google AI Studio](https://aistudio.google.com/app/apikey).

    The application expects the API key to be available as an environment variable:
    ```bash
    export GEMINI_API_KEY="YOUR_API_KEY_HERE"
    ```
    Alternatively, you can pass the API key directly via the `--api_key` CLI argument, but using an environment variable is recommended for security.

    If the API key is not provided or the `google-generativeai` SDK is not available, the system design generation will run in a **simulated mode** with mock responses.

## Usage

Navigate to the directory containing `main.py` (e.g., the `app_designer` directory if you've structured it that way, or its parent if `main.py` is at the root of `app_designer` package). The application is run via `main.py`.

**General Command Structure:**
```bash
python -m app_designer.main [INPUT_OPTION] [OTHER_OPTIONS]
```
or if `main.py` is directly in your current path (e.g. you `cd app_designer`):
```bash
python main.py [INPUT_OPTION] [OTHER_OPTIONS]
```

**Input Options (Required - choose one):**

-   `--text "Your user flow text..."`: Provide the user flow as a direct string.
-   `--file /path/to/your/user_flow.txt`: Provide the path to a text file containing the user flow.

**Other Options:**

-   `-o /path/to/output.md`, `--output /path/to/output.md`: Save the generated Markdown to a file. (Default: prints to console)
-   `--api_key "YOUR_API_KEY"`: Specify your Gemini API key (overrides environment variable).
-   `--model_name "model-name"`: Specify the Gemini model to use (e.g., `gemini-1.5-flash`, `gemini-pro`). Defaults to the value in `app_designer/config.py`.
-   `-v`, `--verbose`: Enable verbose (DEBUG level) logging.
-   `-q`, `--quiet`: Enable quiet (WARNINGS only) logging.

**Examples:**

1.  **Using direct text input, output to console (assuming you are in the directory containing `app_designer`):**
    ```bash
    python -m app_designer.main --text "User clicks login. System verifies credentials. User sees dashboard."
    ```

2.  **Using a file input, output to `design.md` (assuming you are in the directory containing `app_designer`):**
    ```bash
    # First, create a sample file, e.g., sample_flows/registration_flow.txt
    # mkdir -p sample_flows
    # echo "User goes to signup page. User enters details. System creates account." > sample_flows/registration_flow.txt
    python -m app_designer.main --file ./sample_flows/registration_flow.txt -o design.md
    ```

3.  **Using verbose logging and a specific model (assuming you are in the `app_designer` directory):**
    ```bash
    python main.py --file ../some_flow.txt --model_name "gemini-1.5-pro-latest" -v
    ```
    *(Adjust path to `some_flow.txt` as needed)*

4.  **Running with your API key (if not set as env var):**
    ```bash
    python -m app_designer.main --file flow.txt --api_key "YOUR_ACTUAL_API_KEY"
    ```

## Project Structure

```
app_designer_project_root/
├── app_designer/          <-- This is the main package
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── analysis_agent.py
│   │   ├── formatting_agent.py
│   │   ├── generation_agent.py
│   │   └── ingestion_agent.py
│   ├── __init__.py
│   ├── config.py
│   ├── main.py             <-- CLI Entry point
│   ├── orchestrator.py
├── README.md               <-- This file
└── tests/                  <-- (To be added)
    └── ...
```
*(You might also have a top-level `.gitignore`, `requirements.txt` etc.)*

## Advanced AI Workflow (Conceptual)

The application now includes a more advanced, multi-stage conceptual workflow:

1.  **User Flow Ingestion & Analysis:** The input user flow is cleaned and (currently) analyzed using rule-based methods.
2.  **Initial Design Generation:** `SystemDesignGenerationAgent` creates a first draft of the system design using Gemini (or simulation).
3.  **AI Design Analysis (`DesignAnalysisAgent`):** This (conceptual) agent analyzes the initial design for completeness, coherence, best practices, and ambiguities. *Currently returns mocked data.*
4.  **AI Design Review (`DesignReviewAgent`):** This (conceptual) agent reviews the analysis, prioritizes issues, and suggests redesign focus areas. *Currently returns mocked data.*
5.  **AI Simulation & Test Generation (`SimulationAndTestGenerationAgent`):** This (highly conceptual) agent would generate test cases and simulate system behavior to find flaws. *Currently returns mocked data.*
6.  **AI Redesign (`RedesignAgent`):** This (conceptual) agent takes all prior feedback to generate an improved system design. *Currently returns mocked data.*
7.  **Comprehensive Report:** The `OutputFormattingAgent` compiles all these stages into a single detailed Markdown report.

The AI-driven steps (3-6) are placeholders for what would be complex interactions with advanced AI models. Their current implementation demonstrates the workflow and data structures involved.

## Future Enhancements / Production Considerations

-   **Implement Real AI for Advanced Workflow:** Replace mocked responses in `DesignAnalysisAgent`, `DesignReviewAgent`, `SimulationAndTestGenerationAgent`, and `RedesignAgent` with actual Gemini API calls and sophisticated prompt engineering.
-   **Robust User Flow Analysis:** Integrate Gemini for the initial user flow analysis phase (`UserFlowAnalysisAgent`) instead of relying on basic regex/keywords.
-   **Advanced Error Handling & Retries:** More granular error handling and retry mechanisms for all API calls.
-   **Input Validation:** Stricter validation for input text complexity and size.
-   **Output Formats:** Support for JSON or other structured output formats for each stage.
-   **Interactive Mode:** Allow users to provide feedback at each stage of the AI review/redesign loop.
-   **Testing:** Comprehensive unit and integration tests for all agents, including mocking strategies for AI calls.
-   **Packaging:** Package the application for easier distribution (e.g., PyPI, Docker).
-   **Security:** If deployed as a service, implement proper authentication/authorization. For CLI, continue secure API key handling.
```
