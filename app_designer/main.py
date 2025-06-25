from orchestrator import Orchestrator # Assuming orchestrator.py is in the same directory or Python path

def run_design_generation_app():
    """
    Main function to run the application.
    Defines a sample user flow and uses the Orchestrator to generate a system design.
    """
    print("Application: System Design Generator from User Flow")
    print("==================================================")

    # --- Sample User Flow ---
    # You can replace this with any user flow text.
    sample_user_flow = """
    User Authentication and Profile Management Flow:

    Part 1: User Registration
    1. New user navigates to the 'Sign Up' page.
    2. User provides their email address, a chosen password (with confirmation), and a username.
    3. User clicks the 'Register' button.
    4. The System attempts to validate the provided data (e.g., email format, password strength, username availability).
    5. If validation fails, the System displays specific error messages next to the relevant fields on the signup page.
    6. If validation succeeds, the System creates a new user record in the database with a 'pending confirmation' status.
    7. The System generates a unique email confirmation token and sends an email with a confirmation link to the user's provided email address.
    8. The user is shown a message on screen: "Registration successful. Please check your email to confirm your account."

    Part 2: Email Confirmation
    1. User receives the confirmation email and clicks the confirmation link.
    2. The System validates the confirmation token (e.g., checks if it exists, hasn't expired).
    3. If the token is valid, the System updates the user's account status to 'active'.
    4. The System redirects the user to a 'Login' page with a message: "Email confirmed. You can now log in."
    5. If the token is invalid or expired, the System shows an error page with an option to resend the confirmation email.

    Part 3: User Login
    1. Returning user navigates to the 'Login' page.
    2. User enters their registered email and password.
    3. User clicks the 'Login' button.
    4. The System verifies the credentials against the database.
    5. If credentials are valid and the account is active, the System creates a session for the user and redirects them to their personalized 'Dashboard' page.
    6. If credentials are invalid or the account is not active, the System displays an error message on the login page.

    Part 4: Basic Profile Viewing (Post-Login)
    1. Logged-in user navigates to their 'Profile' page from the dashboard.
    2. The System retrieves and displays the user's current username and email address.
    """

    print("\n--- Input User Flow ---")
    print(sample_user_flow)
    print("-----------------------\n")

    # Initialize the orchestrator
    # In a real application, you might get the GEMINI_API_KEY from environment variables or a config file
    orchestrator = Orchestrator(gemini_api_key="DUMMY_API_KEY_FROM_MAIN_APP")
                                                        # Still using dummy for this example

    # Generate the system design
    print("Application: Requesting system design generation...\n")
    formatted_system_design = orchestrator.generate_system_design(sample_user_flow)

    # Print the final output
    print("\n\n==============================================")
    print("    최종 생성된 시스템 설계 (Final Generated System Design)   ")
    print("==============================================")
    print(formatted_system_design)
    print("==============================================")
    print("Application: Process finished.")

if __name__ == "__main__":
    run_design_generation_app()
