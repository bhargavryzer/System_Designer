# System Design Generator from User Flow (using Gemini AI)

This application takes a textual description of an application's user flow and leverages Google's Gemini AI to generate a high-level system design. The output includes suggestions for services/modules, API endpoints, database tables, technology stack, and security considerations, formatted in Markdown.

## Current Functional Status

This application provides an end-to-end workflow for generating system design documentation from user flow descriptions. It can be run via CLI (`main.py`) or as a backend API (`api.py`).

-   **Initial System Design Generation:**
    -   This core step **can utilize the actual Google Gemini API** if a valid `GEMINI_API_KEY` is provided in the environment.
    -   If no valid API key is found, or if the `google-generativeai` SDK is not installed, this step falls back to a **simulated response** using predefined mock data.
-   **Advanced AI Workflow (Analysis, Review, Simulation, Redesign):**
    -   The subsequent stages in the advanced workflow—`DesignAnalysisAgent`, `DesignReviewAgent`, `SimulationAndTestGenerationAgent`, and `RedesignAgent`—are currently **conceptual and use mocked responses**.
    -   These mocked stages demonstrate the intended data flow and the *type* of analysis and refinement that a more advanced AI system could perform. They do **not** involve real AI calls for these specific refinement tasks in the current version.
-   **Low-Level Design (LLD):**
    -   The system *attempts* to outline LLD aspects (e.g., method signatures, detailed API schemas, specific database column definitions).
    -   These LLD details are primarily showcased within the **mocked output of the conceptual `RedesignAgent`**.
-   **Output:** The application generates a comprehensive Markdown report detailing all stages, including the mocked advanced workflow outputs and conceptual LLD.

## Features

-   Parses user flow text provided directly or from a file.
-   Generates an initial system design using Gemini AI (or simulation, see "Current Functional Status").
-   **Conceptual Advanced AI Workflow (Currently Mocked - see "Current Functional Status"):**
    -   AI Design Analysis
    -   AI Design Review
    -   AI Simulation & Test Generation
    -   AI Redesign
-   Outputs a comprehensive system design report in Markdown, including HLD and conceptual LLD.
-   Configurable Gemini model (for initial generation) and logging levels via CLI.
-   User flow analysis currently uses regex/keywords.

**Important Note on LLD and Production Readiness:**
While this system *attempts* to generate LLD aspects, any AI-generated LLD should be treated as a **detailed starting point or accelerator**. It is **not** a substitute for thorough review, refinement, and validation by experienced human engineers and architects. True production readiness involves many factors beyond initial design generation, including rigorous testing, security hardening, performance optimization, and adherence to specific organizational standards, all of which require expert human oversight.

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

## The Vision: A Universal AI Solution Architect

The aspiration to create an AI that acts as a senior solution architect—capable of generating production-ready system designs for any programming language, including diagrammatic outputs, and drawing inspiration from the web—represents a significant and exciting frontier in AI-driven software development. This is a highly ambitious goal with many complex challenges.

**Key Challenges for a Universal AI Architect:**

*   **Deep Language & Framework Nuance:** Mastering the idiomatic uses, best practices, standard libraries, concurrency models, error handling philosophies, and vast ecosystems of numerous programming languages and their frameworks is an immense task. Current LLMs have broad knowledge but may lack the deep, practical expertise required for *every* specific context.
*   **Constant Evolution:** The software landscape (languages, frameworks, cloud services, security threats) changes rapidly. Keeping an AI's knowledge base current and accurate is a continuous, large-scale effort.
*   **"Production-Ready" is Contextual:** The definition of "production-ready" varies dramatically based on application type (e.g., hobby project vs. enterprise financial system), scale, performance needs, security requirements, compliance mandates, team skills, and budget. An AI would need to deeply understand and reason about these non-functional requirements.
*   **Diagramming Complexity:** Generating semantically correct, visually clear, and contextually appropriate diagrams (e.g., C4, sequence, ERD, deployment) from abstract designs is non-trivial. While generating code for diagramming tools (PlantUML, Mermaid) is feasible, ensuring the diagrams are truly insightful requires advanced reasoning.
*   **True Validation & Simulation:** Rigorously validating a design for correctness, security vulnerabilities, performance bottlenecks, and simulating its behavior without actual execution remains an extremely difficult research problem, especially across diverse architectures.
*   **Non-Technical Factors:** Human architects consider factors like existing infrastructure, organizational standards, team capabilities, project timelines, and even stakeholder politics. Incorporating and reasoning about these qualitative aspects is challenging for AI.
*   **Web Inspiration & Information Quality:** While AI can be equipped with tools to browse the web for information, it also needs the ability to critically evaluate the quality, relevance, and timeliness of that information, and to synthesize it effectively without introducing errors or outdated practices.

**How Current AI (like Gemini) Contributes:**

Models like Gemini and other advanced LLMs are already powerful tools that can assist in many parts of this process:
*   Generating initial drafts of system designs, data models, and API specifications from user requirements.
*   Producing code snippets or boilerplate in various languages.
*   Creating code for diagramming tools (e.g., PlantUML, Mermaid.js).
*   Performing high-level reviews of designs or code against provided best practices.
*   Summarizing technical documentation and explaining complex concepts.
*   Brainstorming alternative solutions.

**This Project as a Foundation:**

The current application, with its (conceptual) multi-stage AI workflow including analysis, review, and redesign, aims to be a foundational step towards more sophisticated AI-assisted system design. It demonstrates the structure and potential of such a system, even if the most advanced AI reasoning components are currently mocked or simplified. Achieving the full vision of a universal AI solution architect is a long-term endeavor requiring ongoing research and development in various AI fields.

## Running the Backend API Server

The Python application can be run as an API server using Flask. This is necessary if you intend to use a separate frontend (like the conceptual React UI described below).

