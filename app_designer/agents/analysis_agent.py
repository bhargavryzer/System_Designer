import re

class UserFlowAnalysisAgent:
    """
    Agent responsible for analyzing the user flow text to extract key components.
    """
    def __init__(self):
        pass

    def analyze_flow(self, cleaned_flow_text: str) -> dict:
        """
        Analyzes the cleaned user flow text to extract structured information.
        For this version, it will use simple regex and keyword spotting.

        Returns:
            A dictionary containing extracted elements like 'actors', 'screens', 'actions'.
        """
        if not cleaned_flow_text:
            raise ValueError("Cleaned flow text cannot be empty for analysis.")

        print(f"UserFlowAnalysisAgent: Analyzing text: '{cleaned_flow_text[:100]}...'")

        actors = set()
        actions = set()
        screens_keywords = {'page', 'screen', 'dashboard', 'view', 'form'}
        screens = set()

        # Simple Actor Extraction (words starting with User, System, Admin, etc., followed by a verb)
        # This is very naive and will need improvement.
        actor_patterns = r'\b(User|System|Admin|Customer|Service[s]?)\b'
        found_actors = re.findall(actor_patterns, cleaned_flow_text, re.IGNORECASE)
        for actor in found_actors:
            actors.add(actor.capitalize())

        # Simple Action Extraction (keywords like navigates, enters, clicks, submits, validates, creates, sends, displays, redirects)
        action_keywords = [
            'navigates', 'enters', 'inputs', 'clicks', 'submits', 'selects', 'uploads',
            'validates', 'verifies', 'creates', 'sends', 'displays', 'shows', 'redirects',
            'logs in', 'signs up', 'views', 'searches for', 'updates', 'deletes', 'saves'
        ]
        # A more robust way would be to find verbs associated with actors.
        # For simplicity, let's find sentences or phrases containing these keywords.
        sentences = re.split(r'[.\n]', cleaned_flow_text) # Split by sentences or newlines
        for sentence in sentences:
            for keyword in action_keywords:
                if keyword in sentence.lower():
                    # Attempt to extract a slightly more meaningful action phrase
                    match = re.search(rf'.*?({keyword}[^.]*)\b', sentence, re.IGNORECASE)
                    if match and match.group(1).strip():
                        actions.add(match.group(1).strip().capitalize())

            # Simple Screen Extraction
            for screen_keyword in screens_keywords:
                if screen_keyword in sentence.lower():
                    # Try to find words like "signup page", "dashboard"
                    match = re.search(rf'\b(\w+\s+{screen_keyword}|{screen_keyword})\b', sentence, re.IGNORECASE)
                    if match and match.group(1).strip():
                        screens.add(match.group(1).strip().capitalize())


        # If no specific actors found, but "user" is mentioned, add "User"
        if not actors and "user" in cleaned_flow_text.lower():
            actors.add("User")
        if not actors: # Default actor if none identified
            actors.add("GenericActor")


        analysis_result = {
            "actors": sorted(list(actors)),
            "actions": sorted(list(actions))[:10], # Limit actions for brevity in this example
            "screens_pages": sorted(list(screens)),
            "original_flow": cleaned_flow_text
        }

        print(f"UserFlowAnalysisAgent: Analysis complete. Found {len(actors)} actors, {len(actions)} actions, {len(screens)} screens.")
        return analysis_result

if __name__ == '__main__':
    # Example Usage
    analysis_agent = UserFlowAnalysisAgent()
    sample_cleaned_flow = "User Registration Flow: 1. User navigates to the signup page. 2. User enters email, password, and username. 3. System validates the input. If valid, System creates a new user account. 4. System sends a confirmation email. 5. User is redirected to the login page or dashboard."

    analysis_output = analysis_agent.analyze_flow(sample_cleaned_flow)
    print("\nAnalysis Output:")
    import json
    print(json.dumps(analysis_output, indent=2))

    another_flow = "Customer logs in with username and password. System verifies credentials. Customer views the order history page. Customer clicks on an order to see details."
    analysis_output_2 = analysis_agent.analyze_flow(another_flow)
    print("\nAnalysis Output 2:")
    print(json.dumps(analysis_output_2, indent=2))