1.  **Ensure Prerequisites and Setup are complete** (Python, dependencies, `GEMINI_API_KEY` environment variable).

2.  **Navigate to the project root directory** (the one containing the `app_designer` package).

3.  **Run the API server:**
    You have a few options:
    *   **Using Flask CLI (Recommended for development):**
        ```bash
        export FLASK_APP=app_designer.api:app
        # Optional: export FLASK_ENV=development (for debug mode)
        # Optional: export FLASK_RUN_PORT=5001
        # Optional: export FLASK_RUN_HOST=0.0.0.0 (to make it accessible on your network)
        flask run
        ```
    *   **Directly running `api.py` (for simple development):**
        ```bash
        python -m app_designer.api
        ```
        This will typically start the server on `http://127.0.0.1:5001`. You can set `FLASK_DEBUG=true`, `FLASK_RUN_HOST`, and `FLASK_RUN_PORT` environment variables to configure it.

4.  The API server will start, and the `POST /api/v1/generate-design` endpoint will be available.

**For Production Deployment:** Use a proper WSGI server like Gunicorn or uWSGI:
```bash
# Example with Gunicorn (install gunicorn first: pip install gunicorn)
gunicorn -w 4 -b 0.0.0.0:5001 app_designer.api:app
```

## Conceptual React UI Frontend

A React-based user interface can be developed to interact with the backend API. This section outlines the conceptual structure and setup for such a frontend. **Note:** The React frontend code is not part of this backend project directly but would be a separate project.

**Purpose:**
To provide a user-friendly web interface for:
-   Inputting user flow text.
-   Submitting the flow to the backend API.
-   Displaying the generated system design report (Markdown).
-   Showing loading states and error messages.

**Setup (Conceptual - for a new React project named `frontend`):**

1.  **Install Node.js and npm/yarn.**
2.  **Create a new React application (e.g., using Vite):**
    ```bash
    npm create vite@latest frontend -- --template react
    cd frontend
    npm install
    ```
3.  **Install necessary libraries:**
    ```bash
    npm install axios react-router-dom react-markdown remark-gfm
    # Optionally, a UI component library like Material-UI:
    # npm install @mui/material @emotion/react @emotion/styled
    # Optionally, a state management library like Zustand:
    # npm install zustand
    ```
4.  **Configure API Base URL:**
    In your React app (e.g., in a `.env` file like `.env.development.local` or `.env.local`), set the base URL for your Python backend API:
    ```
    REACT_APP_API_BASE_URL=http://localhost:5001
    ```
    (Adjust if your Flask server runs on a different port/host). Your API service code in React (e.g., `src/services/designApiService.js`) would then use this environment variable.

5.  **Develop Components:**
    Create components as outlined in the "Conceptual React Application Structure" (e.g., `HomePage.js`, `DesignReportPage.js`). Refer to the conceptual snippets provided earlier in development.

6.  **Run the React Development Server:**
    ```bash
    npm run dev
    ```
    This will typically start the React app on `http://localhost:5173` (for Vite) or `http://localhost:3000` (for Create React App).

**Interaction:**
The React frontend will make HTTP POST requests to the `http://localhost:5001/api/v1/generate-design` endpoint (or your configured API URL) on the Python backend. Ensure CORS is enabled on the Flask backend (as done in `api.py`) to allow requests from the React development server's origin.

## Testing

This project uses Python's built-in `unittest` framework for unit testing. Tests are located in the `tests/` directory.

**Approach:**

-   **Unit Tests:** Each agent and the orchestrator have corresponding test files (e.g., `test_ingestion_agent.py`, `test_orchestrator.py`). These tests focus on verifying the logic of individual components.
-   **Mocking:**
    -   Interactions with the Gemini API (in `SystemDesignGenerationAgent`) are mocked using `unittest.mock` to simulate API responses, including success and error scenarios (like blocked prompts or malformed JSON). This allows testing the agent's handling of API interactions without making actual external calls during tests.
    -   Dependencies between agents (especially in `Orchestrator` tests) are often mocked to isolate the unit under test and control the data flow between components.
-   **Conceptual Agent Testing:** For the advanced AI workflow agents that currently use mocked responses (`DesignAnalysisAgent`, `DesignReviewAgent`, `SimulationAndTestGenerationAgent`, `RedesignAgent`), their standalone `if __name__ == '__main__':` blocks demonstrate their mock logic. Unit tests for these would be similar to `test_generation_agent.py` if/when they are implemented with real AI calls, focusing on mocking the AI interaction. The orchestrator tests ensure these conceptual agents are called in the correct sequence and their mock data is processed.

**How to Run Tests:**

1.  Navigate to the project root directory (the one containing the `app_designer` package and the `tests` directory).
2.  Run the following command in your terminal:

    ```bash
    python -m unittest discover -s tests -v
    ```
    The `-v` flag enables verbose output.

**Current Testing Limitations:**

-   **No End-to-End API Testing:** The current test suite does not include tests that make actual HTTP requests to the Flask API endpoints (e.g., using a test client like `requests` or Flask's `test_client()`). Such tests would be a valuable addition for ensuring API request/response handling, but are outside the current automated execution environment.
-   **No UI Testing:** The conceptual React UI is not implemented or tested.
-   **No Qualitative AI Output Testing:** The tests verify that the application *handles* expected structures from AI (real or mocked), but they do not assess the *quality, accuracy, or relevance* of the actual content generated by a real Gemini API call. Qualitative testing of AI outputs typically requires human evaluation or specialized metrics and datasets.
-   **Limited Integration Testing for Advanced Workflow:** While the orchestrator tests the flow involving mocked advanced agents, true integration testing for these stages would require them to have real (or more sophisticated simulated) logic.
```
